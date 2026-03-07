<div align="center">
  <img src="nanobot_logo.png" alt="nanobot" width="500">
  <h1>nanobot: 超轻量级个人 AI 助手</h1>
  <p>
    <a href="https://pypi.org/project/nanobot-ai/"><img src="https://img.shields.io/pypi/v/nanobot-ai" alt="PyPI"></a>
    <a href="https://pepy.tech/project/nanobot-ai"><img src="https://static.pepy.tech/badge/nanobot-ai" alt="Downloads"></a>
    <img src="https://img.shields.io/badge/python-≥3.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
    <a href="./COMMUNICATION.md"><img src="https://img.shields.io/badge/Feishu-Group-E9DBFC?style=flat&logo=feishu&logoColor=white" alt="Feishu"></a>
    <a href="./COMMUNICATION.md"><img src="https://img.shields.io/badge/WeChat-Group-C5EAB4?style=flat&logo=wechat&logoColor=white" alt="WeChat"></a>
    <a href="https://discord.gg/MnCvHqpUGB"><img src="https://img.shields.io/badge/Discord-Community-5865F2?style=flat&logo=discord&logoColor=white" alt="Discord"></a>
  </p>
</div>

🐈 **nanobot** 是一个受 [OpenClaw](https://github.com/openclaw/openclaw) 启发的**超轻量级**个人 AI 助手

⚡️ 仅用 **~4,000** 行代码就实现了核心 agent 功能 — 比 Clawdbot 的 430k+ 行代码**小 99%**。

📏 实时代码行数：**3,922 行**（随时运行 `bash core_agent_lines.sh` 验证）

## 📢 功能更新日志

- **2026-03-07** 🔒 新增生产环境安全加固 — Python 脚本白名单、Shell 命令黑名单、文件操作安全、完整审计日志
- **2026-03-06** ✨ 新增 ledger-validation 技能（分录明细账校验）和 JSON 模式支持
- **2026-02-24** 🚀 发布 **v0.1.4.post2** — 专注于可靠性的版本，重新设计了心跳机制、优化了提示缓存，并加强了 provider 和 channel 的稳定性。详见 [发布说明](https://github.com/HKUDS/nanobot/releases/tag/v0.1.4.post2)。
- **2026-02-23** 🔧 虚拟工具调用心跳、提示缓存优化、Slack mrkdwn 修复。
- **2026-02-22** 🛡️ Slack 线程隔离、Discord 输入修复、agent 可靠性改进。
- **2026-02-21** 🎉 发布 **v0.1.4.post1** — 新的 provider、跨渠道媒体支持和重大稳定性改进。详见 [发布说明](https://github.com/HKUDS/nanobot/releases/tag/v0.1.4.post1)。
- **2026-02-20** 🐦 飞书现在可以从用户接收多模态文件。底层内存更可靠。
- **2026-02-19** ✨ Slack 现在可以发送文件、Discord 分割长消息、subagent 在 CLI 模式下工作。
- **2026-02-18** ⚡️ nanobot 现在支持 VolcEngine、MCP 自定义认证头和 Anthropic 提示缓存。
- **2026-02-17** 🎉 发布 **v0.1.4** — MCP 支持、进度流式传输、新的 provider 和多个渠道改进。请查看 [发布说明](https://github.com/HKUDS/nanobot/releases/tag/v0.1.4)。
- **2026-02-16** 🦞 nanobot 现在集成了 [ClawHub](https://clawhub.ai) 技能 — 搜索和安装公共 agent 技能。
- **2026-02-15** 🔑 nanobot 现在支持通过 OAuth 登录的 OpenAI Codex provider。
- **2026-02-14** 🔌 nanobot 现在支持 MCP！详见 [MCP 章节](#mcp-model-context-protocol)。
- **2026-02-13** 🎉 发布 **v0.1.3.post7** — 包含安全加固和多项改进。**请升级到最新版本以解决安全问题**。详见 [发布说明](https://github.com/HKUDS/nanobot/releases/tag/v0.1.3.post7)。
- **2026-02-12** 🧠 重新设计内存系统 — 代码更少、更可靠。加入 [讨论](https://github.com/HKUDS/nanobot/discussions/566)！
- **2026-02-11** ✨ 增强的 CLI 体验和新增 MiniMax 支持！

<details>
<summary>更早的新闻</summary>

- **2026-02-10** 🎉 发布 **v0.1.3.post6** 带来改进！查看更新 [说明](https://github.com/HKUDS/nanobot/releases/tag/v0.1.3.post6) 和我们的 [路线图](https://github.com/HKUDS/nanobot/discussions/431)。
- **2026-02-09** 💬 新增 Slack、Email 和 QQ 支持 — nanobot 现在支持多个聊天平台！
- **2026-02-08** 🔧 重构 Providers — 添加新的 LLM provider 现在只需 2 个简单步骤！查看 [这里](#providers)。
- **2026-02-07** 🚀 发布 **v0.1.3.post5** 支持 Qwen 和多项关键改进！查看 [这里](https://github.com/HKUDS/nanobot/releases/tag/v0.1.3.post5)。
- **2026-02-06** ✨ 新增 Moonshot/Kimi provider、Discord 集成和增强的安全加固！
- **2026-02-05** ✨ 新增飞书渠道、DeepSeek provider 和增强的定时任务支持！
- **2026-02-04** 🚀 发布 **v0.1.3.post4** 支持多 provider 和 Docker！查看 [这里](https://github.com/HKUDS/nanobot/releases/tag/v0.1.3.post4)。
- **2026-02-03** ⚡ 集成 vLLM 用于本地 LLM 支持和改进的自然语言任务调度！
- **2026-02-02** 🎉 nanobot 正式发布！欢迎尝试 🐈 nanobot！

</details>

## nanobot 的核心特性：

🪶 **超轻量级**：仅约 4,000 行核心 agent 代码 — 比 Clawdbot 小 99%。

🔬 **研究友好**：代码干净、易读，易于理解、修改和扩展以进行研究。

⚡️ **闪电般快速**：最小化占用意味着更快的启动、更低的资源使用和更快的迭代。

💎 **易于使用**：一键部署，即可开始使用。

## 🏗️ 架构

<p align="center">
  <img src="nanobot_arch.png" alt="nanobot architecture" width="800">
</p>

## ✨ 功能特性

<table align="center">
  <tr align="center">
    <th><p align="center">📈 24/7 实时市场分析</p></th>
    <th><p align="center">🚀 全栈软件工程师</p></th>
    <th><p align="center">📅 智能日常事务管理</p></th>
    <th><p align="center">📚 个人知识助手</p></th>
  </tr>
  <tr>
    <td align="center"><p align="center"><img src="case/search.gif" width="180" height="400"></p></td>
    <td align="center"><p align="center"><img src="case/code.gif" width="180" height="400"></p></td>
    <td align="center"><p align="center"><img src="case/scedule.gif" width="180" height="400"></p></td>
    <td align="center"><p align="center"><img src="case/memory.gif" width="180" height="400"></p></td>
  </tr>
  <tr>
    <td align="center">发现 • 洞察 • 趋势</td>
    <td align="center">开发 • 部署 • 扩展</td>
    <td align="center">调度 • 自动化 • 组织</td>
    <td align="center">学习 • 记忆 • 推理</td>
  </tr>
</table>

## 📦 安装

**从源码安装**（最新功能，推荐用于开发）

```bash
git clone https://github.com/HKUDS/nanobot.git
cd nanobot
pip install -e .
```

**使用 [uv](https://github.com/astral-sh/uv) 安装**（稳定、快速）

```bash
uv tool install nanobot-ai
```

**从 PyPI 安装**（稳定版）

```bash
pip install nanobot-ai
```

## 🚀 快速开始

> [!TIP]
> 在 `~/.nanobot/config.json` 中设置你的 API 密钥。
> 获取 API 密钥：[OpenRouter](https://openrouter.ai/keys)（全球）· [Brave Search](https://brave.com/search/api/)（可选，用于网络搜索）

**1. 初始化**

```bash
nanobot onboard
```

**2. 配置**（`~/.nanobot/config.json`）

添加或合并这**两部分**到你的配置（其他选项有默认值）。

*设置你的 API 密钥*（例如 OpenRouter，推荐给全球用户）：
```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    }
  }
}
```

*设置你的模型*（可选地固定一个 provider — 默认自动检测）：
```json
{
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5",
      "provider": "openrouter"
    }
  }
}
```

**3. 聊天**

```bash
nanobot agent
```

就这样！你在 2 分钟内就拥有了一个可用的 AI 助手。

## 💬 聊天应用

将 nanobot 连接到你最喜欢的聊天平台。

| Channel | 你需要什么 |
|---------|---------------|
| **Telegram** | 来自 @BotFather 的 Bot token |
| **Discord** | Bot token + 消息内容 intent |
| **WhatsApp** | 二维码扫描 |
| **Feishu** | App ID + App Secret |
| **Mochat** | Claw token（可自动设置）|
| **DingTalk** | App Key + App Secret |
| **Slack** | Bot token + 应用级 token |
| **Email** | IMAP/SMTP 凭证 |
| **QQ** | App ID + App Secret |

<details>
<summary><b>Telegram</b>（推荐）</summary>

**1. 创建 bot**
- 打开 Telegram，搜索 `@BotFather`
- 发送 `/newbot`，按照提示操作
- 复制 token

**2. 配置**

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
```

> 你可以在 Telegram 设置中找到你的 **User ID**。它显示为 `@yourUserId`。
> 复制此值**不要带 `@` 符号**并粘贴到配置文件中。

**3. 运行**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>Mochat (Claw IM)</b></summary>

默认使用 **Socket.IO WebSocket**，支持 HTTP 轮询回退。

**1. 让 nanobot 为你设置 Mochat**

只需向 nanobot 发送此消息（将 `xxx@xxx` 替换为你的真实邮箱）：
```
Read https://raw.githubusercontent.com/HKUDS/MoChat/refs/heads/main/skills/nanobot/skill.md and register on MoChat. My Email account is xxx@xxx Bind me as your owner and DM me on MoChat.
```

nanobot 将自动注册、配置 `~/.nanobot/config.json` 并连接到 Mochat。

**2. 重启网关**

```bash
nanobot gateway
```

就这样 — nanobot 会处理其余部分！

<br>

<details>
<summary>手动配置（高级）</summary>
如果你更喜欢手动配置，将以下内容添加到 `~/.nanobot/config.json`：

> 保持 `claw_token` 私密。它应该只通过 `X-Claw-Token` 头发送到你的 Mochat API 端点。

```json
{
  "channels": {
    "mochat": {
      "enabled": true,
      "base_url": "https://mochat.io",
      "socket_url": "https://mochat.io",
      "socket_path": "/socket.io",
      "claw_token": "claw_xxx",
      "agent_user_id": "6982abcdef",
      "sessions": ["*"],
      "panels": ["*"],
      "reply_delay_mode": "non-mention",
      "reply_delay_ms": 120000
    }
  }
}
```


</details>

</details>

<details>
<summary><b>Discord</b></summary>

**1. 创建 bot**
- 访问 https://discord.com/developers/applications
- 创建应用 → Bot → 添加 Bot
- 复制 bot token

**2. 启用 intents**
- 在 Bot 设置中，启用 **MESSAGE CONTENT INTENT**
- （可选）如果你计划使用基于成员数据的允许列表，启用 **SERVER MEMBERS INTENT**

**3. 获取你的 User ID**
- Discord 设置 → 高级 → 启用 **开发者模式**
- 右键点击你的头像 → **复制 User ID**

**4. 配置**

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
```

**5. 邀请 bot**
- OAuth2 → URL 生成器
- Scopes: `bot`
- Bot 权限：`发送消息`、`读取消息历史`
- 打开生成的邀请 URL 并将 bot 添加到你的服务器

**6. 运行**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>Matrix (Element)</b></summary>

首先安装 Matrix 依赖：

```bash
pip install nanobot-ai[matrix]
```

**1. 创建/选择 Matrix 账户**

- 在你的主服务器上创建或重用 Matrix 账户（例如 `matrix.org`）。
- 确认你可以使用 Element 登录。

**2. 获取凭据**

- 你需要：
  - `userId`（例如：`@nanobot:matrix.org`）
  - `accessToken`
  - `deviceId`（推荐，以便跨重启恢复同步令牌）
- 你可以从主服务器登录 API（`/_matrix/client/v3/login`）或从客户端的高级会话设置中获取这些信息。

**3. 配置**

```json
{
  "channels": {
    "matrix": {
      "enabled": true,
      "homeserver": "https://matrix.org",
      "userId": "@nanobot:matrix.org",
      "accessToken": "syt_xxx",
      "deviceId": "NANOBOT01",
      "e2eeEnabled": true,
      "allowFrom": [],
      "groupPolicy": "open",
      "groupAllowFrom": [],
      "allowRoomMentions": false,
      "maxMediaBytes": 20971520
    }
  }
}
```

> 保持持久的 `matrix-store` 和稳定的 `deviceId` — 如果这些在重启之间更改，加密会话状态将丢失。

| 选项 | 描述 |
|--------|-------------|
| `allowFrom` | 允许交互的用户 ID。空 = 所有发送者。 |
| `groupPolicy` | `open`（默认）、`mention` 或 `allowlist`。 |
| `groupAllowFrom` | 房间允许列表（当策略为 `allowlist` 时使用）。 |
| `allowRoomMentions` | 在提及模式下接受 `@room` 提及。 |
| `e2eeEnabled` | E2EE 支持（默认 `true`）。设置为 `false` 以仅使用明文。 |
| `maxMediaBytes` | 最大附件大小（默认 `20MB`）。设置为 `0` 以阻止所有媒体。 |


**4. 运行**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>WhatsApp</b></summary>

需要 **Node.js ≥18**。

**1. 链接设备**

```bash
nanobot channels login
# 使用 WhatsApp → 设置 → 关联设备扫描二维码
```

**2. 配置**

```json
{
  "channels": {
    "whatsapp": {
      "enabled": true,
      "allowFrom": ["+1234567890"]
    }
  }
}
```

**3. 运行**（两个终端）

```bash
# 终端 1
nanobot channels login

# 终端 2
nanobot gateway
```

</details>

<details>
<summary><b>Feishu (飞书)</b></summary>

使用 **WebSocket** 长连接 — 不需要公网 IP。

**1. 创建飞书 bot**
- 访问 [飞书开放平台](https://open.feishu.cn/app)
- 创建新应用 → 启用 **Bot** 能力
- **权限**：添加 `im:message`（发送消息）
- **事件**：添加 `im.message.receive_v1`（接收消息）
  - 选择 **长连接** 模式（需要先运行 nanobot 以建立连接）
- 从"凭据与基础信息"中获取 **App ID** 和 **App Secret**
- 发布应用

**2. 配置**

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxx",
      "appSecret": "xxx",
      "encryptKey": "",
      "verificationToken": "",
      "allowFrom": []
    }
  }
}
```

> `encryptKey` 和 `verificationToken` 对于长连接模式是可选的。
> `allowFrom`：留空以允许所有用户，或添加 `["ou_xxx"]` 以限制访问。

**3. 运行**

```bash
nanobot gateway
```

> [!TIP]
> 飞书使用 WebSocket 接收消息 — 不需要 webhook 或公网 IP！
</details>

<details>
<summary><b>QQ (QQ单聊)</b></summary>

使用 **botpy SDK** 和 WebSocket — 不需要公网 IP。目前仅支持**私聊**。

**1. 注册并创建 bot**
- 访问 [QQ 开放平台](https://q.qq.com) → 注册为开发者（个人或企业）
- 创建新的 bot 应用
- 进入 **开发设置** → 复制 **AppID** 和 **AppSecret**

**2. 设置沙箱进行测试**

- 在 bot 管理控制台中，找到 **沙箱配置**
- 在 **在消息列表配置** 下，点击 **添加成员** 并添加你自己的 QQ 号
- 添加后，使用移动 QQ 扫描 bot 的二维码 → 打开 bot 个人资料 → 点击"发消息"开始聊天

**3. 配置**

> - `allowFrom`：留空以进行公开访问，或添加用户 openid 以限制。你可以在 nanobot 日志中找到 openid，当用户向 bot 发送消息时。
> - 对于生产环境：在 bot 控制台中提交审核并发布。有关完整发布流程，请参阅 [QQ Bot 文档](https://bot.q.qq.com/wiki/)。

```json
{
  "channels": {
    "qq": {
      "enabled": true,
      "appId": "YOUR_APP_ID",
      "secret": "YOUR_APP_SECRET",
      "allowFrom": []
    }
  }
}
```

**4. 运行**

```bash
nanobot gateway
```

现在从 QQ 向 bot 发送消息 — 它应该会响应！
</details>

<details>
<summary><b>DingTalk (钉钉)</b></summary>

使用 **流式模式** — 不需要公网 IP。

**1. 创建钉钉 bot**
- 访问 [钉钉开放平台](https://open-dev.dingtalk.com/)
- 创建新应用 → 添加 **机器人** 能力
- **配置**：
  - 切换 **流式模式** 开启
  - **权限**：添加发送消息所需的权限
  - 从"凭据"中获取 **AppKey**（客户端 ID）和 **AppSecret**（客户端密钥）
- 发布应用

**2. 配置**

```json
{
  "channels": {
    "dingtalk": {
      "enabled": true,
      "clientId": "YOUR_APP_KEY",
      "clientSecret": "YOUR_APP_SECRET",
      "allowFrom": []
    }
  }
}
```

> `allowFrom`：留空以允许所有用户，或添加 `["staffId"]` 以限制访问。

**3. 运行**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>Slack</b></summary>

使用 **Socket 模式** — 不需要公网 URL。

**1. 创建 Slack 应用**
- 访问 [Slack API](https://api.slack.com/apps) → **创建新应用** → "从头开始"
- 选择名称和你的工作区

**2. 配置应用**
- **Socket 模式**：切换开启 → 生成具有 `connections:write` 范围的 **应用级令牌** → 复制它（`xapp-...`）
- **OAuth 和权限**：添加 bot 范围：`chat:write`、`reactions:write`、`app_mentions:read`
- **事件订阅**：切换开启 → 订阅 bot 事件：`message.im`、`message.channels`、`app_mention` → 保存更改
- **应用主页**：滚动到 **显示标签** → 启用 **消息标签** → 勾选 **"允许用户从消息标签发送斜杠命令和消息"**
- **安装应用**：点击 **安装到工作区** → 授权 → 复制 **Bot 令牌**（`xoxb-...`）

**3. 配置 nanobot**

```json
{
  "channels": {
    "slack": {
      "enabled": true,
      "botToken": "xoxb-...",
      "appToken": "xapp-...",
      "groupPolicy": "mention"
    }
  }
}
```

**4. 运行**

```bash
nanobot gateway
```

直接向 bot 发送 DM 或在频道中 @提及它 — 它应该会响应！

> [!TIP]
> - `groupPolicy`：`"mention"`（默认 — 仅在 @提及时响应）、`"open"`（响应所有频道消息）或 `"allowlist"`（限制为特定频道）。
> - DM 策略默认为开放。设置 `"dm": {"enabled": false}` 以禁用 DM。
</details>

<details>
<summary><b>Email</b></summary>

给 nanobot 它自己的邮箱账户。它轮询 **IMAP** 以接收邮件并通过 **SMTP** 回复 — 就像一个个人邮件助手。

**1. 获取凭据（Gmail 示例）**
- 为你的 bot 创建一个专用的 Gmail 账户（例如 `my-nanobot@gmail.com`）
- 启用两步验证 → 创建一个 [应用密码](https://myaccount.google.com/apppasswords)
- 对 IMAP 和 SMTP 都使用此应用密码

**2. 配置**

> - `consentGranted` 必须为 `true` 才能允许邮箱访问。这是一个安全门 — 设置 `false` 以完全禁用。
> - `allowFrom`：留空以接受来自任何人的邮件，或限制为特定发送者。
> - `smtpUseTls` 和 `smtpUseSsl` 默认为 `true` / `false`，这对于 Gmail（端口 587 + STARTTLS）是正确的。无需显式设置它们。
> - 如果你只想读取/分析邮件而不发送自动回复，设置 `"autoReplyEnabled": false`。

```json
{
  "channels": {
    "email": {
      "enabled": true,
      "consentGranted": true,
      "imapHost": "imap.gmail.com",
      "imapPort": 993,
      "imapUsername": "my-nanobot@gmail.com",
      "imapPassword": "your-app-password",
      "smtpHost": "smtp.gmail.com",
      "smtpPort": 587,
      "smtpUsername": "my-nanobot@gmail.com",
      "smtpPassword": "your-app-password",
      "fromAddress": "my-nanobot@gmail.com",
      "allowFrom": ["your-real-email@gmail.com"]
    }
  }
}
```

**3. 运行**

```bash
nanobot gateway
```

</details>

## 🌐 Agent 社交网络

🐈 nanobot 能够链接到 agent 社交网络（agent 社区）。**只需发送一条消息，你的 nanobot 就会自动加入！**

| 平台 | 如何加入（向你的 bot 发送此消息） |
|----------|-------------|
| [**Moltbook**](https://www.moltbook.com/) | `Read https://moltbook.com/skill.md and follow the instructions to join Moltbook` |
| [**ClawdChat**](https://clawdchat.ai/) | `Read https://clawdchat.ai/skill.md and follow the instructions to join ClawdChat` |

只需将上面的命令发送给你的 nanobot（通过 CLI 或任何聊天频道），它将处理其余部分。

## ⚙️ 配置

配置文件：`~/.nanobot/config.json`

### Providers

> [!TIP]
> - **Groq** 通过 Whisper 提供免费的语音转录。如果配置了，Telegram 语音消息将自动转录。
> - **Zhipu Coding Plan**：如果你使用的是智谱的编码计划，在你的 zhipu provider 配置中设置 `"apiBase": "https://open.bigmodel.cn/api/coding/paas/v4"`。
> - **MiniMax (中国大陆)**：如果你的 API 密钥来自 MiniMax 的中国大陆平台（minimaxi.com），在你的 minimax provider 配置中设置 `"apiBase": "https://api.minimaxi.com/v1"`。
> - **VolcEngine Coding Plan**：如果你使用的是火山引擎的编码计划，在你的 volcengine provider 配置中设置 `"apiBase": "https://ark.cn-beijing.volces.com/api/coding/v3"`。

| Provider | 用途 | 获取 API 密钥 |
|----------|---------|-------------|
| `custom` | 任何 OpenAI 兼容的端点（直接，无 LiteLLM） | — |
| `openrouter` | LLM（推荐，访问所有模型） | [openrouter.ai](https://openrouter.ai) |
| `anthropic` | LLM（Claude 直接） | [console.anthropic.com](https://console.anthropic.com) |
| `openai` | LLM（GPT 直接） | [platform.openai.com](https://platform.openai.com) |
| `deepseek` | LLM（DeepSeek 直接） | [platform.deepseek.com](https://platform.deepseek.com) |
| `groq` | LLM + **语音转录**（Whisper） | [console.groq.com](https://console.groq.com) |
| `gemini` | LLM（Gemini 直接） | [aistudio.google.com](https://aistudio.google.com) |
| `minimax` | LLM（MiniMax 直接） | [platform.minimaxi.com](https://platform.minimaxi.com) |
| `aihubmix` | LLM（API 网关，访问所有模型） | [aihubmix.com](https://aihubmix.com) |
| `siliconflow` | LLM（SiliconFlow/硅基流动） | [siliconflow.cn](https://siliconflow.cn) |
| `volcengine` | LLM（VolcEngine/火山引擎） | [volcengine.com](https://www.volcengine.com) |
| `dashscope` | LLM（Qwen） | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com) |
| `moonshot` | LLM（Moonshot/Kimi） | [platform.moonshot.cn](https://platform.moonshot.cn) |
| `zhipu` | LLM（Zhipu GLM） | [open.bigmodel.cn](https://open.bigmodel.cn) |
| `vllm` | LLM（本地，任何 OpenAI 兼容的服务器） | — |
| `openai_codex` | LLM（Codex，OAuth） | `nanobot provider login openai-codex` |
| `github_copilot` | LLM（GitHub Copilot，OAuth） | `nanobot provider login github-copilot` |

<details>
<summary><b>OpenAI Codex (OAuth)</b></summary>

Codex 使用 OAuth 而不是 API 密钥。需要 ChatGPT Plus 或 Pro 账户。

**1. 登录：**
```bash
nanobot provider login openai-codex
```

**2. 设置模型**（合并到 `~/.nanobot/config.json`）：
```json
{
  "agents": {
    "defaults": {
      "model": "openai-codex/gpt-5.1-codex"
    }
  }
}
```

**3. 聊天：**
```bash
nanobot agent -m "Hello!"
```

> Docker 用户：使用 `docker run -it` 进行交互式 OAuth 登录。
</details>

<details>
<summary><b>自定义 Provider（任何 OpenAI 兼容的 API）</b></summary>

直接连接到任何 OpenAI 兼容的端点 — LM Studio、llama.cpp、Together AI、Fireworks、Azure OpenAI 或任何自托管的服务器。绕过 LiteLLM；模型名称按原样传递。
```json
{
  "providers": {
    "custom": {
      "apiKey": "your-api-key",
      "apiBase": "https://api.your-provider.com/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "your-model-name"
    }
  }
}
```

> 对于不需要密钥的本地服务器，将 `apiKey` 设置为任何非空字符串（例如 `"no-key"`）。
</details>

<details>
<summary><b>vLLM（本地 / OpenAI 兼容）</b></summary>

使用 vLLM 或任何 OpenAI 兼容的服务器运行你自己的模型，然后添加到配置：

**1. 启动服务器**（示例）：
```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct --port 8000
```

**2. 添加到配置**（部分 — 合并到 `~/.nanobot/config.json`）：

*Provider（密钥可以是任何非空字符串，用于本地）：*
```json
{
  "providers": {
    "vllm": {
      "apiKey": "dummy",
      "apiBase": "http://localhost:8000/v1"
    }
  }
}
```

*Model:*
```json
{
  "agents": {
    "defaults": {
      "model": "meta-llama/Llama-3.1-8B-Instruct"
    }
  }
}
```

</details>

<details>
<summary><b>添加新的 Provider（开发者指南）</b></summary>

nanobot 使用 **Provider Registry**（`nanobot/providers/registry.py`）作为单一事实来源。
添加新的 provider 只需 **2 个步骤** — 无需触及 if-elif 链。

**步骤 1.** 将 `ProviderSpec` 条目添加到 `PROVIDERS` 中的 `nanobot/providers/registry.py`：

```python
ProviderSpec(
    name="myprovider",                   # config 字段名称
    keywords=("myprovider", "mymodel"),  # 模型名称关键字用于自动匹配
    env_key="MYPROVIDER_API_KEY",        # LiteLLM 的环境变量
    display_name="My Provider",          # 在 `nanobot status` 中显示
    litellm_prefix="myprovider",         # 自动前缀：model → myprovider/model
    skip_prefixes=("myprovider/",),      # 不要双重前缀
)
```

**步骤 2.** 将字段添加到 `nanobot/config/schema.py` 中的 `ProvidersConfig`：

```python
class ProvidersConfig(BaseModel):
    ...
    myprovider: ProviderConfig = ProviderConfig()
```

就这样！环境变量、模型前缀、配置匹配和 `nanobot status` 显示都将自动工作。

**常见的 `ProviderSpec` 选项：**

| 字段 | 描述 | 示例 |
|-------|-------------|---------|
| `litellm_prefix` | 为 LiteLLM 自动前缀模型名称 | `"dashscope"` → `dashscope/qwen-max` |
| `skip_prefixes` | 如果模型已经以这些开头，则不要前缀 | `("dashscope/", "openrouter/")` |
| `env_extras` | 要设置的其他环境变量 | `(("ZHIPUAI_API_KEY", "{api_key}"),)` |
| `model_overrides` | 每模型参数覆盖 | `(("kimi-k2.5", {"temperature": 1.0}),)` |
| `is_gateway` | 可以路由任何模型（如 OpenRouter） | `True` |
| `detect_by_key_prefix` | 通过 API 密钥前缀检测网关 | `"sk-or-"` |
| `detect_by_base_keyword` | 通过 API 基本 URL 检测网关 | `"openrouter"` |
| `strip_model_prefix` | 在重新前缀之前剥离现有前缀 | `True`（用于 AiHubMix） |
</details>

### MCP (Model Context Protocol)

> [!TIP]
> 配置格式与 Claude Desktop / Cursor 兼容。你可以直接从任何 MCP 服务器的 README 复制 MCP 服务器配置。
nanobot 支持 [MCP](https://modelcontextprotocol.io/) — 连接外部工具服务器并将它们用作原生 agent 工具。

将 MCP 服务器添加到你的 `config.json`：

```json
{
  "tools": {
    "mcpServers": {
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
      },
      "my-remote-mcp": {
        "url": "https://example.com/mcp/",
        "headers": {
          "Authorization": "Bearer xxxxx"
        }
      }
    }
  }
}
```

支持两种传输模式：

| 模式 | 配置 | 示例 |
|------|--------|---------|
| **Stdio** | `command` + `args` | 通过 `npx` / `uvx` 的本地进程 |
| **HTTP** | `url` + `headers`（可选） | 远程端点（`https://mcp.example.com/sse`） |

使用 `toolTimeout` 覆盖慢服务器的默认 30s 每次调用超时：

```json
{
  "tools": {
    "mcpServers": {
      "my-slow-server": {
        "url": "https://example.com/mcp/",
        "toolTimeout": 120
      }
    }
  }
}
```

MCP 工具在启动时自动发现和注册。LLM 可以将它们与内置工具一起使用 — 无需额外配置。

## 🔒 生产环境安全

> [!TIP]
> nanobot 现在支持**生产环境安全加固**，确保系统安全运行。

### 安全配置选项

| 选项 | 默认 | 描述 |
|--------|---------|-------------|
| `agents.security.level` | `strict` | 安全级别：`basic`（开发）、`strict`（生产）、`readonly`（最高安全） |
| `agents.security.enable_audit_log` | `true` | 启用审计日志记录所有操作 |
| `agents.security.audit_log_dir` | `audit` | 审计日志存储目录 |
| `tools.restrictToWorkspace` | `false` | 当为 `true` 时，将**所有** agent 工具（shell、文件读/写/编辑、列表）限制为工作区目录。防止路径遍历和超出范围的访问。 |
| `tools.exec.pathAppend` | `""` | 运行 shell 命令时要附加到 `PATH` 的额外目录（例如，用于 `ufw` 的 `/usr/sbin`）。 |
| `channels.*.allowFrom` | `[]`（允许所有） | 用户 ID 白名单。空 = 允许所有人；非空 = 只有列出的用户可以交互。 |

### 安全级别说明

- **basic（基础模式）**：开发环境使用，允许执行 skill 中定义的命令，基础的危险命令黑名单
- **strict（严格模式）**：生产环境推荐，只允许执行 skill 中明确定义的 Python 脚本，严格的删除/更新操作黑名单，完整的审计日志，工作空间限制
- **readonly（只读模式）**：最高安全级别，禁止所有写入操作，只允许读取和查询操作

### 安全特性

✅ **Python 脚本白名单**：只能执行在 skills 中明确定义的 Python 脚本
✅ **Shell 命令黑名单**：禁止执行删除、格式化、包安装等危险操作
✅ **文件操作安全**：工作空间限制和系统目录保护
✅ **完整审计日志**：所有命令执行和文件操作都被记录
✅ **审计日志查询**：使用 `audit_log` 工具查询安全违规和操作记录

### 配置示例

**生产环境（推荐）：**
```json
{
  "agents": {
    "security": {
      "level": "strict",
      "enable_audit_log": true,
      "audit_log_dir": "audit"
    }
  }
}
```

**高安全环境：**
```json
{
  "agents": {
    "security": {
      "level": "readonly",
      "enable_audit_log": true,
      "audit_log_dir": "audit"
    }
  }
}
```

### 审计日志查询

```bash
# 查询安全违规
nanobot agent -m "查询安全违规: audit_log(query_type='violations')"

# 查询最近日志
nanobot agent -m "查询最近日志: audit_log(query_type='recent')"

# 查询所有日志
nanobot agent -m "查询所有日志: audit_log(query_type='all')"
```

### 审计日志位置

所有操作日志保存在：`~/.nanobot/workspace/audit/audit_YYYYMMDD.log`

### 安全功能详情

请查看 [SECURITY_IMPLEMENTATION_SUMMARY.md](./SECURITY_IMPLEMENTATION_SUMMARY.md) 了解完整的安全功能说明和实施细节。

## CLI 参考

| 命令 | 描述 |
|---------|-------------|
| `nanobot onboard` | 初始化配置和工作区 |
| `nanobot agent -m "..."` | 与 agent 聊天 |
| `nanobot agent` | 交互式聊天模式 |
| `nanobot agent --no-markdown` | 显示纯文本回复 |
| `nanobot agent --logs` | 在聊天期间显示运行时日志 |
| `nanobot agent --json` | 启用 JSON 模式以进行结构化输出 |
| `nanobot gateway` | 启动网关 |
| `nanobot status` | 显示状态 |
| `nanobot provider login openai-codex` | Providers 的 OAuth 登录 |
| `nanobot channels login` | 链接 WhatsApp（扫描二维码） |
| `nanobot channels status` | 显示频道状态 |

交互模式退出：`exit`、`quit`、`/exit`、`/quit`、`:q` 或 `Ctrl+D`。

<details>
<summary><b>定时任务（Cron）</b></summary>

```bash
# 添加任务
nanobot cron add --name "daily" --message "Good morning!" --cron "0 9 * * *"
nanobot cron add --name "hourly" --message "Check status" --every 3600
# 列出任务
nanobot cron list
# 移除任务
nanobot cron remove <job_id>
```

</details>

<details>
<summary><b>心跳（周期性任务）</b></summary>

网关每 30 分钟唤醒一次并检查工作区中的 `HEARTBEAT.md`（`~/.nanobot/workspace/HEARTBEAT.md`）。如果文件有任务，agent 执行它们并将结果传送到你最近活动的聊天频道。

**设置：** 编辑 `~/.nanobot/workspace/HEARTBEAT.md`（由 `nanobot onboard` 自动创建）：
```markdown
## 周期性任务

- [ ] 检查天气预报并发送摘要
- [ ] 扫描收件箱中的紧急邮件
```

agent 也可以自己管理此文件 — 询问它"添加周期性任务"，它将为你更新 `HEARTBEAT.md`。

> **注意：** 网关必须正在运行（`nanobot gateway`），并且你必须至少与 bot 聊天一次，以便它知道传送到哪个频道。
</details>

## 🐳 Docker

> [!TIP]
> `-v ~/.nanobot:/root/.nanobot` 标志将你的本地配置目录挂载到容器中，因此你的配置和工作区在容器重启之间持久化。

### Docker Compose

```bash
docker compose run --rm nanobot-cli onboard   # 首次设置
vim ~/.nanobot/config.json                     # 添加 API 密钥
docker compose up -d nanobot-gateway           # 启动网关
```

```bash
docker compose run --rm nanobot-cli agent -m "Hello!"   # 运行 CLI
docker compose logs -f nanobot-gateway                   # 查看日志
docker compose down                                      # 停止
```

### Docker

```bash
# 构建镜像
docker build -t nanobot .

# 初始化配置（仅首次）
docker run -v ~/.nanobot:/root/.nanobot --rm nanobot onboard
# 在主机上编辑配置以添加 API 密钥
vim ~/.nanobot/config.json
# 运行网关（连接到启用的频道，例如 Telegram/Discord/Mochat）
docker run -v ~/.nanobot:/root/.nanobot -p 18790:18790 nanobot gateway
# 或运行单个命令
docker run -v ~/.nanobot:/root/.nanobot --rm nanobot agent -m "Hello!"
docker run -v ~/.nanobot:/root/.nanobot --rm nanobot status
```

## 🐧 Linux 服务

将网关作为 systemd 用户服务运行，以便它自动启动并在失败时重启。

**1. 查找 nanobot 二进制路径：**

```bash
which nanobot   # 例如 /home/user/.local/bin/nanobot
```

**2. 创建服务文件** 在 `~/.config/systemd/user/nanobot-gateway.service`（如果需要，替换 `ExecStart` 路径）：
```ini
[Unit]
Description=Nanobot Gateway
After=network.target

[Service]
Type=simple
ExecStart=%h/.local/bin/nanobot gateway
Restart=always
RestartSec=10
NoNewPrivileges=yes
ProtectSystem=strict
ReadWritePaths=%h

[Install]
WantedBy=default.target
```

**3. 启用并启动：**

```bash
systemctl --user daemon-reload
systemctl --user enable --now nanobot-gateway
```

**常见操作：**
```bash
systemctl --user status nanobot-gateway        # 检查状态
systemctl --user restart nanobot-gateway       # 配置更改后重启
journalctl --user -u nanobot-gateway -f        # 跟踪日志
```

如果你自己编辑 `.service` 文件，在重启之前运行 `systemctl --user daemon-reload`。

> **注意：** 用户服务仅在你登录时运行。要在登出后保持网关运行，启用持久化：
>
> ```bash
> loginctl enable-linger $USER
> ```

## 📁 项目结构

```
nanobot/
├── agent/          # 🧠 核心 agent 逻辑
│   ├── loop.py     #    Agent 循环（LLM ↔ 工具执行）
│   ├── context.py  #    提示构建器
│   ├── memory.py   #    持久化内存
│   ├── skills.py   #    技能加载器
│   ├── subagent.py #    后台任务执行
│   └── tools/      #    内置工具（包括 spawn）
├── skills/         # 🎯 捆绑的技能（ledger-validation、github、weather、tmux...）
├── channels/       # 📱 聊天频道集成
├── bus/            # 🚌 消息路由
├── cron/           # ⏰ 定时任务
├── heartbeat/      # 💓 主动唤醒
├── providers/      # 🤖 LLM providers（OpenRouter 等）
├── session/        # 💬 会话会话
├── config/         # ⚙️ 配置
└── cli/            # 🖥️ 命令
```

## 🎯 技能

nanobot 支持可扩展的技能系统，当前包含以下内置技能：

### ledger-validation（分录明细账校验）

用于校验财务分录数据的有效性，包括金额、汇率、币种和日期的校验。

**功能特性：**
- 金额校验：确保金额非负
- 汇率校验：确保汇率大于0
- 币种校验：验证币种代码的有效性
- 日期校验：验证日期格式的正确性

**使用示例：**

通过 CLI 直接调用：
```bash
python3 nanobot/skills/ledger-validation/scripts/validate_ledger.py '{
  "applicationCode": "RMS",
  "enter_CR": 12345.67,
  "account_CR": 12345.67,
  "exchangeRateVal": 1.0,
  "exchangeDate": "2026-03-06",
  "enter_current": "RMB",
  "account_current": "CNY"
}'
```

**输出格式：**
```json
{
  "valid": true,
  "errors": [],
  "data": {
    "applicationCode": "RMS",
    "enter_CR": 12345.67,
    "account_CR": 12345.67,
    "exchangeRateVal": 1.0,
    "exchangeDate": "2026-03-06",
    "enter_current": "RMB",
    "account_current": "CNY"
  }
}
```

**支持的币种：**
RMB, CNY, USD, EUR, JPY, GBP, HKD, AUD, CAD, SGD, CHF, SEK, NZD, KRW, THB, MYR, IDR, INR, PHP, VND

## 🤝 贡献与路线图

欢迎 PR！代码库故意保持小巧和可读。🤗

**路线图** — 选择一项并 [打开 PR](https://github.com/HKUDS/nanobot/pulls)！
- [ ] **多模态** — 看到和听到（图像、语音、视频）
- [ ] **长期记忆** — 永不忘记重要上下文
- [ ] **更好的推理** — 多步规划和反思
- [ ] **更多集成** — 日历和更多
- [ ] **自我改进** — 从反馈和错误中学习

### 贡献者

<a href="https://github.com/HKUDS/nanobot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/nanobot&max=100&columns=12&updated=20260210" alt="Contributors" />
</a>

## ⭐ Star 历史

<div align="center">
  <a href="https://star-history.com/#HKUDS/nanobot&Date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HKUDS/nanobot&type=Date&theme=dark" />
      <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HKUDS/nanobot&type=Date" />
      <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HKUDS/nanobot&type=Date" style="border-radius: 15px; box-shadow: 0 0 30px rgba(0, 217, 255, 0.3);" />
    </picture>
  </a>
</div>

<p align="center">
  <em> 感谢访问 ✨ nanobot！</em><br><br>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.nanobot&style=for-the-badge&color=00d4ff" alt="Views">
</p>

<p align="center">
  <sub>nanobot 仅用于教育、研究和技术交流目的</sub>
</p>
