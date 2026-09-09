# 本地视频转写 Skill

将视频分享链接转成 HTML 文稿。支持抖音、快手、小红书和视频号的解析；首次使用由 agent 引导填写自己的 MiMo API Key、必要的 Cookie 和安装位置。

转写程序随 Skill 一起提供。无需服务器或 Docker，数据和登录配置由每位用户在本机管理。解析、下载和提取音频在本机执行；音频会发送到 MiMo，按用户自己的账号用量计费。

## 安装与使用

将此 Skill 目录链接发给支持安装 GitHub Skill 的 agent：

```text
https://github.com/zql15857082982-art/unified-video-transcription-skill/tree/main/skills/video-transcription
```

可以这样说：“请安装这个 Skill，按说明帮我在本机配置。我会提供自己的 MiMo Key 和需要的平台 Cookie。” Codex 已实测；WorkBuddy 是否能自动安装取决于其版本，尚未实测。也可下载完整仓库，再让 agent 从本地 Skill 文件夹安装。

将完整的 `skills/video-transcription` 文件夹安装到 agent 的技能目录（Codex 为 `~/.codex/skills/video-transcription`），然后说：

> 使用 video-transcription 转写这个视频：视频链接

固定只生成本地 HTML：包括转写正文、原链接、解析后的下载地址、封面链接、作者及平台返回的互动数据。HTML 无额外依赖或模型调用，正文可离线阅读，外部视频链接需联网打开。下载地址可能过期，文档会记录平台提供的到期时间。

安装需要 Python 3.10+ 和网络；常见 Windows/macOS 的 FFmpeg 由脚本自动准备。默认程序目录为 `~/.video-transcription`，也可指定其他位置。首次完成配置后，每次只需提供链接。

凭证获取步骤和安装命令见 [Skill 使用说明](skills/video-transcription/SKILL.md)，包括：

- 元宝：登录 → 右键“检查” → Network → list → Request Headers → Cookie；没有 list 时先给元宝发几句话。
- MiMo：登录 [Xiaomi MiMo API 开放平台](https://platform.xiaomimimo.com/) → 控制台 → API Keys。

不把个人 Key、Cookie、配置或生成的文稿加入开源仓库。

## 手动安装

在可交互终端执行：

```text
python skills/video-transcription/scripts/setup.py --with-yuanbao
python skills/video-transcription/scripts/run.py "视频链接" --output "文稿.html"
```

使用其他目录时，安装命令加 `--install-dir "安装目录"`。重跑安装会保留配置。后台安装前先在该目录准备 `config.env`，然后加 `--non-interactive`。

## 发布与维护

公开发布时需包含整个 `skills/video-transcription` 目录；不能只发 SKILL.md。仓库尚未发布前，不能把计划中的 GitHub 地址当作可用安装链接。

根目录的 `transcribe.py` 和 `app/` 是开发源文件。修改后执行 `python scripts/package_skill.py` 更新 Skill 中的 runtime，再测试完整安装包。不要发布 `installation.json`、虚拟环境或个人配置。

## 验证范围

2026-09-09，在 Windows 上从已安装的 Skill 入口实测：自动安装依赖和 FFmpeg → 使用个人元宝 Cookie 解析视频号 → 提取音频 → 使用个人 MiMo Key 转写 → 生成非空文稿，全部成功。也已验证重复安装会保留配置。

2026-09-09，补充实测用户提供的小红书和抖音链接：无需额外 Cookie，均成功解析、提取音频、调用 MiMo，并生成包含作者、互动数据和下载链接的 HTML。当前固定仅输出 HTML。

2026-09-09，快手分享链接也完成真实转写测试：修正动态分享页子域名识别后，无额外 Cookie 成功解析、提取音频、调用 MiMo 并生成 HTML，包含作者和平台返回的播放、点赞、评论等数据。

四个平台各有真实链接在 Windows 上测试成功；这不代表所有作品均可访问。macOS 和 WorkBuddy 尚未实测，平台接口和登录有效期也可能变化。

## 许可

MIT，保留原作者版权和许可文本。直接来源、原项目列明的三个参考仓库及依赖许可见 [来源与第三方说明](THIRD_PARTY_NOTICES.md)。

## 使用边界

每位用户使用自己的本地安装目录、MiMo 账号和 Cookie，不连接作者部署的服务。MiMo 转写会消耗该用户的 API 额度；本地配置不上传到本仓库。Cookie 到期后需重新获取。

支持的是可访问的视频分享链接，图文笔记、直播或需要额外权限的内容不保证可用。单次压缩音频上限 22 MiB，提取最长 480 秒、MiMo 请求最长 600 秒。平台调整页面或限制访问时可能失败；AI 转写也可能有错字，应结合原视频校对。

HTML 默认不覆盖已有文件。下载地址可能过期，部分平台的直链需要特定来源或登录态；文档会提示。平台返回的数据只是获取时的快照，并不保证包含所有指标。
