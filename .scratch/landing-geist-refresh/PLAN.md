# Plan: Landing page 对齐 Geist 设计规范

Status: proposed（依据 vercel.com/design.md 与 design.dark.md，2026-07-15 抓取）

## 背景

当前 landing（site/index.html）是"Vercel 风格"的手工近似。现以 Geist
官方规范为基准做一次系统对齐。范围仅 landing page；本地 app 页面
（src/framecredit/static/index.html）后续可复用同一套 token，另行处理。

## 1. 颜色 token 对齐（现值 → Geist dark 目标值）

| 用途 | 现值 | Geist dark | 动作 |
|---|---|---|---|
| 页面/面板背景 | #000 / #0a0a0a | background-100/200 均为 #000000 | 面板不再用 #0a0a0a 实色，改用 #000 + gray-alpha 边框分层 |
| 面板层级底色 | - | gray-100 #1a1a1a（hover #1f1f1f 级） | 需要"抬起"的卡片（如安装块代码区）用 #1a1a1a |
| 默认边框 | #262626 | gray-400 #2e2e2e | 替换 |
| 强边框/hover | #333333 | gray-500 #454545 | 替换，hover 递进 400→500→600 |
| 主文字 | #ededed | primary #ededed | 保持 |
| 次文字 | #a1a1a1 | secondary #a0a0a0 | 微调 |
| 弱文字 | #666 | gray-700 #8f8f8f（disabled 档） | 改 #8f8f8f，保证 AA |
| 焦点蓝 | #0070f3 | dark 模式焦点应为 blue-900 #47a8ff | 替换（#0070f3 是亮色模式值，黑底上对比不足） |
| 焦点环 | outline 2px | 双层 box-shadow: 0 0 0 2px #000, 0 0 0 4px #47a8ff | 替换 |

全部收敛为 CSS 变量，命名跟随 Geist 语义（--ds-background-100、
--ds-gray-400、--ds-blue-900…），为以后 app 页复用做准备。

## 2. 字体：自托管 Geist

landing 是公开网站（非本地 app 的 CSP 约束），可以自托管字体：

- 下载 Geist Sans（400/500/600）与 Geist Mono（400）woff2，
  放 site/fonts/（Geist 为 SIL OFL 许可，允许自托管分发）；
- @font-face + font-display: swap + preload 首屏两档；
- fallback 栈保留现有系统字体；
- 体积预算：4 个 woff2 约 120-160KB，可接受；不引任何 CDN。

排版 token 对齐：

- 标题走 heading 系：h1 = heading-40（40px/600/-1.6px 级），
  section h2 = heading-32，卡片 h3 = heading-16；
- 正文 copy 系（copy-16：400/行高 1.6）；按钮 button-14（500 weight，
  现在的 600/700 全部降到 500）；
- 每视图不超过两种字重（400/500/600 里挑两档主用，600 只给标题）。

## 3. 圆角与阴影

- 按钮/输入/代码块/FAQ 项：8px → 6px（Geist sm）；
- 大媒体面（截图框、hero 卡）：8px → 12px（md）；
- 不再混用其他圆角；
- 抬起的卡片加 Geist dark raised 阴影 `0 1px 2px rgba(0,0,0,.16)`，
  其余保持平面 + 边框。

## 4. 间距节奏

按 4px 尺度审计：组内 8px、组间 16px、区块间 32-40px；
卡片 padding 统一 24px（现 .panel 28px）；hero 区 32px。
shell 宽度 1080px → 1200px（Geist 容器标准），断点对照
sm 401 / md 601 / lg 961 / xl 1200。

## 5. 按钮体系

| 变体 | 现状 | Geist dark 目标 |
|---|---|---|
| Primary | #fff 底黑字，hover #ccc | #ededed 底 #000 字，40px 高，6px 圆角，hover 降一档灰 |
| Secondary | 透明底 + #333 边 | #000 底 + gray-alpha 半透明边，hover 边框 500 档 |
| Tertiary（新增，可选） | - | 透明底 #ededed 字，hover 灰底，用于 nav 内链 |

状态递进统一：背景 100→200→300，边框 400→500→600。

## 6. 动效与交互

- 过渡时长统一 token：状态 150ms、浮层 200ms；
  easing `cubic-bezier(0.175, 0.885, 0.32, 1.1)`；
- 保持 prefers-reduced-motion 全关；
- "motion 只用于说明变化"：现页只有 hover/焦点/平滑滚动，符合，不加新动效。

## 7. 文案语态（Geist voice）

- 按钮与 nav 标签改 Title Case：`Install FrameCredit`（已符合）、
  `See how it works` → `See How It Works`、nav `How it works` →
  `How It Works`；
- 正文与 FAQ 保持 sentence case；
- 决策点：section 标题（h2）是否也 Title Case——Geist 对 "titles"
  用 Title Case，但长句式标题（"What FrameCredit does not promise"）
  Title Case 会变拗口。倾向：h2 保持 sentence case，只有按钮/标签/nav
  走 Title Case。待拍板。

## 8. 明确不做

- 不引入 Geist 的浅色模式（页面锁暗色，og/screenshot 均为暗色资产）；
- 不引入 P3/oklch 双轨 token（单页静态站，收益不值复杂度）；
- 不改信息架构、锚点 id、文案内容（SEO/结构化数据不受影响）；
- FAQPage/SoftwareApplication JSON-LD 不动。

## 9. 验证清单

- 双端截图（1200 / 390 宽）对照改版前；
- 焦点环键盘走查（Tab 全链路）；
- 对比度抽查（#8f8f8f on #000 = 7.4:1，#a0a0a0 = 8.3:1，均过 AA）；
- Lighthouse 性能回归（字体自托管后 LCP 预算 <2.5s，preload 验证）；
- 零 em-dash、JSON-LD parse、Pages 部署后线上抽查。

## 工作量估计

token 替换 + 按钮/圆角/间距（§1/3/4/5）约 1-2 小时；字体自托管（§2）
约 1 小时（含下载、子集评估、preload 调试）；文案语态（§7）15 分钟；
验证（§9）30 分钟。合计约半天。
