# CLI 命令详细参考

本文档提供 `scripts/cli.py` 所有命令的详细参数说明。

## 全局参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--host HOST` | Chrome 调试主机 | 127.0.0.1 |
| `--port PORT` | Chrome 调试端口 | 9222 |
| `--account NAME` | 指定账号名称 | default |

## 子命令

### check-login

检查当前登录状态。

```bash
python scripts/cli.py check-login
```

**输出：**
```json
{
  "logged_in": true,
  "user_id": "xxx",
  "nickname": "用户名",
  "xhs_id": "xxxxx"
}
```

**未登录时：**
```json
{
  "logged_in": false,
  "login_method": "qrcode" | "both"
}
```

---

### login

二维码登录（阻塞等待）。

```bash
python scripts/cli.py login
```

**参数：**
- 无

**输出：**
```json
{
  "logged_in": true,
  "nickname": "用户名",
  "xhs_id": "xxxxx"
}
```

---

### get-qrcode

获取二维码（非阻塞）。

```bash
python scripts/cli.py get-qrcode
```

**输出：**
```json
{
  "qrcode_path": "/path/to/qrcode.png",
  "qrcode_data_url": "data:image/png;base64,..."
}
```

---

### send-code

发送手机验证码。

```bash
python scripts/cli.py send-code --phone 13800138000
```

**参数：**
- `--phone` (必填): 手机号（不含国家码）

**输出：**
```json
{
  "status": "code_sent",
  "message": "验证码已发送至 138****0000"
}
```

---

### verify-code

提交验证码完成登录。

```bash
python scripts/cli.py verify-code --code 123456
```

**参数：**
- `--code` (必填): 6 位验证码

**输出：**
```json
{
  "logged_in": true,
  "message": "登录成功"
}
```

---

### phone-login

手机号+验证码登录（交互式，适合本地终端）。

```bash
# 方式一：交互式输入验证码
python scripts/cli.py phone-login --phone 13800138000

# 方式二：直接传入验证码
python scripts/cli.py phone-login --phone 13800138000 --code 123456
```

**参数：**
- `--phone` (必填): 手机号（不含国家码）
- `--code`: 短信验证码（省略则交互式输入）

**输出：**
```json
{
  "logged_in": true,
  "message": "登录成功"
}
```

---

### delete-cookies

清除 cookies（退出/切换账号）。

```bash
python scripts/cli.py delete-cookies
python scripts/cli.py --account work delete-cookies
```

**参数：**
- 无（使用 `--account` 指定账号）

**输出：**
```json
{
  "success": true,
  "message": "Cookies 已清除"
}
```

---

### list-feeds

获取首页推荐 Feed。

```bash
python scripts/cli.py list-feeds
python scripts/cli.py list-feeds --limit 20
```

**参数：**
- `--limit`: 返回数量限制

**输出：**
```json
{
  "feeds": [
    {
      "feed_id": "xxx",
      "title": "笔记标题",
      "author": "作者名",
      "likes": 100,
      "comments": 20,
      "covers": ["url1", "url2"]
    }
  ]
}
```

---

### search-feeds

关键词搜索笔记。

```bash
python scripts/cli.py search-feeds --keyword "关键词"
python scripts/cli.py search-feeds --keyword "露营" --sort-by "最多点赞" --note-type "图文"
```

**参数：**
- `--keyword` (必填): 搜索关键词
- `--sort-by`: 排序方式（综合/最新/最多点赞/最多评论/最多收藏）
- `--note-type`: 笔记类型（不限/视频/图文）
- `--publish-time`: 时间范围（不限/一天内/一周内/半年内）
- `--search-scope`: 搜索范围（不限/已看过/未看过/已关注）
- `--location`: 位置（不限/同城/附近）

**输出：**
```json
{
  "feeds": [...],
  "total": 100,
  "page": 1
}
```

---

### get-feed-detail

获取笔记详情。

```bash
python scripts/cli.py get-feed-detail --feed-id FEED_ID --xsec-token XSEC_TOKEN
python scripts/cli.py get-feed-detail --feed-id FEED_ID --xsec-token XSEC_TOKEN --load-all-comments
```

**参数：**
- `--feed-id` (必填): 笔记 ID
- `--xsec-token` (必填): xsec_token 参数
- `--load-all-comments`: 加载全部评论
- `--click-more-replies`: 点击展开更多回复
- `--max-replies-threshold`: 展开回复数阈值（默认 10）
- `--max-comment-items`: 最大评论数（0=不限，默认 0）
- `--scroll-speed`: 滚动速度（slow/normal/fast，默认 normal）

**输出：**
```json
{
  "feed_id": "xxx",
  "title": "标题",
  "content": "正文内容",
  "author": {
    "user_id": "xxx",
    "nickname": "作者",
    "xhs_id": "xxxx"
  },
  "images": ["url1", "url2"],
  "likes": 100,
  "comments": 20,
  "collects": 10,
  "comments_list": [...]
}
```

---

### user-profile

获取用户主页信息。

```bash
python scripts/cli.py user-profile --user-id USER_ID --xsec-token XSEC_TOKEN
```

**参数：**
- `--user-id` (必填): 用户 ID
- `--xsec-token` (必填): xsec_token

**输出：**
```json
{
  "user_id": "xxx",
  "nickname": "昵称",
  "xhs_id": "xxxxx",
  "avatar": "url",
  "gender": "unknown" | "male" | "female",
  "desc": "个人简介",
  "follows": 100,
  "fans": 1000,
  "likes": 5000,
  "notes": [...]
}
```

---

### post-comment

发表评论。

```bash
python scripts/cli.py post-comment --feed-id FEED_ID --xsec-token XSEC_TOKEN --content "评论内容"
```

**参数：**
- `--feed-id` (必填): 笔记 ID
- `--xsec-token` (必填): xsec_token
- `--content` (必填): 评论内容

**输出：**
```json
{
  "success": true,
  "comment_id": "xxx",
  "message": "评论成功"
}
```

---

### reply-comment

回复评论。

```bash
python scripts/cli.py reply-comment --feed-id FEED_ID --xsec-token XSEC_TOKEN --comment-id COMMENT_ID --content "回复内容"
python scripts/cli.py reply-comment --feed-id FEED_ID --xsec-token XSEC_TOKEN --user-id USER_ID --content "回复内容"
```

**参数：**
- `--feed-id` (必填): 笔记 ID
- `--xsec-token` (必填): xsec_token
- `--content` (必填): 回复内容
- `--comment-id`: 被回复的评论 ID
- `--user-id`: 目标用户 ID（二选一，配合 `--comment-id` 或单独使用）

**输出：**
```json
{
  "success": true,
  "reply_id": "xxx",
  "message": "回复成功"
}
```

---

### like-feed

点赞/取消点赞。

```bash
python scripts/cli.py like-feed --feed-id FEED_ID --xsec-token XSEC_TOKEN
python scripts/cli.py like-feed --feed-id FEED_ID --xsec-token XSEC_TOKEN --unlike
```

**参数：**
- `--feed-id` (必填): 笔记 ID
- `--xsec-token` (必填): xsec_token
- `--unlike`: 取消点赞

**输出：**
```json
{
  "success": true,
  "action": "liked" | "unliked"
}
```

---

### favorite-feed

收藏/取消收藏。

```bash
python scripts/cli.py favorite-feed --feed-id FEED_ID --xsec-token XSEC_TOKEN
python scripts/cli.py favorite-feed --feed-id FEED_ID --xsec-token XSEC_TOKEN --unfavorite
```

**参数：**
- `--feed-id` (必填): 笔记 ID
- `--xsec-token` (必填): xsec_token
- `--unfavorite`: 取消收藏

**输出：**
```json
{
  "success": true,
  "action": "favorited" | "unfavorited"
}
```

---

### publish

一步发布图文。

```bash
python scripts/cli.py publish \
  --title-file /path/to/title.txt \
  --content-file /path/to/content.txt \
  --images "/path/pic1.jpg" "/path/pic2.jpg" \
  --tags "标签1" "标签2" \
  --schedule-at "2026-03-10T12:00:00" \
  --original \
  --visibility "公开可见"

# 无头模式（未登录自动降级到有窗口）
python scripts/cli.py publish --headless \
  --title-file /path/to/title.txt \
  --content-file /path/to/content.txt \
  --images "/path/pic1.jpg"
```

**参数：**
- `--title-file` (必填): 标题文件路径
- `--content-file` (必填): 正文文件路径
- `--images` (必填): 图片路径列表
- `--tags`: 话题标签列表
- `--schedule-at`: 定时发布时间 (ISO8601)
- `--original`: 声明原创
- `--visibility`: 可见范围
- `--headless`: 无头模式（未登录自动降级到有窗口模式）

**输出：**
```json
{
  "success": true,
  "note_id": "xxx",
  "title": "标题",
  "images": ["url1", "url2"],
  "status": "published"
}
```

---

### fill-publish

分步发布 - 填写表单（不发布）。

```bash
python scripts/cli.py fill-publish \
  --title-file /path/to/title.txt \
  --content-file /path/to/content.txt \
  --images "/path/pic1.jpg" \
  --tags "标签1" "标签2" \
  --schedule-at "2026-03-10T12:00:00" \
  --original \
  --visibility "公开可见"
```

**参数：**
- `--title-file` (必填): 标题文件路径
- `--content-file` (必填): 正文文件路径
- `--images` (必填): 图片路径列表
- `--tags`: 话题标签列表
- `--schedule-at`: 定时发布时间
- `--original`: 声明原创
- `--visibility`: 可见范围

---

### fill-publish-video

分步发布视频 - 填写表单（不发布）。

```bash
python scripts/cli.py fill-publish-video \
  --title-file /path/to/title.txt \
  --content-file /path/to/content.txt \
  --video "/path/video.mp4" \
  --tags "标签1" "标签2"
```

**参数：**
- `--title-file` (必填): 标题文件路径
- `--content-file` (必填): 正文文件路径
- `--video` (必填): 视频文件路径
- `--tags`: 话题标签列表
- `--schedule-at`: 定时发布时间
- `--visibility`: 可见范围

---

### click-publish

分步发布 - 点击发布按钮。

```bash
python scripts/cli.py click-publish
```

---

### save-draft

保存为草稿。

```bash
python scripts/cli.py save-draft
```

---

### publish-video

一步发布视频。

```bash
python scripts/cli.py publish-video \
  --title-file /path/to/title.txt \
  --content-file /path/to/content.txt \
  --video "/path/video.mp4" \
  --tags "标签1" "标签2" \
  --schedule-at "2026-03-10T12:00:00" \
  --visibility "公开可见"

# 无头模式（未登录自动降级到有窗口）
python scripts/cli.py publish-video --headless \
  --title-file /path/to/title.txt \
  --content-file /path/to/content.txt \
  --video "/path/video.mp4"
```

**参数：**
- `--title-file` (必填): 标题文件路径
- `--content-file` (必填): 正文文件路径
- `--video` (必填): 视频文件路径
- `--tags`: 话题标签列表
- `--schedule-at`: 定时发布时间 (ISO8601)
- `--visibility`: 可见范围
- `--headless`: 无头模式（未登录自动降级到有窗口模式）

---

### long-article

长文发布。

```bash
python scripts/cli.py long-article \
  --title-file /path/to/title.txt \
  --content-file /path/to/content.txt
```

---

### select-template

选择长文排版模板。

```bash
python scripts/cli.py select-template --name "模板名称"
```

---

### next-step

长文下一步。

```bash
python scripts/cli.py next-step --content-file /path/to/description.txt
```

---

## 退出码

| 退出码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1 | 未登录 |
| 2 | 错误（查看 JSON 中的 error 字段） |
