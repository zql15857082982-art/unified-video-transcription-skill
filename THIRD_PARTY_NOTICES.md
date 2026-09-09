# 来源与第三方说明

## 直接来源

本项目由 [zql15857082982-art/unified-video-parser](https://github.com/zql15857082982-art/unified-video-parser) 的本地版本 `97dbd7e` 拆分而来。`app/` 中的平台解析、HTTP 请求、数据模型和链接处理代码由该版本复制并修改。Skill 安装器、命令行转写入口及 HTML 报告是本项目新增或改写的部分。

原项目采用 MIT License，版权声明为 `Copyright (c) 2026 Video Link Parser contributors`。本项目 LICENSE 保留该声明，原始许可证另存于 `third_party/unified-video-parser/LICENSE`。

## 原项目列明的参考仓库

原项目初始提交 `7634c46` 及上述版本的 THIRD_PARTY_NOTICES.md 都说明，其平台页面数据结构和部署方式参考了以下项目。2026-09-09 核对各仓库当前 LICENSE：

| 仓库 | 许可证 | 原版权声明 |
| --- | --- | --- |
| [jiji262/douyin-downloader](https://github.com/jiji262/douyin-downloader) | MIT | Copyright (c) 2026 jiji262 |
| [wwwzhouhui/video-parser](https://github.com/wwwzhouhui/video-parser) | MIT | Copyright (c) 2025 ucmao |
| [hostinger-bot/rednote-api](https://github.com/hostinger-bot/rednote-api) | MIT | Copyright (c) 2025 BOTCAHX |

这里保留的是原项目声明的参考关系；仓库历史没有逐行记录参考来源，不能据此声称每个函数都来自某一仓库。三个项目的完整许可文本及核对时的许可证文件 SHA 保存在 `third_party/` 中，随 Skill 一起分发。

原项目说明未包含或依赖 `videodl`。本项目依赖清单中也不包含该软件；这里不把它标为本项目代码来源。

## 安装依赖与外部服务

- [HTTPX](https://github.com/encode/httpx) 0.28.1：BSD-3-Clause，用于 HTTP 请求。
- [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) 0.6.0：Python 包采用 BSD-2-Clause。安装时由 PyPI 获取相应平台的 FFmpeg 可执行文件；FFmpeg 的许可证取决于构建选项，不属于本项目 MIT 许可覆盖的代码。请参阅 [FFmpeg 许可说明](https://ffmpeg.org/legal.html) 和所安装包附带的许可证。
- 其他 Python 间接依赖保留各自随发行包提供的许可证。仓库仅包含依赖清单，不重新分发虚拟环境或 FFmpeg 二进制。
- 音频转写调用用户自己的 [Xiaomi MiMo API](https://platform.xiaomimimo.com/)；视频号解析使用用户自己的腾讯元宝登录状态。两者都是外部服务，服务条款不被本项目 MIT 许可替代。
- 原解析器保留一个默认关闭的第三方视频号备用解析选项 `WEIXIN_WORKER_FALLBACK`。正常安装与测试不启用此选项；它会把分享链接交给第三方服务，不需要启用它来使用本 Skill。

本项目没有获得上述平台或参考项目的背书。开源代码许可不授予他人视频内容的版权或账号访问权限。
