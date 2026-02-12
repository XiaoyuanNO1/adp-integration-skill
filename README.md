# ADP Integration Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 与腾讯云 ADP (AI Dialog Platform) 平台进行 HTTP SSE 流式对话对接的 AI Agent Skill

---

## 📋 简介

本 Skill 提供了与腾讯云 ADP 平台的完整对接能力，支持：

- ✅ HTTP SSE（Server-Sent Events）流式对话
- ✅ 多轮对话上下文管理
- ✅ 自定义角色指令
- ✅ 流式和非流式两种模式
- ✅ 完整的事件处理和错误处理

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 基本使用

```python
from adp_client import create_client

# 创建客户端（需要提供 ADP AppKey）
client = create_client(app_key="YOUR_APP_KEY")

# 发送消息并获取回复
response = client.chat("你好，请介绍一下自己")
print(response)

# 关闭连接
client.close()
```

### 3. 流式对话

```python
# 实时接收 AI 回复
for event in client.chat_stream("讲一个有趣的故事"):
    if event.event_type == "reply":
        print(event.reply_content, end="", flush=True)
```

### 4. 多轮对话

```python
# 自动保持上下文
client.chat("我今年25岁")
response = client.chat("我多大了？")  # AI 会记住之前的信息
print(response)
```

---

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | Knot 平台 Skill 定义文件（符合 AgentSkills 规范） |
| `adp_client.py` | 核心客户端库（12KB） |
| `README.md` | 本文档 - 使用指南 |
| `KNOT_PACKAGE_GUIDE.md` | Knot 平台打包和上传指南 |

---

## 📦 在 Knot 平台使用

### 上传 Skill

1. **打包 Skill**

```bash
# 克隆仓库
git clone https://github.com/XiaoyuanNO1/adp-integration-skill.git
cd adp-integration-skill

# 创建符合 Knot 规范的文件夹
mkdir adp-integration
cp SKILL.md adp-integration/
cp adp_client.py adp-integration/
cp README.md adp-integration/

# 打包（确保顶层文件夹名为 adp-integration）
zip -r adp-integration.zip adp-integration/
```

2. **上传到 Knot**
   - 访问：https://knot.woa.com
   - 进入 Skills 管理
   - 上传 `adp-integration.zip`

详细说明请参考 [KNOT_PACKAGE_GUIDE.md](./KNOT_PACKAGE_GUIDE.md)

---

## 🎯 核心功能

### 简单对话

```python
from adp_client import create_client

client = create_client(app_key="YOUR_KEY")
response = client.chat("什么是人工智能？")
print(response)
client.close()
```

### 自定义角色

```python
# 设置专业角色
client.set_system_role("你是一个金融专家，擅长投资理财建议")
response = client.chat("如何开始投资？")
print(response)
```

### 会话管理

```python
# 为不同用户使用不同的会话 ID
client = create_client(
    app_key="YOUR_KEY",
    session_id=f"user_{user_id}",
    visitor_biz_id=user_id
)
```

---

## 📚 API 文档

### `create_client()`

创建 ADP 客户端实例。

**参数**：
- `app_key` (str, 必需) - ADP 应用密钥
- `session_id` (str, 可选) - 会话 ID
- `visitor_biz_id` (str, 可选) - 访客业务 ID
- `streaming_throttle` (int, 可选) - 流式回复频率，默认 5
- `incremental` (bool, 可选) - 是否增量输出，默认 False
- `model_name` (str, 可选) - 指定模型名称
- `custom_variables` (dict, 可选) - 自定义参数

**返回**：`ADPClient` 实例

### `chat(message, request_id=None)`

发送消息并获取完整回复。

**参数**：
- `message` (str) - 消息内容
- `request_id` (str, 可选) - 请求 ID

**返回**：str - AI 的完整回复

### `chat_stream(message, request_id=None)`

发送消息并获取流式回复。

**参数**：
- `message` (str) - 消息内容
- `request_id` (str, 可选) - 请求 ID

**返回**：Iterator[ChatMessage] - 事件流迭代器

### `set_system_role(role)`

设置系统角色指令。

**参数**：
- `role` (str) - 角色描述

### `close()`

关闭客户端连接，释放资源。

---

## 🔐 安全建议

1. **保护密钥**：不要在代码中硬编码 AppKey

```python
import os
app_key = os.environ.get("ADP_APP_KEY")
client = create_client(app_key=app_key)
```

2. **会话隔离**：不同用户使用不同的 session_id

3. **资源管理**：始终使用 try-finally 确保连接关闭

```python
try:
    client = create_client(app_key=app_key)
    response = client.chat("你好")
    print(response)
finally:
    client.close()
```

---

## 🛠️ 故障排查

### 连接失败

- 检查网络连接
- 验证 AppKey 是否正确
- 确认 ADP 服务是否正常

### 回复为空

- 检查是否收到 error 事件
- 确认机器人配置是否正确
- 查看是否命中敏感词（`is_evil=True`）

### 中文乱码

```bash
export PYTHONIOENCODING=utf-8
export LANG=zh_CN.UTF-8
```

---

## 📖 参考资源

- **ADP 官方文档**：https://www.tencentcloud.com/zh/document/product/1254/69979
- **Skill 详细文档**：[SKILL.md](./SKILL.md)
- **Knot 平台**：https://knot.woa.com
- **打包指南**：[KNOT_PACKAGE_GUIDE.md](./KNOT_PACKAGE_GUIDE.md)

---

## 📝 版本历史

### v1.0.0 (2026-02-12)

- ✅ 实现 HTTP SSE 协议对接
- ✅ 支持简单对话和流式对话
- ✅ 实现多轮对话上下文管理
- ✅ 支持自定义角色指令
- ✅ 完整的事件处理和错误处理

---

## 📄 许可证

MIT License - 详见 [LICENSE](./LICENSE) 文件

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**Made with ❤️ for AI Agents**
