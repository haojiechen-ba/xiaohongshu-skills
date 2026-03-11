---
name: xiaohongshu-skills
description: |
  小红书自动化技能集合。包含 6 个子技能：内容创作(xhs-content-creation)、认证管理(xhs-auth)、内容发布(xhs-publish)、内容发现(xhs-explore)、社交互动(xhs-interact)、复合运营(xhs-content-ops)。
  当用户要求操作小红书（创作笔记、生成图片、发布、搜索、评论、登录、分析、点赞、收藏）时触发。
---

# 小红书自动化 Skills

根据用户意图路由到对应的子技能完成任务。

## 意图路由

按优先级路由：

1. **内容创作** → 参考`./skills/xhs-content-creation/SKILL.md`
   - 触发词：写笔记、创作内容、生成图片卡片、制作卡片
2. **认证登录** → 参考`./skills/xhs-auth/SKILL.md`
   - 触发词：登录、登录小红书、检查登录、切换账号
3. **发布内容** → 参考`./skills/xhs-publish/SKILL.md`
   - 触发词：发布、发帖子、上传图文、上传视频
4. **搜索发现** → 参考`./skills/xhs-explore/SKILL.md`
   - 触发词：搜索笔记、查看详情、浏览首页、看用户主页
5. **社交互动** → 参考`./skills/xhs-interact/SKILL.md`
   - 触发词：评论、回复、点赞、收藏
6. **复合运营** → 参考`./skills/xhs-content-ops/SKILL.md`
   - 触发词：竞品分析、热点追踪、批量互动

## 全局约束

- 执行操作前先检查登录状态（运行 `python scripts/cli.py check-login`）
- 文件路径使用绝对路径
- CLI 输出为 JSON 格式

## 快速开始

```bash
# 启动 Chrome
python scripts/chrome_launcher.py

# 检查登录状态
python scripts/cli.py check-login

# 登录（如需要）
python scripts/cli.py login
```

## 子技能

| 技能 | 说明 |
|------|------|
| xhs-content-creation | 笔记撰写、Markdown 格式、图片卡片渲染（8 套主题） |
| xhs-auth | 登录检查、二维码登录、手机验证码、多账号切换 |
| xhs-publish | 图文/视频发布、长文发布、定时发布、分步预览 |
| xhs-explore | 关键词搜索、笔记详情、用户主页、首页推荐 |
| xhs-interact | 评论、回复、点赞、收藏 |
| xhs-content-ops | 竞品分析、热点追踪、批量互动 |

## 详细参考

- **CLI 命令**：加载 `references/cli-commands.md` 获取完整命令列表
- **CSS 选择器**：加载 `references/selectors.md` 获取页面元素选择器

## 失败处理

- **未登录**：提示用户执行登录流程
- **Chrome 未启动**：运行 `python scripts/chrome_launcher.py`
- **操作超时**：检查网络，增加等待时间
