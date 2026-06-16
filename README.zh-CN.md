# design-to-frontend

[English](README.md) · **中文**

一个 Claude Code **技能(skill)**:把现有的 *Claude Design 原型* —— 一个浏览器内运行的
React + `@babel/standalone` HTML 原型(单个 HTML 入口加载 `src/*.jsx` + 设计令牌,**无构建步骤**)
—— 推进到可交付开发、打磨完善的前端。

> `SKILL.md` 是技能触发时 Claude 实际遵循的"作业手册";本文件面向**人类** —— 说明这个技能是什么、
> 怎么安装、以及如何直接使用它自带的脚本。

## 它能做什么 —— 四类活动

每一类都是独立入口;从零开始的完整流程从左到右依次进行。

| 活动 | 做什么 | 指南 |
|---|---|---|
| **摄取 (Ingest)** | 梳理原型的页面/组件/设计令牌,找出代码引用了但实际缺失的图片资源,写出/刷新 `DESIGN.md` 规格 | `references/1-ingest-design.md` |
| **生成 (Generate)** | 用 OpenAI 图像 API 生成缺失的图片资源(吉祥物/banner/图标),**透明背景**,并按文件名约定落盘 | `references/2-generate-assets.md` |
| **新建 (Build)** | 以原型一贯的方式新增页面/组件/功能(复用令牌、`window` 注册、接入导航) | `references/3-polish-frontend.md` |
| **打磨 (Polish)** | 视觉层级、交互/状态完整性、移动端工效、多语言、可访问性 —— 每处改动都在真实浏览器中验证 | `references/3-polish-frontend.md` |

**不适用于**:与原型资源无关的通用图像生成、从零搭框架应用(Next.js/Vite/Vue)、Web 性能/SEO 优化、
后端、logo 设计、一次性文件转换、Figma 等设计工具。

## 安装

技能就是一个文件夹(或该文件夹打包成的 `.skill` zip)。放到 Claude Code 能发现技能的位置即可:

```
~/.claude/skills/design-to-frontend/      # 个人级 —— 所有项目可用
# 或  <项目>/.claude/skills/design-to-frontend/   # 仅当前项目
```

从本仓库直接安装:

```bash
git clone https://github.com/magicnight/design-to-frontend-skill ~/.claude/skills/design-to-frontend
```

从 `.skill` 文件安装:解压到 `~/.claude/skills/` 即可(会展开成 `design-to-frontend/`)。Claude 会自动
把它列入可用技能,无需重启;匹配到相应请求时它会**自动触发**(触发条件见 `SKILL.md` 的 `description`),
不需要手动调用。

## 依赖

- **Python 3** + [`uv`](https://docs.astral.sh/uv/) —— `uv venv && uv pip install pillow`(Pillow 仅用于
  PNG→WebP 转换;生成器和服务器都是纯标准库)。
- **OpenAI API key**,填到*项目的* `.env`(`OPENAI_API_KEY=...`)—— 仅"生成"活动需要。切勿硬编码或写进
  环境变量;脚本会读 `.env`。
- **浏览器驱动**(Playwright 或浏览器 MCP),用于"新建/打磨"中的验证循环。

## 自带脚本(`scripts/`)

除标注外均为纯标准库;在项目根目录运行。

```bash
# 1) 生成透明背景资源(先编辑脚本里的 JOBS,把 key 填进 .env)
python scripts/gen_image.py                 # 全部任务  ·  python scripts/gen_image.py icon_wallet
python scripts/check_alpha.py out/icon_wallet.png   # 校验 alpha 是否真透明(四角应为 0)

# 2) 用禁缓存服务器预览原型(改动后换一个新端口)
python scripts/nocache_server.py 8853       # → http://127.0.0.1:8853/<入口>.html
```

`gen_image.py` 用 **`gpt-image-1.5`**(不是 `gpt-image-2`,后者不接受 `background=transparent`),
同时支持 `/images/generations`(文生图)和 `/images/edits`(带参考图、跨姿态保持角色一致)。

## 它依赖/传授的约定

- **资源命名池** —— UI 按文件名自动取图(如 `assets/<类>/m-<日>-<场次>.webp`、随机 `pool-<N>.webp`),
  缺图回落 `placeholder.webp`。外部开发只按命名丢图,无需改代码。(详见指南 2。)
- **多语言字体架构** —— 正文/标题用拉丁字体(Inter)→ Noto Sans SC/JP/KR/… 兜底,杜绝"豆腐块";
  装饰/`numeric` 字体(如 Orbitron)**只用于纯 ASCII**(数字、货币代号、品牌词)。(指南 3 的 P4。)
- **无构建、浏览器内验证** —— 改 `.jsx` 即刷新;babel 按 URL 缓存,所以用换端口的禁缓存服务器破缓存;
  每处改动先确认 0 控制台报错 + 截图,再声称完成。

## 目录结构

```
design-to-frontend/
├── SKILL.md                       # 面向 agent 的作业手册(触发条件 + 跨阶段铁律)
├── README.md                      # 英文说明
├── README.zh-CN.md                # 本文件
├── references/
│   ├── 1-ingest-design.md
│   ├── 2-generate-assets.md
│   └── 3-polish-frontend.md       # 新建 + 打磨
└── scripts/
    ├── gen_image.py               # OpenAI gpt-image-1.5,透明 PNG
    ├── check_alpha.py             # 校验 PNG 的 alpha 通道
    └── nocache_server.py          # 禁缓存静态服务器
```

## 作者与许可

由 **Kefeng Zhou** &lt;magicnight@gmail.com&gt; 创建。基于 MIT 许可证发布 —— 见 [`LICENSE`](LICENSE)。
