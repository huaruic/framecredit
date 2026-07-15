# Plan: Landing 简洁度重构（线格布局，配色字体不变）

Status: FINAL v2, 按 codex review 收敛为外科式文案裁剪
（codex session `019f6653-230e-7383-972d-59ce7d30aaea`；
下方 v1 中与本节冲突的内容一律作废）

## FINAL：定稿改动（45-90 分钟）

1. #what-is：两段散文 → 一段 35-50 词定义（保留实体：local video
   attribution tool / X creators / burned into video frames / reposted
   copies retain attribution）+ 三条语义 <ul> 差异点。
   **不做 2×2 事实格**（不必要的卡片化，且拟稿有三处措辞不严谨：
   "100% local" 忽略安装下载、"Survives re-encoding" 绝对化、
   "Same dimensions and audio" 歧义）。可见自然句子仍是 GEO 主载体，
   llms.txt 与 FAQPage rich results 都不可依赖。
2. #install（重头）：三列线格只放平台前置依赖
   （macOS/Homebrew | Windows/winget | Debian-Ubuntu/apt），
   共享的 uv tool install framecredit 与 framecredit app 在其下只出现
   一次；pip 与源码安装收进 <details> "Alternative installation"；
   删全部客套句。三列 ~950px 即塌；grid 子项加 min-width:0；
   移动端 DOM 顺序保持 平台→命令。
3. #how-it-works：三步各压到一句话，保留 01/02/03 编号。
4. #privacy：压缩为加粗首句 + 一行。
5. #scope：基本保持原样（限定条款是信任建设，约束 marker 声明）。
6. 微修正：h1/h2 加 text-wrap: balance；顺手改 curly 撇号。
   **跳过**：touch-action、&nbsp;（会把 FAQ 镜像文本变 U+00A0 破坏
   JSON-LD 等值）、em-dash 专项验证。
7. 改完文案后**审计 JSON-LD**（结构化数据须代表可见主内容，
   "零改动"不再是硬约束，FAQ 原文不动则镜像不动）。
8. 验证：token 等值测试、全量 unittest、320/390/1200 + 400% zoom、
   JSON-LD parse + FAQ 镜像、Lighthouse 复测。



## 动机

用户判断 + 审计确认：可见正文过长（"What is" 两段 95 词且与 hero、
How-it-works 三处重复同一卖点；Install 区 7 个代码块间夹 10 句客套散文；
每步说明 25-42 词）。参考 open-agents.dev 的手法：每区域一个短句 +
一个视觉锚点，用线条划分区域。

## 约束（不变项）

- 配色、字体、GEIST TOKENS 全部不动（token 等值测试继续生效）
- 锚点 id、nav/footer 链接、meta/OG、两个 JSON-LD 块零改动
- FAQ 全部保留原文（GEO 素材，默认折叠，与 FAQPage JSON-LD 镜像）
- app 页零改动；app 截图不需重制

## 改动

1. Hero：不动。
2. #what-is：散文两段废除，改 2×2 hairline 事实格
   （grid gap:1px、背景透出 --ds-gray-400、格子底 --ds-background-200，
   Geist 经典网格），四格：
   - Burned into pixels / not metadata, so stripping metadata changes nothing
   - Survives re-encoding / ordinary reposts keep your handle readable
   - 100% local / binds 127.0.0.1, nothing uploads
   - Normal MP4 out / H.264 + AAC, same dimensions and audio
   每格：短标题 + 一行 ≤15 词。区块保留一句 GEO 定义句（≤25 词）作为
   section 引言。
3. #how-it-works：保留 01/02/03 编号结构，每步正文压到一句话 ≤18 词。
4. #install：三平台改并排三列线格（macOS | Windows | Linux，格内只有
   平台名 + 代码块）；pip 与源码安装合并为其下一行备选；验证三连与
   framecredit app 保留但删客套句；移动端三列塌成单列。
5. #scope：三段散文 → 三条 hairline 分隔短句（复用 marker-facts 列表
   样式家族要注意 taste 的布局重复规则：marker-facts 已用同款，改用
   无边框短段或并入事实格，二选一由实现时定，倾向短段）。
6. #privacy：压缩为加粗首句 + 一行补充。
7. Guidelines 小项：正文撇号改 curly（'），h1/h2 加 text-wrap: balance，
   按钮加 touch-action: manipulation，数字单位加 &nbsp;
   （150&nbsp;milliseconds、H.264 等处）。

## 验证

token 等值测试、全量 unittest、390/1200 截图、零 em-dash、
JSON-LD parse 且 FAQ 镜像不变、Lighthouse 复测、线上抽查。

## 预期

可见正文约 -40~50%；结构从"文章"变"版面"。工作量 2-3 小时。
