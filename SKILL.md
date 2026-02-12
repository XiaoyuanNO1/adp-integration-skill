---
name: adp-integration
description: 与腾讯云 ADP (AI Dialog Platform) 平台进行 HTTP SSE 流式对话对接
version: 1.0.0
author: xiaoyuan-no1-888
tags:
  - adp
  - ai-agent
  - sse
  - chat
  - integration
category: integration
---

# ADP 平台对接 Skill

## 📚 文档导航

- **[API 参考文档](./API_REFERENCE.md)** - 完整的 ADP HTTP SSE 对接 API 文档
  - 包含所有请求参数、返回事件、错误码的详细说明
  - 来源：https://www.tencentcloud.com/zh/document/product/1254/69979
  - 如需查询 API 细节，请查看此文档

---

## 📋 Skill 概述

本 Skill 提供了与腾讯云 ADP（AI Dialog Platform）平台的完整对接能力，支持通过 HTTP SSE（Server-Sent Events）协议进行流式对话交互。

**核心功能**：
- ✅ 简单对话接口
- ✅ 流式响应处理
- ✅ 多轮对话上下文管理
- ✅ 自定义角色指令
- ✅ 事件驱动架构（reply、reference、token_stat、thought、error）
- ✅ 完善的错误处理

---

## 🚀 快速开始

### 1. 基础配置

```python
from adp_client import create_client

# 创建客户端（需要提供 AppKey）
client = create_client(
    app_key="YOUR_APP_KEY",
    session_id="user_session_001",  # 可选，默认自动生成
    visitor_biz_id="user_001"        # 可选，默认自动生成
)
```

### 2. 简单对话

```python
# 发送消息并获取回复
response = client.chat("你好，请介绍一下自己")
print(response)

# 记得关闭连接
client.close()
```

### 3. 流式对话

```python
# 实时接收 AI 回复
for event in client.chat_stream("讲一个故事"):
    if event.event_type == "reply":
        print(event.reply_content, end="", flush=True)
    elif event.event_type == "token_stat":
        print(f"\n[Token 统计: {event.data}]")

client.close()
```

### 4. 多轮对话

```python
# 自动保持上下文
client.chat("我今年17岁")
response = client.chat("我可以开户炒股吗？")  # AI 会记住你的年龄
print(response)

client.close()
```

### 5. 自定义角色

```python
# 设置角色指令
client.set_system_role("你是一个专业的金融顾问，请用专业术语回答问题")
response = client.chat("什么是股票？")
print(response)

client.close()
```

---

## 📚 API 参考

### `create_client()` - 创建客户端

```python
client = create_client(
    app_key: str,                    # 必需：ADP 应用密钥
    session_id: str = None,          # 可选：会话 ID（2-64字符）
    visitor_biz_id: str = None,      # 可选：访客 ID
    streaming_throttle: int = 5,     # 可选：流式回复频率（默认5，建议≤100）
    incremental: bool = False,       # 可选：是否增量输出
    model_name: str = None,          # 可选：指定模型（如 DeepSeek-V3）
    custom_variables: dict = None    # 可选：自定义参数（工作流场景）
)
```

### `chat()` - 简单对话

```python
response = client.chat(
    message: str,              # 必需：消息内容
    request_id: str = None     # 可选：请求 ID（用于消息追踪）
) -> str
```

**返回**：完整的 AI 回复文本

### `chat_stream()` - 流式对话

```python
for event in client.chat_stream(
    message: str,              # 必需：消息内容
    request_id: str = None     # 可选：请求 ID
):
    # 处理事件
    pass
```

**返回**：`ChatMessage` 事件流（迭代器）

### `set_system_role()` - 设置角色指令

```python
client.set_system_role(role: str)
```

### `close()` - 关闭连接

```python
client.close()
```

---

## 🎯 事件类型

### ChatMessage 对象属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `event_type` | str | 事件类型：`reply`、`reference`、`token_stat`、`thought`、`error` |
| `data` | dict | 原始事件数据 |
| `reply_content` | str | 回复内容（仅 reply 事件） |
| `is_final` | bool | 是否为最终回复 |
| `record_id` | str | 消息唯一 ID |
| `is_evil` | bool | 是否命中敏感内容 |
| `reply_method` | int | 回复方式（1=大模型，2=未知问题等） |

### 事件类型说明

#### 1. `reply` - 回复事件（核心）
包含 AI 的回复内容，支持流式输出。

```python
if event.event_type == "reply":
    print(event.reply_content)
    if event.is_final:
        print("回复完成")
```

#### 2. `reference` - 参考来源事件
包含 AI 回复的参考来源信息。

```python
if event.event_type == "reference":
    print(f"参考来源: {event.data}")
```

#### 3. `token_stat` - Token 统计事件
包含 Token 使用统计信息。

```python
if event.event_type == "token_stat":
    print(f"Token 统计: {event.data}")
```

#### 4. `thought` - 思考事件（DeepSeek-R1 专属）
包含模型的思考过程（仅 DeepSeek-R1 模型）。

```python
if event.event_type == "thought":
    print(f"思考过程: {event.data}")
```

#### 5. `error` - 错误事件
包含错误信息。

```python
if event.event_type == "error":
    print(f"错误: {event.data}")
```

---

## 💡 使用场景

### 场景 1：智能客服机器人

```python
from adp_client import create_client

def customer_service_bot(app_key, user_id):
    """客服机器人"""
    client = create_client(
        app_key=app_key,
        visitor_biz_id=user_id
    )
    
    print("客服机器人已启动，输入 'quit' 退出")
    
    while True:
        user_input = input("用户: ")
        if user_input.lower() == 'quit':
            break
        
        response = client.chat(user_input)
        print(f"客服: {response}\n")
    
    client.close()
```

### 场景 2：实时流式输出

```python
def streaming_chat(app_key, message):
    """实时流式输出"""
    client = create_client(app_key=app_key)
    
    print("AI: ", end="", flush=True)
    
    for event in client.chat_stream(message):
        if event.event_type == "reply":
            print(event.reply_content, end="", flush=True)
    
    print()  # 换行
    client.close()
```

### 场景 3：专业领域助手

```python
def financial_advisor(app_key):
    """金融顾问助手"""
    client = create_client(app_key=app_key)
    
    # 设置专业角色
    client.set_system_role(
        "你是一个专业的金融顾问，拥有10年以上的投资经验。"
        "请用专业但易懂的语言回答用户的金融问题。"
    )
    
    while True:
        question = input("请问: ")
        if not question:
            break
        
        answer = client.chat(question)
        print(f"\n顾问: {answer}\n")
    
    client.close()
```

### 场景 4：批量问答处理

```python
def batch_qa(app_key, questions):
    """批量问答"""
    client = create_client(app_key=app_key)
    results = []
    
    for q in questions:
        try:
            answer = client.chat(q)
            results.append({
                "question": q,
                "answer": answer,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "question": q,
                "answer": None,
                "status": "error",
                "error": str(e)
            })
    
    client.close()
    return results
```

---

## 🔧 高级配置

### 1. 自定义模型

```python
client = create_client(
    app_key="YOUR_KEY",
    model_name="DeepSeek-V3"  # 指定模型
)
```

### 2. 调整流式输出频率

```python
client = create_client(
    app_key="YOUR_KEY",
    streaming_throttle=10  # 每10个字返回一次（默认5）
)
```

### 3. 增量输出模式

```python
client = create_client(
    app_key="YOUR_KEY",
    incremental=True  # 启用增量输出
)

# 增量模式下，每次只返回新增的内容
for event in client.chat_stream("讲个故事"):
    if event.event_type == "reply":
        print(event.reply_content, end="", flush=True)
```

### 4. 自定义工作流参数

```python
client = create_client(
    app_key="YOUR_KEY",
    custom_variables={
        "user_level": "vip",
        "language": "zh-CN"
    }
)
```

---

## 🛠️ 错误处理

### 常见错误

```python
from adp_client import create_client

client = create_client(app_key="YOUR_KEY")

try:
    response = client.chat("你好")
    print(response)
except Exception as e:
    if "401" in str(e):
        print("认证失败，请检查 AppKey")
    elif "timeout" in str(e).lower():
        print("请求超时，请稍后重试")
    else:
        print(f"发生错误: {e}")
finally:
    client.close()
```

### UTF-8 编码处理 ⭐

**重要**：ADP 平台返回的内容是 UTF-8 编码，`adp_client.py` 已经正确处理了编码问题。

#### 已内置的编码处理

```python
# adp_client.py 中已经正确设置了编码
response = requests.post(
    url,
    json=payload,
    headers={"Content-Type": "application/json; charset=utf-8"},
    stream=True,
    timeout=30
)

# SSE 流式数据使用 UTF-8 解码
for line in response.iter_lines(decode_unicode=True):
    # decode_unicode=True 确保正确解码 UTF-8
    if line:
        # 处理中文等多字节字符
        ...
```

#### 如果遇到乱码问题

如果你在使用过程中仍然遇到乱码，可以尝试以下方法：

**方法 1：确保终端支持 UTF-8**

```python
import sys
import io

# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 然后正常使用
client = create_client(app_key="YOUR_KEY")
response = client.chat("你好")
print(response)  # 不会乱码
client.close()
```

**方法 2：显式编码转换（通常不需要）**

```python
# 如果返回的内容是 bytes 类型（正常情况下不会）
if isinstance(response, bytes):
    response = response.decode('utf-8')
print(response)
```

**方法 3：文件写入时指定编码**

```python
# 将对话结果保存到文件
client = create_client(app_key="YOUR_KEY")
response = client.chat("你好")

# 写入文件时指定 UTF-8 编码
with open("chat_result.txt", "w", encoding="utf-8") as f:
    f.write(response)

client.close()
```

#### 常见编码问题排查

| 问题现象 | 可能原因 | 解决方案 |
|---------|---------|---------|
| 中文显示为 `\u4e2d\u6587` | JSON 未正确解码 | 使用 `json.loads()` 而非 `eval()` |
| 中文显示为 `???` 或乱码 | 终端不支持 UTF-8 | 设置终端编码或使用方法 1 |
| 部分中文乱码 | 多字节字符被截断 | 确保使用 `decode_unicode=True` |
| 写入文件后乱码 | 文件编码不是 UTF-8 | 使用 `open(..., encoding='utf-8')` |

#### 验证编码是否正确

```python
from adp_client import create_client

client = create_client(app_key="YOUR_KEY")

# 测试中文处理
test_messages = [
    "你好",
    "测试中文编码",
    "emoji 测试 😊🎉",
    "特殊字符：©®™€£¥"
]

for msg in test_messages:
    response = client.chat(msg)
    print(f"问: {msg}")
    print(f"答: {response}")
    print(f"编码: {response.encode('utf-8')}")  # 查看字节编码
    print("-" * 50)

client.close()
```

### 超时设置

```python
import requests

# 修改默认超时时间
client = create_client(app_key="YOUR_KEY")
# 在 chat_stream 中，超时设置为 30 秒
```

---

## 📊 测试用例

### 运行测试

```bash
# 运行完整测试套件
python3 test_adp.py

# 运行交互式演示
python3 quick_start.py

# 测试特定问题
python3 test_stock_question.py
```

### 测试覆盖

- ✅ 简单对话功能
- ✅ 流式对话处理
- ✅ 多轮对话上下文保持
- ✅ 自定义角色指令
- ✅ 错误处理和异常情况

---

## 📖 技术细节

### SSE 协议解析

本 Skill 实现了完整的 SSE（Server-Sent Events）协议解析，特别处理了 ADP 平台的特殊格式：

1. **多行 data 字段**：ADP 的 `data:` 字段可能跨多行，后续行不带 `data:` 前缀
2. **JSON 嵌套**：data 字段中的 JSON 可能包含冒号，需要特殊处理
3. **消息回显**：第一个 reply 事件是用户消息的回显（`is_from_self=true`），需要过滤

### 数据流处理

```
HTTP Request → SSE Stream → Event Parser → Message Handler → User
     ↓              ↓              ↓              ↓
  POST /chat   event:reply    parse JSON    filter self    return
               data:{...}     extract       messages       content
```

---

## 🔐 安全建议

1. **保护 AppKey**：不要在代码中硬编码 AppKey，使用环境变量或配置文件
2. **会话管理**：为不同用户使用不同的 `session_id` 和 `visitor_biz_id`
3. **内容审核**：检查 `is_evil` 字段，过滤敏感内容
4. **错误处理**：始终使用 try-finally 确保连接关闭

```python
import os

# 推荐：从环境变量读取
app_key = os.environ.get("ADP_APP_KEY")
client = create_client(app_key=app_key)

try:
    response = client.chat("你好")
    # 检查敏感内容
    if hasattr(response, 'is_evil') and response.is_evil:
        print("内容包含敏感信息")
finally:
    client.close()
```

---

## 📝 更新日志

### v1.0.0 (2026-02-12)
- ✅ 初始版本发布
- ✅ 实现 HTTP SSE 协议对接
- ✅ 支持简单对话和流式对话
- ✅ 实现多轮对话上下文管理
- ✅ 支持自定义角色指令
- ✅ 完整的事件类型支持
- ✅ 修复 SSE 多行 data 字段解析问题
- ✅ 修复用户消息回显过滤问题
- ✅ 所有测试用例通过

---

## 📞 参考资源

- **官方文档**：https://www.tencentcloud.com/zh/document/product/1254/69979
- **API 端点**：`https://wss.lke.tencentcloud.com/v1/qbot/chat/sse`
- **项目文件**：
  - `adp_client.py` - 核心客户端库
  - `test_adp.py` - 完整测试套件
  - `quick_start.py` - 快速开始示例
  - `README.md` - 项目说明

---

## 🎓 最佳实践

### 1. 使用上下文管理器

```python
from contextlib import contextmanager
from adp_client import create_client

@contextmanager
def adp_session(app_key):
    """上下文管理器，自动管理连接"""
    client = create_client(app_key=app_key)
    try:
        yield client
    finally:
        client.close()

# 使用
with adp_session("YOUR_KEY") as client:
    response = client.chat("你好")
    print(response)
# 自动关闭连接
```

### 2. 异步处理（可选）

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def chat_task(app_key, message):
    """单个对话任务"""
    client = create_client(app_key=app_key)
    try:
        return client.chat(message)
    finally:
        client.close()

async def batch_chat_async(app_key, messages):
    """异步批量对话"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [
            loop.run_in_executor(executor, chat_task, app_key, msg)
            for msg in messages
        ]
        results = await asyncio.gather(*tasks)
    return results

# 使用
messages = ["问题1", "问题2", "问题3"]
results = asyncio.run(batch_chat_async("YOUR_KEY", messages))
```

### 3. 日志记录

```python
import logging
from adp_client import create_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def logged_chat(app_key, message):
    """带日志的对话"""
    client = create_client(app_key=app_key)
    
    try:
        logger.info(f"发送消息: {message}")
        response = client.chat(message)
        logger.info(f"收到回复: {response[:100]}...")
        return response
    except Exception as e:
        logger.error(f"对话失败: {e}")
        raise
    finally:
        client.close()
```

---

## ⚡ 性能优化

### 1. 连接复用

```python
# 推荐：复用同一个客户端进行多次对话
client = create_client(app_key="YOUR_KEY")

for i in range(10):
    response = client.chat(f"问题 {i+1}")
    print(response)

client.close()  # 最后统一关闭
```

### 2. 流式输出优化

```python
# 对于长文本，使用流式输出可以更快地看到结果
for event in client.chat_stream("写一篇长文章"):
    if event.event_type == "reply":
        print(event.reply_content, end="", flush=True)
```

---

## 🎉 总结

本 Skill 提供了与 ADP 平台的完整对接能力，经过充分测试，可直接用于生产环境。支持简单对话、流式响应、多轮对话、自定义角色等功能，满足各种对话场景需求。

**关键特性**：
- ✅ 生产就绪
- ✅ 完整测试覆盖
- ✅ 详细文档和示例
- ✅ 灵活的 API 设计
- ✅ 健壮的错误处理

开始使用吧！🚀
