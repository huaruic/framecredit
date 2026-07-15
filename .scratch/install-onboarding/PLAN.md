# Plan: 降低非开发者的安装门槛

Status: revised after codex review 2026-07-15（session `019f6602-055d-7c12-a2ed-0ecc76152938`）

## Revision v2（codex review 结论，覆盖下方原稿的冲突处）

采纳的关键修正：

1. **原 macOS 命令是坏的**：Homebrew 的 Python 遵循 PEP 668，
   `pip3 install framecredit` 会被 externally-managed-environment 拒绝。
   macOS 一条龙改为：`brew install uv ffmpeg && uv tool install framecredit`。
2. **砍掉阶段 2（Homebrew tap）**：uv 路线已用两条命令覆盖 macOS/Windows/Linux，
   tap 带来的是持续维护成本（每次发版 bump formula、Pillow resource 源码
   编译、audit、双架构测试），收益边际。挂起，等真实需求（用户反馈/issue）
   再启动，届时用 codex 指出的方案 A（vendor resources）而非 B。
3. **文档层补齐**（原稿遗漏）：装完的最后一步 `framecredit app`；
   新开终端/PATH 刷新说明；`python3 -m pip` 替代裸 `pip`；
   `sudo apt update &&`；验证三连 `framecredit --version` /
   `ffmpeg -version` / `ffprobe -version`；Windows 用
   `winget install --id Gyan.FFmpeg.Essentials -e --source winget`
   （比完整版轻，manifest 含 ffmpeg/ffprobe aliases）。
4. **平台分流替代"uv 全平台主推"**：有 Homebrew 的 macOS 用户
   `brew install uv ffmpeg`；无 Homebrew 的 macOS 用 uv standalone
   installer；Windows/Linux 首推 uv。不要求用户为装 FrameCredit 先装 Homebrew。
5. **阶段 3 从"立 issue"升级为"限时一天 spike + issue"**，spike 清单：
   桌面入口（现在 CLI 无参会直接 argparse 报错，需要新入口直启 app）、
   bundled ffmpeg 的显式解析（现在只查 PATH，打包了也不会用）、
   进程退出机制（关浏览器不会停服务）、windowed 模式错误可见性、
   静态资源收集、系统字体、干净 VM 真实视频验证、
   Gyan 静态 GPLv3 build + libx264 的分发合规材料。
6. **验证标准修正**：unittest 会因缺 ffmpeg/playwright 而 skip，
   "测试进程绿"不等于安装路径验证过；文档发布后需在干净环境
   （或至少全新 venv + 新终端）实际走一遍每条安装命令。
7. **CI 增加 Python 3.13**（独立小项）：classifier 和任何分发渠道
   声称 3.13 支持之前，先让 CI 测过。
8. local-only 与"检查更新"的关系修正：承诺的边界是视频数据不出本机，
   不自动等于不能查版本；不做更新检查的真实理由是隐私姿态、复杂度
   与维护成本。结论不变（不做），理由修正。

执行顺序（修订后）：文档层（含上述全部修正）→ CI 加 3.13 →
桌面打包 spike（另行排期）。Homebrew tap 挂起。

---

（以下为 v1 原稿，保留供追溯）

## 背景与目标

当前唯一安装路径是 `pip install framecredit`，隐含两个前置：Python 3.11+ 和
ffmpeg/ffprobe on PATH。对目标用户（创作者，非开发者）这是 20-40 分钟的环境
配置墙，Windows 上尤其痛（Python 不自带、ffmpeg 要手动配 PATH）。

分三个阶段降低门槛，成本递增、独立交付：

- 阶段 1：文档层（本次执行，约 30 分钟）
- 阶段 2：Homebrew tap（本次执行，约半天）
- 阶段 3：桌面打包（只立 issue 挂账，不排期；真正小白市场留给它或 SaaS）

不做的事：app 内置更新检查或安装器下载逻辑（违反 local-only 承诺）；
任何需要账号/云端的分发方式（那是 SaaS 层的事）。

## 阶段 1：文档层

官网 `site/index.html` Install 区新增 "Not a developer?" 子块，按平台给
一条龙命令：

- macOS（有 Homebrew）：
  `brew install python ffmpeg && pip3 install framecredit`
- 任意平台（推荐主路径，Python 由 uv 自动管理）：
  1. 装 uv：macOS/Linux `curl -LsSf https://astral.sh/uv/install.sh | sh`；
     Windows `winget install astral-sh.uv`
  2. `uv tool install framecredit`
  3. ffmpeg：macOS `brew install ffmpeg`；Windows `winget install Gyan.FFmpeg`；
     Debian/Ubuntu `sudo apt install ffmpeg`
- 升级对照：`pip install -U framecredit` / `uv tool upgrade framecredit` /
  `pipx upgrade framecredit`

同步改动（保持镜像一致）：

- FAQ 新增一条 "Do I need to know Python to use FrameCredit?"，
  FAQPage JSON-LD 同步；
- README（英/中）Quick start 增加 uv 一行替代路径；
- `site/llms.txt` 安装段落更新。

验证：页面本地渲染截图、JSON-LD `json.loads` 校验、零 em-dash 检查、
全量 unittest（文档不涉代码，跑一遍作为回归习惯）、Pages 部署后线上抽查。

## 阶段 2：Homebrew tap

目标：macOS 用户一条命令 `brew install huaruic/tap/framecredit`，
Python 和 ffmpeg 作为依赖自动带上。

- 新建公开仓库 `huaruic/homebrew-tap`，`Formula/framecredit.rb`；
- formula 采用 Homebrew 标准的 Python 应用打包方式：
  `include Language::Python::Virtualenv`，
  `depends_on "python@3.13"`、`depends_on "ffmpeg"`，
  url 指向 PyPI sdist（framecredit-0.1.2.tar.gz）+ sha256，
  `virtualenv_install_with_resources` 安装；
- 风险点：Pillow 作为 resource 时 brew 会从 sdist 源码编译，需要
  `depends_on "libjpeg-turbo"`、`zlib` 等构建依赖，维护成本高。
  备选方案 A：resource 里直接引用 Pillow sdist 并补齐构建依赖；
  备选方案 B：formula 不 vendor Pillow，而是 `depends_on "pillow"`
  （homebrew-core 有 pillow formula，绑定其 python 版本）；
  倾向 B，代价是 Python 版本跟随 homebrew-core 的 pillow。
- 每次发版需要 bump formula 的 url/sha256：在 tap 仓库加一个
  说明文档，先手动 bump（发版频率低），后续可用
  `brew bump-formula-pr` 或 GitHub Action 自动化；
- 测试：本机 `brew install --build-from-source huaruic/tap/framecredit`，
  验证 `framecredit --version`、`framecredit app` 启动、
  处理一个真实视频成功；
- 完成后回填阶段 1 文档：macOS 首推命令改为
  `brew install huaruic/tap/framecredit`。

## 阶段 3：桌面打包（只立 issue）

在 `.scratch/install-onboarding/issues/01-desktop-app-packaging.md` 记录：

- 目标：双击即用的 .app（macOS）/.exe（Windows），bundle Python 运行时
  与 ffmpeg 二进制，点开即启动本地界面；
- 技术候选：PyInstaller（单文件，成熟）vs Briefcase（原生工程结构）；
- 许可证核对：ffmpeg 以 GPL 配置分发时与 AGPL-3.0 应用的兼容性
  （初判兼容，需在 issue 里确认具体 build 的许可配置）；
- 成本项：macOS 签名 + 公证需要 Apple Developer Program（$99/年）；
  Windows 无签名会触发 SmartScreen 警告，EV 证书另算；
- 更新分发：不做自动更新（local-only 承诺），Release 页手动下载；
- 验收草案：一台从未装过 Python/ffmpeg 的干净机器，下载后双击即可
  完成一次真实视频的 Attributed Export。

Status: proposed，不排期，等开源版用户量或 SaaS 决策后再定。

## Open questions（请 codex 重点评审）

1. 阶段 2 的 Pillow 处理：方案 A（vendor sdist + 构建依赖）vs
   方案 B（depends_on homebrew-core 的 pillow），哪个长期维护成本低？
   有没有第三种更简做法？
2. 文档层的平台顺序：uv 做全平台主推是否合理，还是 macOS 直接首推
   brew 路线（阶段 2 完成后）？
3. Windows 非开发者路径 `winget install Gyan.FFmpeg` 是否是当前最优？
4. 阶段 3 现在只立 issue 是否足够，还是有必要先做一个
   PyInstaller 可行性 spike（比如确认 Pillow + 打包体积）？
5. 有没有遗漏的更低成本方案（比如 GitHub Codespaces/容器路线对这个
   本地视频场景是否完全不适用）？
