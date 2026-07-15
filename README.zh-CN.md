# FrameCredit

**发布前把你的 X 用户名烧录进视频的每一帧，被搬运转发后观众依然认得你。**

视频在 X（Twitter）上被下载重传时，通常什么都保留，唯独丢了作者。
FrameCredit 把一个紧凑的描边文字标识 `X · @你的用户名` 直接渲染进视频像素：
它不怕转码、跟着每一份拷贝走，并且每 30 秒在左右上角之间切换，不会永久遮挡
画面的任何区域。

全部在你自己的电脑上运行：无账号、无上传、无云端。

## 安装

需要 `ffmpeg`/`ffprobe` 在 PATH 上。下面的 `uv` 路线会自动管理 Python；
已有 Python 3.11+ 的话直接用 pip 也行。

**macOS**

```bash
brew install uv ffmpeg
uv tool install framecredit
```

**Windows（PowerShell）**

```powershell
winget install astral-sh.uv
winget install --id Gyan.FFmpeg.Essentials -e --source winget
uv tool install framecredit
```

**Debian/Ubuntu**

```bash
sudo apt update && sudo apt install ffmpeg
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install framecredit
```

**已有 Python 3.11+**

```bash
python3 -m pip install framecredit
```

新开一个终端验证：`framecredit --version && ffmpeg -version && ffprobe -version`。
升级：`uv tool upgrade framecredit` 或 `python3 -m pip install -U framecredit`。

## 快速开始

命令行：

```bash
framecredit process input.mp4 --x-handle "@yourhandle" --output attributed.mp4
```

本地拖拽界面（只监听 127.0.0.1，视频不出本机）：

```bash
framecredit app
```

## 诚实的边界

FrameCredit 的目标是**署名存活**（Attribution Survival），不是防盗：

- 烧录的像素无法成为可点击链接或二维码；
- 有心人总能裁剪或遮盖任何可见标识；
- 它能做到的是：视频经过普通搬运（转码、轻裁剪、加字幕）后，观众仍能读到
  你的用户名并搜索到你。

更多说明见 [英文 README](README.md) 和 [官网](https://huaruic.com/framecredit/)。

## 许可证

[AGPL-3.0-or-later](LICENSE)。可自由使用、修改、再分发；若把修改版作为
网络服务运行，必须以同样的许可证向用户提供源码。
