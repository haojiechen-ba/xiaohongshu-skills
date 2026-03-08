# 小红书 CSS 选择器参考

本文档记录了小红书网页版的关键 CSS 选择器，用于自动化操作。选择器可能随小红书前端更新而变化。

## 登录页面

| 元素 | 选择器 |
|------|--------|
| 二维码图片 | `.qrcode-img` |
| 验证码输入框 | `input[name="phone"]` |
| 验证码按钮 | `button:contains("获取验证码")` |
| 登录按钮 | `button:contains("登录")` |

## 首页 Feed

| 元素 | 选择器 |
|------|--------|
| Feed 列表容器 | `.feed-list` |
| 单条笔记卡片 | `.note-item` |
| 笔记标题 | `.note-title` |
| 笔记作者 | `.author-name` |
| 点赞数 | `.like-count` |
| 评论数 | `.comment-count` |
| 收藏数 | `.collect-count` |

## 搜索结果

| 元素 | 选择器 |
|------|--------|
| 搜索输入框 | `input[name="keyword"]` |
| 搜索按钮 | `button:contains("搜索")` |
| 筛选按钮 | `.filter-btn` |
| 排序选项 | `.sort-options` |
| 笔记类型筛选 | `.note-type-filter` |

## 笔记详情页

| 元素 | 选择器 |
|------|--------|
| 笔记标题 | `.note-detail-title` |
| 笔记正文 | `.note-content` |
| 作者信息 | `.author-info` |
| 点赞按钮 | `.like-btn` |
| 收藏按钮 | `.collect-btn` |
| 评论列表 | `.comment-list` |
| 评论输入框 | `textarea.comment-input` |
| 发布评论按钮 | `button:contains("发布")` |

## 发布页面

| 元素 | 选择器 |
|------|--------|
| 标题输入框 | `input[name="title"]` |
| 正文输入框 | `div[contenteditable="true"]` |
| 图片上传按钮 | `.upload-btn` |
| 视频上传按钮 | `.video-upload-btn` |
| 标签输入框 | `input[name="tags"]` |
| 发布按钮 | `button:contains("发布")` |
| 预览按钮 | `button:contains("预览")` |
| 保存草稿按钮 | `button:contains("存草稿")` |

## 用户主页

| 元素 | 选择器 |
|------|--------|
| 用户昵称 | `.user-nickname` |
| 小红书号 | `.xhs-id` |
| 粉丝数 | `.fans-count` |
| 关注数 | `.following-count` |
| 获赞与收藏 | `.like-collect-count` |
| 笔记列表 | `.user-notes` |
| 笔记 tab | `.tab:contains("笔记")` |
| 收藏 tab | `.tab:contains("收藏")` |

## 长文发布

| 元素 | 选择器 |
|------|--------|
| 长文入口 | `a:contains("写长文")` |
| 新建创作 | `button:contains("新的创作")` |
| 标题输入框 | `input.note-title-input` |
| 正文编辑器 | `.editor-content` |
| 一键排版按钮 | `button:contains("一键排版")` |
| 模板列表 | `.template-list` |
| 下一步按钮 | `button:contains("下一步")` |

## 注意事项

1. **选择器可能变化**：小红书前端更新频繁，选择器可能失效
2. **优先使用 ID 和 data-***：尽量使用稳定的 ID 或 data-* 属性
3. **备用选择器**：为关键元素准备备用选择器
4. **测试验证**：每次小红书更新后需要验证选择器

## 更新日志

- 2024-01: 初始版本
- 2024-03: 更新登录和发布选择器
- 2024-06: 添加长文相关选择器
