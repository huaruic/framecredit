# Plan (FINAL): Landing 与本地 app 页面对齐 Geist 设计规范

Status: final v3, ready to implement
History: v1 landing-only 草案 → v2 扩至双页 + taste-skill 合规检查 →
v3 吸收 codex 两轮 review（sessions `019f661e-5587-77e2-b5e7-6eb39546dc95`）。
本文为唯一有效版本，v1/v2 中与此冲突的内容一律以本文为准。

## 范围与一致性策略

- 两个页面：site/index.html（landing，GitHub Pages）与
  src/framecredit/static/index.html（本地 app）。
- **只共享 primitives**（颜色、灰阶、圆角、焦点环、动效时长、按钮规格）；
  排版密度与布局各自保留——landing 是营销页，app 是产品界面，
  不强行同构。
- 无构建系统：两文件各持一份带 `/* GEIST TOKENS v1 */` 标记的变量块，
  新增 `tests/test_design_tokens.py`（纯文本：提取两文件标记块、
  归一化空白、断言相等）作为防漂移的强制机制，注释不作为约束手段。

## 定稿 token 映射（修正版）

| 语义变量 | 值 | 用途 |
|---|---|---|
| --ds-background-200 | #000000 | 页面底色 |
| --ds-background-100 | #0a0a0a | 面板/卡片 surface（保留现有分层，v2 中"面板改纯黑"作废） |
| --ds-gray-100 | #1a1a1a | 更高一层 fill（代码块底、hover 面） |
| --ds-gray-400 | #2e2e2e | 默认边框 |
| --ds-gray-500 | #454545 | hover 边框 |
| --ds-gray-800 | #8f8f8f | 最弱文字（隐私注脚等；黑底对比约 6.5:1，过 AA） |
| --ds-gray-900 | #a1a1a1 | 次要文字（与现值相同，不动） |
| --ds-gray-1000 | #ededed | 主文字（不动） |
| --ds-blue-900 | #52a8ff | 暗色焦点环外环 |
| --ds-focus-ring | 0 0 0 2px var(元素 surface), 0 0 0 4px var(--ds-blue-900) | 双层焦点环；内环用所在 surface 变量，不硬编码 |

注：两份抓取源对暗色焦点蓝记录不一致（#47a8ff vs #52a8ff），
codex 联网核对 Geist 文档为 blue-900 = #52a8ff，采用后者。
#0070f3 是 blue-700/action blue，不再用作暗色焦点环。

## 圆角（按角色，不按"控件/容器"二分）

- 6px：按钮、输入框、chips、代码块、FAQ 项（现 8/10px 者）
- 12px：workspace 面板、截图框、hero 媒体面（app 现 8px、landing 现 8px）
- 不引入 16px 档（本项目无 fullscreen surface）

## 按钮

- Primary：#ededed 底 / #000 字 / 500 字重 / 40px 高 / 6px 圆角；
  hover #cccccc。不套灰阶 100→200→300 递进（那是低对比 surface 的
  规则，不适用于高对比 primary）。
- Secondary：#0a0a0a 底 + rgba(255,255,255,.14) 半透明边；
  hover 边框升 gray-500。
- 小控件（位置 chips 等）不强行拉到 40px，保持紧凑档，仅统一
  圆角/颜色/焦点环。
- 按钮与 nav 标签 Title Case（Geist voice）；章节标题 h2 保持
  sentence case（taste skill 与 Geist 在此切分下互不冲突，定案）。

## 字体

- **App 页：维持系统字体栈（定案）**。理由：canvas 标识预览显式使用
  系统栈做 JS 度量，导出渲染用 Arial/PingFang/Noto/DejaVu
  （processing.py），换 Geist 反而拉大预览与导出的差距；
  打包字体的路由/包体/测试成本对本地工具无收益。
- **Landing：自托管 Geist variable 字体 ×2**：
  Geist Sans variable（覆盖 400-600）+ Geist Mono variable（400），
  woff2 放 site/fonts/，**附 OFL.txt**（SIL OFL 1.1 要求许可文本
  随字体分发）；只 preload Sans，Mono 常规加载；
  fallback 保留系统栈；以实际构建产物体积为准，若两个 variable
  文件反而更大再改静态子集。
- Landing hero 用较大的 marketing 标题档（56-48px 级），
  不锁死在 heading-40。

## 间距与容器

- 4px 尺度审计：组内 8、组间 16、区块间 32-40；卡片 padding 24px。
- landing shell 1080 → 1200px；**app 页 shell 保持现宽**（双栏平衡
  与 820px 断点已调好，改宽需重新平衡，收益低）。
- 断点检查覆盖 390 / 820（app 断点）/ 1200。

## App 页专项

- 行为零改动：id、API、canvas 绘制逻辑（字体、描边、坐标、尺寸）
  全部不碰。
- 不给 marker 预览加任何不透明底（产品声明是 transparent outlined
  text，页面组件不得与之矛盾）。
- 补上缺失的可访问性项：drop zone 的键盘焦点态
  （`:focus-within` 显示 --ds-focus-ring），浏览器测试加断言。
- Playwright 现有断言只覆盖文案与 canvas 可见性，样式改动后跑
  全量回归确认未误伤。

## 连锁更新（v2 遗漏，codex 补）

改版完成后按序重制三件视觉资产（app 页样式变了，旧图即过期）：

1. `site/app-screenshot.png`（landing hero + README + JSON-LD 引用）
2. `site/og.png`（由新截图合成）
3. GitHub 社交预览图（1280×640，需用户手动重传）

## 明确不做

- 浅色模式；P3/oklch 双轨；信息架构/锚点/JSON-LD 结构改动；
- app 页字体打包（除非日后用户反馈两页字体差异不可接受，
  届时走 /fonts 路由 + font/woff2 MIME + 包数据 + 路由测试，
  CSP 无需改动——default-src 'self' 已覆盖同源字体）。

## 验证清单

1. `tests/test_design_tokens.py` 等值断言通过
2. 全量 unittest + 强制 Playwright 浏览器测试
3. 键盘 Tab 走查两页焦点环（含 drop zone）
4. 对比度实测复核（工具计算，不再手估）
5. 390/820/1200 三档截图对照
6. Lighthouse：字体自托管后 LCP < 2.5s，preload 不重复请求
7. 零 em-dash、JSON-LD parse、Pages 部署后线上抽查
8. 三件视觉资产重制并验证引用处

## 工作量

token/圆角/按钮双页对齐约 3 小时，landing 字体 1 小时，
焦点态 + 等值测试 1 小时，资产重制与验证 1.5 小时。约一个工作日。
