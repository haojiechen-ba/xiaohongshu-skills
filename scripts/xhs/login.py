"""登录管理，对应 Go xiaohongshu/login.go。"""

from __future__ import annotations

import base64
import logging
import os
import struct
import tempfile
import time
import zlib

_QR_DIR = os.path.join(tempfile.gettempdir(), "xhs")
_QR_FILE = os.path.join(_QR_DIR, "login_qrcode.png")
_QR_BORDER = 16  # 白边宽度（像素）

_PNG_SIG = b"\x89PNG\r\n\x1a\n"


def _add_png_border(data: bytes, padding: int = _QR_BORDER) -> bytes:
    """给 PNG 图片添加白色边框（纯 Python stdlib，不依赖 Pillow）。

    支持 8-bit 深度的 Grayscale / RGB / Grayscale+Alpha / RGBA 四种色彩类型。
    Indexed-color（color_type=3）暂不处理，原样返回。

    Args:
        data: 原始 PNG 字节。
        padding: 边框宽度（像素）。

    Returns:
        带白色边框的 PNG 字节。
    """
    if not data.startswith(_PNG_SIG):
        return data

    # ── 解析 chunks ──────────────────────────────────────────────
    def _read_chunks(buf: bytes) -> list[tuple[bytes, bytes]]:
        result, pos = [], 8
        while pos < len(buf):
            (length,) = struct.unpack_from(">I", buf, pos)
            ctype = buf[pos + 4 : pos + 8]
            cdata = buf[pos + 8 : pos + 8 + length]
            result.append((ctype, cdata))
            pos += 12 + length
        return result

    def _make_chunk(ctype: bytes, cdata: bytes) -> bytes:
        crc = zlib.crc32(ctype + cdata) & 0xFFFFFFFF
        return struct.pack(">I", len(cdata)) + ctype + cdata + struct.pack(">I", crc)

    chunks = _read_chunks(data)

    # ── IHDR ─────────────────────────────────────────────────────
    ihdr = next(d for t, d in chunks if t == b"IHDR")
    w, h = struct.unpack_from(">II", ihdr)
    bit_depth, color_type = ihdr[8], ihdr[9]

    if bit_depth != 8 or color_type == 3:
        return data  # 不支持的格式，原样返回

    bpp = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
    white = bytes([255] * bpp)

    # ── 解压 IDAT ────────────────────────────────────────────────
    raw = zlib.decompress(b"".join(d for t, d in chunks if t == b"IDAT"))

    # ── 逐行解码 PNG filter，还原像素数据 ────────────────────────
    stride = w * bpp

    def _paeth(a: int, b: int, c: int) -> int:
        p = a + b - c
        pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
        if pa <= pb and pa <= pc:
            return a
        return b if pb <= pc else c

    pixel_rows: list[bytes] = []
    prior = bytearray(stride)
    pos = 0
    for _ in range(h):
        f = raw[pos]
        row = bytearray(raw[pos + 1 : pos + 1 + stride])
        pos += 1 + stride
        if f == 1:  # Sub
            for i in range(bpp, stride):
                row[i] = (row[i] + row[i - bpp]) & 0xFF
        elif f == 2:  # Up
            for i in range(stride):
                row[i] = (row[i] + prior[i]) & 0xFF
        elif f == 3:  # Average
            for i in range(stride):
                a = row[i - bpp] if i >= bpp else 0
                row[i] = (row[i] + (a + prior[i]) // 2) & 0xFF
        elif f == 4:  # Paeth
            for i in range(stride):
                a = row[i - bpp] if i >= bpp else 0
                b = prior[i]
                c = prior[i - bpp] if i >= bpp else 0
                row[i] = (row[i] + _paeth(a, b, c)) & 0xFF
        pixel_rows.append(bytes(row))
        prior = row

    # ── 构建带边框的新图像（filter 0 = None，最简单）────────────
    new_w, new_h = w + padding * 2, h + padding * 2
    white_row = b"\x00" + white * new_w
    pad_cols = white * padding

    new_raw = bytearray()
    for _ in range(padding):
        new_raw += white_row
    for row in pixel_rows:
        new_raw += b"\x00" + pad_cols + row + pad_cols
    for _ in range(padding):
        new_raw += white_row

    new_idat = zlib.compress(bytes(new_raw), 6)
    new_ihdr = struct.pack(">II", new_w, new_h) + ihdr[8:]

    # ── 重建 PNG ─────────────────────────────────────────────────
    out = bytearray(_PNG_SIG)
    out += _make_chunk(b"IHDR", new_ihdr)
    for ctype, cdata in chunks:
        if ctype not in (b"IHDR", b"IDAT", b"IEND"):
            out += _make_chunk(ctype, cdata)
    out += _make_chunk(b"IDAT", new_idat)
    out += _make_chunk(b"IEND", b"")
    return bytes(out)

from .cdp import Page
from .errors import RateLimitError
from .human import sleep_random
from .selectors import (
    AGREE_CHECKBOX,
    AGREE_CHECKBOX_CHECKED,
    CAPTCHA_MODAL,
    CAPTCHA_QRCODE,
    CODE_INPUT,
    GET_CODE_BUTTON,
    LOGIN_CONTAINER,
    LOGIN_ERR_MSG,
    LOGIN_STATUS,
    LOGOUT_MENU_ITEM,
    LOGOUT_MORE_BUTTON,
    PHONE_INPUT,
    PHONE_LOGIN_SUBMIT,
    QRCODE_IMG,
)
from .urls import EXPLORE_URL

logger = logging.getLogger(__name__)


def check_login_status(page: Page) -> bool:
    """检查登录状态。

    Returns:
        True 已登录，False 未登录。
    """
    page.navigate(EXPLORE_URL)
    page.wait_for_load()
    sleep_random(800, 1500)

    return page.has_element(LOGIN_STATUS)


def fetch_qrcode(page: Page) -> tuple[str, bool]:
    """获取登录二维码。

    Returns:
        (qrcode_src, already_logged_in)
        - 如果已登录，返回 ("", True)
        - 如果未登录，返回 (qrcode_base64_or_url, False)
    """
    page.navigate(EXPLORE_URL)
    page.wait_for_load()
    sleep_random(1500, 2500)

    # 检查是否已登录
    if page.has_element(LOGIN_STATUS):
        return "", True

    # 获取二维码图片 src
    src = page.get_element_attribute(QRCODE_IMG, "src")
    if not src:
        raise RuntimeError("二维码图片 src 为空")

    return src, False


def save_qrcode_to_file(src: str) -> tuple[str, str]:
    """将二维码图片保存为临时 PNG 文件，同时返回 data URL。

    相当于浏览器"右键 → 另存为图片"：从 img.src 取得图片字节后落盘。

    Args:
        src: 二维码 img 元素的 src——data URL（data:image/...;base64,...）或网络 URL。

    Returns:
        (file_path, data_url)
        - file_path: 保存的 PNG 文件绝对路径
        - data_url:  data:image/png;base64,... 格式，可直接嵌入 Markdown
    """
    if src.startswith("data:image/"):
        # data URL：直接解码
        _, encoded = src.split(",", 1)
        img_data = base64.b64decode(encoded)
    elif src.startswith("http://") or src.startswith("https://"):
        # 网络 URL：下载（等同浏览器右键另存为）
        import requests as _req
        resp = _req.get(src, timeout=10)
        resp.raise_for_status()
        img_data = resp.content
    else:
        raise ValueError(f"不支持的二维码格式: {src[:80]}")

    img_data = _add_png_border(img_data)

    os.makedirs(_QR_DIR, exist_ok=True)
    with open(_QR_FILE, "wb") as f:
        f.write(img_data)

    data_url = "data:image/png;base64," + base64.b64encode(img_data).decode()
    logger.info("二维码已保存: %s", _QR_FILE)
    return _QR_FILE, data_url


def send_phone_code(page: Page, phone: str) -> bool:
    """填写手机号并发送短信验证码。

    适用于无界面服务器场景，全程通过 CDP 操作，无需扫码。

    Args:
        page: CDP 页面对象。
        phone: 手机号（不含国家码，如 13800138000）。

    Returns:
        True 验证码已发送，False 已登录（无需再登录）。

    Raises:
        RuntimeError: 找不到登录表单或手机号输入框。
    """
    page.navigate(EXPLORE_URL)
    page.wait_for_load()
    sleep_random(1500, 2500)

    if page.has_element(LOGIN_STATUS):
        return False

    # 等待登录弹窗出现
    page.wait_for_element(LOGIN_CONTAINER, timeout=15.0)
    sleep_random(500, 800)

    # 点击手机号输入框并逐字输入
    page.click_element(PHONE_INPUT)
    sleep_random(200, 400)
    page.type_text(phone, delay_ms=80)
    sleep_random(500, 800)

    # 先勾选用户协议，再点获取验证码
    if not page.has_element(AGREE_CHECKBOX_CHECKED):
        page.click_element(AGREE_CHECKBOX)
        sleep_random(300, 600)

    # 点击"获取验证码"
    page.click_element(GET_CODE_BUTTON)
    sleep_random(2000, 2500)

    # 检测按钮是否变为倒计时（成功发送后按钮文字会包含数字秒数）
    btn_text = page.get_element_text(GET_CODE_BUTTON) or ""
    if not any(ch.isdigit() for ch in btn_text):
        raise RateLimitError()

    logger.info("验证码已发送至 %s", phone[:3] + "****" + phone[-4:])
    return True


def submit_phone_code(page: Page, code: str) -> dict[str, object]:
    """填写短信验证码并提交登录。

    提交后可能出现两种情况：
    1. 直接登录成功
    2. 弹出二次确认弹窗（新设备登录），需要再扫码

    Args:
        page: CDP 页面对象。
        code: 收到的短信验证码。

    Returns:
        dict:
        - {"logged_in": True} — 登录成功
        - {"logged_in": False, "error": "..."} — 验证码错误
        - {"logged_in": False, "captcha_required": True, ...} — 需要二次确认扫码
    """
    # 点击验证码输入框并逐字输入
    page.click_element(CODE_INPUT)
    sleep_random(300, 500)
    page.type_text(code, delay_ms=100)
    sleep_random(500, 800)

    # 点击登录按钮
    page.click_element(PHONE_LOGIN_SUBMIT)
    sleep_random(1000, 2000)

    # 检查是否有错误提示
    err = page.get_element_text(LOGIN_ERR_MSG)
    if err and err.strip():
        logger.warning("登录失败: %s", err.strip())
        return {"logged_in": False, "error": err.strip()}

    return wait_for_login(page, timeout=30.0)


def logout(page: Page) -> bool:
    """通过页面 UI 退出登录（点击"更多"→"退出登录"）。

    Args:
        page: CDP 页面对象。

    Returns:
        True 退出成功，False 未登录或操作失败。
    """
    page.navigate(EXPLORE_URL)
    page.wait_for_load()
    sleep_random(800, 1500)

    if not page.has_element(LOGIN_STATUS):
        logger.info("当前未登录，无需退出")
        return False

    # 点击"更多"按钮展开菜单
    page.click_element(LOGOUT_MORE_BUTTON)
    sleep_random(500, 800)

    # 等待退出菜单项出现并点击
    page.wait_for_element(LOGOUT_MENU_ITEM, timeout=5.0)
    page.click_element(LOGOUT_MENU_ITEM)
    sleep_random(1000, 1500)

    logger.info("已退出登录")
    return True


def wait_for_login(page: Page, timeout: float = 120.0) -> dict[str, object]:
    """等待扫码登录完成。

    处理小红书扫码登录流程：
    1. 显示第一个二维码（或提交验证码）
    2. 用户扫码 → 可能弹出二次确认弹窗（新设备）
    3. 如果有二次确认，自动提取二维码并返回
    4. 调用方展示二维码，用户扫码后登录成功

    Args:
        page: CDP 页面对象。
        timeout: 超时时间（秒）。

    Returns:
        dict:
        - {"logged_in": True} — 登录成功
        - {"logged_in": False, "captcha_required": True, "captcha_qrcode_path": "...",
           "captcha_data_url": "data:...", "message": "..."} — 需要二次确认扫码
        - {"logged_in": False, "timeout": True} — 超时
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        # 检查是否已登录
        if page.has_element(LOGIN_STATUS):
            logger.info("登录成功")
            return {"logged_in": True}

        # 检测二次确认弹窗（新设备登录）
        if page.has_element(CAPTCHA_MODAL):
            logger.info("检测到二次确认弹窗（新设备登录）")
            result = _extract_captcha_qrcode(page)
            if result:
                return result
            # 提取失败但弹窗存在，继续轮询等登录成功

        time.sleep(0.5)

    return {"logged_in": False, "timeout": True}


def fetch_captcha_qrcode(page: Page) -> dict[str, object]:
    """检测并获取二次确认弹窗中的二维码（非阻塞）。

    用于 get-qrcode 非阻塞流程：用户扫完第一个二维码后轮询 check-login，
    若检测到二次确认弹窗，调用此函数提取弹窗内的二维码。

    Args:
        page: CDP 页面对象。

    Returns:
        dict:
        - {"captcha_required": False} — 无二次确认弹窗
        - {"captcha_required": True, "captcha_qrcode_path": "...",
           "captcha_data_url": "data:...", "message": "..."} — 弹窗存在，已提取二维码
    """
    if not page.has_element(CAPTCHA_MODAL):
        return {"captcha_required": False}

    logger.info("检测到二次确认弹窗（新设备登录）")
    result = _extract_captcha_qrcode(page)
    if result:
        return result
    return {"captcha_required": True, "error": "检测到二次确认弹窗但无法提取二维码"}


def _extract_captcha_qrcode(page: Page) -> dict[str, object] | None:
    """从二次确认弹窗中提取二维码图片并保存。

    Args:
        page: CDP 页面对象。

    Returns:
        包含二维码信息的 dict，提取失败返回 None。
    """
    captcha_src = page.get_element_attribute(CAPTCHA_QRCODE, "src")
    if not captcha_src:
        logger.warning("二次确认弹窗中未找到二维码图片")
        return None

    try:
        captcha_path, captcha_data_url = save_qrcode_to_file(captcha_src)
        # 重命名为二次确认二维码
        final_path = os.path.join(_QR_DIR, "captcha_qrcode.png")
        if os.path.exists(final_path):
            os.remove(final_path)
        os.rename(captcha_path, final_path)
        logger.info("二次确认二维码已保存: %s", final_path)
        return {
            "logged_in": False,
            "captcha_required": True,
            "captcha_qrcode_path": final_path,
            "captcha_data_url": captcha_data_url,
            "message": "新设备登录需要二次确认，请用小红书 App 扫描此二维码",
        }
    except Exception as e:
        logger.warning("保存二次确认二维码失败: %s", e)
        return None
