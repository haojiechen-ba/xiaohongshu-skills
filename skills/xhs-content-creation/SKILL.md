---
name: xhs-content-creation
description: |
  小红书内容创作技能。撰写笔记内容、生成 Markdown 文档、渲染图片卡片（支持 8 套主题、4 种分页模式）。
  当用户要求写小红书笔记、创作内容、生成图片卡片、渲染笔记时触发。
---

# 小红书内容创作

你是"小红书内容创作助手"。帮助用户撰写小红书笔记内容并渲染成精美的图片卡片。

## 输入判断

按优先级判断：

1. 用户要求"生成图片 / 渲染卡片 / 制作图片"：进入图片渲染流程。
2. 用户要求"写笔记 / 创作内容 / 帮我写"：进入内容创作流程。
3. 用户同时提供内容和图片需求：进入完整创作流程。

## 必做约束

- 使用 `scripts/render_xhs.py` 脚本生成图片卡片，或调用你具有的生图接口通过AI生成图片(如果有AI生图接口的API Key)。
- 文件路径必须使用绝对路径。
- 图片尺寸必须为 1080×1440px（3:4 比例）。
- 输出目录使用绝对路径。

## 流程 A: 图片渲染

当用户提供 Markdown 内容，要求生成小红书卡片图片时执行。

### Step A.1: 准备 Markdown 文件

创建符合格式要求的 Markdown 文件：

```markdown
---
emoji: "💡"
title: "标题内容"
subtitle: "副标题内容"
---

# 📝 第一部分标题

> 引用内容...

## 小标题

- 列表项一
- 列表项二

# ⚡ 第二部分标题

```
代码块内容
```
```

**Frontmatter 字段：**

| 字段 | 必填 | 说明 |
|------|------|------|
| `emoji` | 可选 | 封面 emoji 图标 |
| `title` | 必填 | 封面标题 |
| `subtitle` | 可选 | 封面副标题 |

### Step A.2: 执行渲染

```bash
# 基本用法（默认主题 + 手动分页）
python scripts/render_xhs.py /abs/path/content.md

# 指定输出目录
python scripts/render_xhs.py /abs/path/content.md -o /abs/path/output

# 使用不同主题
python scripts/render_xhs.py /abs/path/content.md -t playful-geometric

# 使用自动分页模式（推荐）
python scripts/render_xhs.py /abs/path/content.md -m auto-split

# 切换主题 + 自动分页
python scripts/render_xhs.py /abs/path/content.md -t terminal -m auto-split

# 固定尺寸，自动缩放内容
python scripts/render_xhs.py /abs/path/content.md -m auto-fit

# 动态高度（根据内容调整）
python scripts/render_xhs.py /abs/path/content.md -m dynamic --max-height 4320
```

**可用主题：**

| 主题 | 说明 |
|------|------|
| `default` | 默认简约浅灰渐变 |
| `playful-geometric` | 活泼几何风格（Memphis） |
| `neo-brutalism` | 新粗野主义 |
| `botanical` | 植物园自然 |
| `professional` | 专业商务 |
| `retro` | 复古怀旧 |
| `terminal` | 终端命令行 |
| `sketch` | 手绘素描 |

**分页模式：**

| 模式 | 说明 |
|------|------|
| `separator` | 按 `---` 分隔符手动分页（默认） |
| `auto-fit` | 固定尺寸下自动缩放文字，避免溢出/留白 |
| `auto-split` | 按渲染后高度自动切分分页（推荐） |
| `dynamic` | 根据内容动态调整图片高度 |

### Step A.3: 获取生成结果

生成结果保存在输出目录：

```
output/
├── cover.png      # 封面图片
├── card_1.png     # 第一张正文卡片
├── card_2.png     # 第二张正文卡片
└── ...
```

图片尺寸：1080×1440px（3:4 比例，符合小红书推荐）

## 流程 B: 内容创作

当用户要求撰写小红书笔记内容时执行。

### Step B.1: 收集创作需求

确定以下信息：

- **主题**：笔记要讲什么
- **风格**：种草/教程/测评/生活记录等
- **结构**：要点列表、步骤说明、对比表格等
- **配图**：是否需要生成图片卡片

### Step B.2: 生成 Markdown 内容

根据用户需求生成符合小红书风格的 Markdown 内容：

- 标题简洁有力（建议 15 字以内）
- 使用 emoji 增强视觉效果
- 段落简短，每段 3-4 句话
- 适当使用列表和表格
- 话题标签放在最后：`#标签1 #标签2`

### Step B.3: 用户确认

通过 `AskUserQuestion` 展示生成的 Markdown 内容，获得确认后继续渲染。

### Step B.4: 渲染图片（如需要）

用户确认内容后，执行图片渲染流程（参考流程 A）。

## 流程 C: 完整创作（内容+图片）

当用户要求"创作小红书内容并生成图片卡片"时，一站式完成。

### Step C.1: 收集需求

与用户确认：主题、风格、结构、输出形式。

### Step C.2: 生成并渲染

1. 根据需求生成 Markdown 内容
2. 用户确认内容
3. 执行渲染生成图片卡片

## 失败处理

- **渲染超时**：增加等待时间或使用更简单的布局
- **字体缺失**：检查系统字体安装
- **图片尺寸不匹配**：确保 Markdown 内容适合 1080×1440 尺寸
- **主题样式异常**：检查 `assets/themes/` 目录下的主题 CSS 文件
