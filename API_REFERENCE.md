# ADP 平台 HTTP SSE 对接 API 参考文档

> 本文档来源：https://www.tencentcloud.com/zh/document/product/1254/69979
> 
> 最后更新时间：2026-02-12

## 📖 文档概述

HTTP SSE（Server-Sent Events）是单向通道，客户端发起 HTTP 请求之后，服务端持续推送流式数据到客户端，此时不支持双向交互。

---

## 1. HTTP SSE 接口请求

### 请求地址
```
https://wss.lke.tencentcloud.com/v1/qbot/chat/sse
```

### 请求方式
POST

### 注意事项
⚠️ 触发对话接口前，需要有已发布的应用。

---

### 1.1 参数说明

请放到 HTTP Body 中，以 JSON 的形式发送：

| 名称 | 类型 | 是否必填 | 说明 |
|------|------|----------|------|
| `request_id` | string(255) | 否 | 请求 ID，用于标识一个请求（作消息串联，建议每个请求使用不同的 request_id）。**为了便于问题排查，建议必填。** |
| `content` | string | 是 | 消息内容，如果发送图片，在此传递 markdown 格式的图片链接，例如 `![](图片链接)`，其中图片链接需要可公有读【需将图片传入 tcadp 的 cos 中】。最大值限制：不同模型最大值有差异，请参考 ListModel 接口的 InputLenLimit。 |
| `file_infos` | Object 数组 | 否 | 文件信息，如果填写该字段，content 字段可以为空。依赖实时文档解析。**注意：没有文件信息时，该字段可不填或指定为空数组。** |
| `session_id` | string(64) | 是 | 会话 ID，用于标识一个会话（外部系统提供，建议不同的用户端会话传入**不同的** session_id，否则同一个应用下的不同用户的消息记录会串掉）。参数长度：2-64个字符。校验规则：`^[a-zA-Z0-9_-]{2,64}$`，一般可以用 uuid 来生成该值。uuid 示例：`1b9c0b03-dc83-47ac-8394-b366e3ea67ef` |
| `bot_app_key` | string(128) | 是 | 应用密钥（AppKey） |
| `visitor_biz_id` | string(64) | 是 | 访客 ID（外部输入，建议唯一，标识当前接入会话的用户） |
| `streaming_throttle` | int32 | 否 | 流式回复频率控制：控制应用回包频率。该值表示应用每积攒多少字符向调用方回包一次，值越小回包越频繁（体验上越流畅，但流量开销也越大）。当不传值或者为 0 时以系统配置为准。**默认值：5，建议最大值：100**。**注意：该设置项也不会加快大模型输出的时间，只是改变了向调用方回包的频率。因此如果设置很大，则会出现很长时间没有回包的现象。** |
| `custom_variables` | map[string]string | 否 | **工作流场景**：自定义参数可用于传递参数给工作流开始节点的API参数字段。**检索知识库范围设置场景**：自定义参数可用于设置知识库检索范围，如需传入多个参数值，使用英文竖线分隔(\|)，例如：`"user1\|user2"`。**注意：map的key和value类型都是string，如 `{"UserID":"10220022"}`** |
| `system_role` | string | 否 | 角色指令（提示词），为空时使用应用配置默认设定，填写时取当前值。最大值限制：不同模型最大值有差异，请参考 ListModel 接口的 RoleLenLimit。**注意：该参数仅在标准模式下生效。** |
| `incremental` | bool | 否 | 控制回复事件和思考事件中的 content 是否是增量输出的内容，默认 false。**注意：该字段设置为 true，只对回复事件、思考事件生效。** |
| `model_name` | string | 否 | 支持在对话的过程传入指定模型，同一个 session_id 下传入不同的模型名称可以保持上下文之间的关联。当前支持：`Deepseek/deepseek-v3.1-terminus`、`Deepseek/deepseek-v3-250324`、`Deepseek/deepseek-r1-0528`。**注意：请确保选择的模型有足够的 token 或者开启了后付费模式，避免在使用过程中报错。** |
| `stream` | string | 否 | 是否开启流式传输。取值范围：空字符串（跟随应用配置）、`enable`（流式传输）、`disable`（非流式传输） |
| `workflow_status` | string | 否 | 是否开启工作流。取值范围：空字符串（跟随应用配置，默认是开启）、`enable`（开启工作流）、`disable`（关闭工作流） |

---

### 1.2 如何获取 AppKey

1. 在**应用管理**界面，找到您处于运行中的应用（需要先发布）
2. 单击**调用**，会弹出"调用信息"窗口
3. 在**调用信息**窗口可以看到 AppKey，单击**复制**即可

---

### 1.3 curl 调用示例

```bash
curl --location 'https://wss.lke.tencentcloud.com/v1/qbot/chat/sse' \
--header 'Content-Type: application/json' \
--data '{
  "session_id":"a29bae68-cb1c-489d-8097-6be78f136acf",
  "bot_app_key":"请自行获取应用对应的key",
  "visitor_biz_id":"a29bae68-cb1c-489d-8097-6be78f136acf",
  "content":"哪吒2票房",
  "incremental": true,
  "streaming_throttle": 10,
  "visitor_labels": [],
  "custom_variables":{},
  "search_network":"disable",
  "stream":"enable",
  "workflow_status":"disable",
  "tcadp_user_id":""
}'
```

---

## 2. HTTP SSE 接口返回

### 2.1 回复事件 (reply)

**事件名**：`reply`

**事件方向**：后端 → 前端

**注意事项**：
- 如果收到的消息中 `is_evil == true` 表示该消息命中敏感内容，发送失败
- 因并发超限导致排队超时，会下发 "超出并发数限制" 错误

**数据结构**：

| 名称 | 类型 | 说明 |
|------|------|------|
| `request_id` | string(255) | 请求 ID |
| `content` | string | 消息内容 |
| `file_infos` | Object 数组 | 文件信息 |
| `record_id` | string(64) | 消息唯一 ID |
| `related_record_id` | string(64) | 关联的消息唯一 ID |
| `session_id` | string(64) | 会话 ID |
| `is_from_self` | bool | 消息是否由自己发出（如果是自己发出，显示在聊天框右侧，否则在左侧） |
| `can_rating` | bool | 该消息记录是否能评价 |
| `timestamp` | int64 | 消息时间戳（秒级） |
| `is_final` | bool | reply 事件消息是否已输出完。流式模式下，消息会多次返回，每次返回均覆盖之前的答案。当 `is_final == true` 时，停止生成按钮被隐藏，并且显示点赞和点踩按钮。**reference 事件和 reply 事件无固定顺序关系，不建议以该字段作为消息完整结束的标识。** |
| `is_evil` | bool | 是否命中敏感内容。**注意：消息上行后会先进行敏感内容检测，并返回一条【reply】事件，告知敏感内容检测结果，敏感内容检测通过后才会进入正常业务逻辑处理。** |
| `is_llm_generated` | bool | 是否为模型生成内容 |
| `reply_method` | uint8 | 回复方式：1-大模型回复，2-未知问题回复，3-拒答问题回复，4-敏感回复，5-已采纳问答对优先回复，6-欢迎语回复，7-并发数超限回复，8-全局干预知识，9-任务流回复，10-任务流答案，11-搜索引擎回复，12-知识润色后回复，13-图片理解回复，14-实时文档回复，15-澄清确认回复，16-工作流回复，17-工作流运行结束，18-智能体回复，19-多意图回复 |
| `knowledge` | Object 数组 | 命中的知识 |
| `option_cards` | string 数组 | 选项卡，任务流程专有（该字段可能为空，为空时该字段不返回） |
| `custom_params` | string 数组 | 用户自定义业务参数，用于透传问答中业务参数（该字段可能为空，为空时该字段不返回） |
| `task_flow` | Object | 任务流程调试信息（该字段可能为空，为空时该字段不返回） |
| `work_flow` | Object | 工作流调试信息（该字段可能为空，为空时该字段不返回） |
| `quote_infos` | Object 数组 | 引用信息 |

---

### 2.2 token 统计事件 (token_stat)

**事件名**：`token_stat`

**事件方向**：后端 → 前端

**数据结构**：

| 名称 | 类型 | 说明 |
|------|------|------|
| `session_id` | string(64) | 会话 id |
| `request_id` | string(255) | 对应发送事件的请求 id |
| `record_id` | string(64) | 对应发送事件的消息记录 id |
| `status_summary` | string | 本轮对话状态：`processing`（处理中）、`success`（成功）、`failed`（失败） |
| `status_summary_title` | string | 本轮对话状态描述 |
| `elapsed` | int | 本轮调用耗时，单位 ms |
| `token_count` | int | 本轮请求消耗 token 数（当包含多个过程时，计算将汇总） |
| `procedures` | Object 数组 | 调用过程列表 |

**procedures 数据结构**：

| 名称 | 类型 | 说明 |
|------|------|------|
| `name` | string | 英文名：`knowledge`（知识库）、`task_flow`（任务流程）、`search_engine`（搜索引擎）、`image`（图片理解）、`large_language_model`（大模型）、`pot_math`（计算器）、`file`（文件） |
| `title` | string | 调用过程描述（中文） |
| `status` | string | 调用过程状态：`processing`（处理中）、`success`（成功）、`failed`（失败） |
| `input_count` | int | 当次过程输入消耗 token 数 |
| `output_count` | int | 当次过程输出消耗 token 数 |
| `count` | int | 当次过程消耗总 token 数（输入 + 输出） |

---

### 2.3 参考来源事件 (reference)

**事件名**：`reference`

**事件方向**：后端 → 前端

**数据结构**：

| 名称 | 类型 | 说明 |
|------|------|------|
| `record_id` | string(64) | 消息唯一 ID |
| `references` | Object 数组 | 参考来源 |

**references 数据结构**：

| 名称 | 类型 | 说明 |
|------|------|------|
| `id` | string | 参考来源 ID（type=1,2,3 时，可调用 DescribeRefer 接口查看详情；type=4 时，表示联网检索来源的序号） |
| `type` | uint32 | 参考来源类型：1-问答，2-文档片段，4-联网检索到的内容。**注意：当 type=2 时，参考来源返回的粒度是文档切片维度的数据，一篇文档【doc_id】可能存在多个切片，请自行决定是否需要进行去重展示。** |
| `url` | string | type=2 时为文档自定义跳转链接地址；type=4 时为联网搜索到的信源地址 |
| `name` | string | 参考来源名称 |
| `doc_id` | uint64 | 参考来源文档 ID |
| `doc_biz_id` | uint64 | 参考来源文档业务 ID |
| `doc_name` | string | 参考来源文档名称 |
| `qa_biz_id` | string | 参考来源问答业务 ID |

---

### 2.4 错误事件 (error)

**事件名**：`error`

**事件方向**：后端 → 前端

**数据结构**：

| 名称 | 类型 | 说明 |
|------|------|------|
| `request_id` | string(255) | 请求 ID |
| `error` | Object | 错误信息 |

**error 数据结构**：

| 名称 | 类型 | 说明 |
|------|------|------|
| `code` | uint32 | 错误码 |
| `message` | string | 错误信息 |

**注意**：接口使用时需判断取值是否为200，是则正常返回。

---

### 2.5 思考事件 (thought)

**事件名**：`thought`

**事件方向**：后端 → 前端

**注意**：该事件目前只在使用 **DeepSeek-R1** 模型的时候有返回。

**数据结构**：

| 名称 | 类型 | 说明 |
|------|------|------|
| `elapsed` | int | 本轮调用耗时，单位 ms |
| `is_workflow` | bool | 是否工作流 |
| `procedures` | Object 数组 | 调用过程列表 |
| `record_id` | string(64) | 对应发送事件对应的消息记录 id |
| `request_id` | string(255) | 对应发送事件对应的请求 id |
| `session_id` | string(64) | 会话 id |
| `trace_id` | string | 链路 id |
| `workflow_name` | string | 工作流名称 |

**procedures 数据结构**：

| 名称 | 类型 | 说明 |
|------|------|------|
| `debugging` | Object | 调试过程信息 |
| `index` | uint32 | 过程索引 |
| `name` | string | 英文名：`knowledge`、`task_flow`、`search_engine`、`image`、`large_language_model`、`pot_math`、`file`、`thought` |
| `title` | string | 调用过程描述（中文） |
| `status` | string | 状态：`processing`（使用中）、`success`（成功）、`failed`（失败） |
| `icon` | string | 图标，用于展示 |
| `switch` | string | 是否切换Agent |
| `workflow_name` | string | 工作流名称 |
| `plugin_type` | int32 | 插件类型：0-自定义插件，1-官方插件，2-工作流 |
| `elapsed` | uint32 | 当前请求执行时间，单位 ms |

**debugging 数据结构**：

| 名称 | 类型 | 说明 |
|------|------|------|
| `content` | string | 调试过程中输出的内容（模型的思考过程） |

---

## 3. 错误码

| 错误码 | 错误信息 |
|--------|----------|
| 400 | 请求参数错误，请参阅接入文档 |
| 460001 | Token 校验失败 |
| 460002 | 事件处理器不存在 |
| 460004 | 应用不存在 |
| 460006 | 消息不存在或没有操作权限 |
| 460007 | 会话创建失败 |
| 460008 | Prompt 渲染失败 |
| 460009 | 访客用户不存在 |
| 460010 | 会话不存在或没有操作权限 |
| 460011 | 超出并发数限制 |
| 460020 | 模型请求超时 |
| 460021 | 知识库未发布 |
| 460022 | 访客创建失败 |
| 460023 | 消息点赞点踩失败 |
| 460024 | 标签不合法 |
| 460025 | 图像识别失败 |
| 460031 | 当前应用连接数超出请求限制，请稍后再试 |
| 460032 | 当前应用模型余额不足 |
| 460033 | 应用不存在或没有操作权限 |
| 460034 | 输入内容过长 |
| 460035 | 计算内容过长，已经停止 |
| 460036 | 任务流程节点预览参数异常 |
| 460037 | 搜索资源已用尽，调用失败 |
| 460038 | 该 AppID 请求存在异常行为，调用失败 |
| 4505004 | APPKEY 无效，请核实 APPKEY来源 |

---

## 4. 编码处理

### UTF-8 编码说明

ADP 平台返回的内容使用 **UTF-8 编码**，在使用 `requests.post()` 和 `iter_lines()` 时需要正确设置编码参数：

```python
# HTTP 请求头设置
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Accept": "text/event-stream; charset=utf-8"
}

# SSE 流式数据处理
for line in response.iter_lines(decode_unicode=True):
    # decode_unicode=True 确保正确解码 UTF-8
    if line:
        # 处理中文等多字节字符
        ...
```

### 常见编码问题

| 问题现象 | 可能原因 | 解决方案 |
|---------|---------|---------|
| 中文显示为 `\u4e2d\u6587` | JSON 未正确解码 | 使用 `json.loads()` 而非 `eval()` |
| 中文显示为 `???` 或乱码 | 终端不支持 UTF-8 | 设置终端编码或使用 `io.TextIOWrapper` |
| 部分中文乱码 | 多字节字符被截断 | 确保使用 `decode_unicode=True` |
| 写入文件后乱码 | 文件编码不是 UTF-8 | 使用 `open(..., encoding='utf-8')` |

---

## 5. 快速部署

adp-chat-client 代码内包括了一个完整连接建立和消息收发的流程。详细请查看：
- [基于官方开源项目 ADP-chat-client 的集成方案](https://www.tencentcloud.com/document/product/1254/74268)

---

## 6. 前端渲染组件

如果不需要完整客户端，仅需要大模型回复的消息的前端渲染组件：

- **消息统一渲染组件（Vue 2 或 React）**：[lke-component - npm](https://www.npmjs.com/package/lke-component)
- **消息统一渲染组件（Vue 3）**：[lke-component-vue3 - npm](https://www.npmjs.com/package/lke-component-vue3)

---

## 📚 相关文档

- [对话接口总体概述](https://www.tencentcloud.com/document/product/1254/69977)
- [对话端接口文档（WebSocket）](https://www.tencentcloud.com/document/product/1254/69978)
- [图片对话或文件对话（实时文档解析+对话）](https://www.tencentcloud.com/document/product/1254/72532)
- [离线文档上传](https://www.tencentcloud.com/document/product/1254/69980)
- [获取来源详情列表 (DescribeRefer)](https://www.tencentcloud.com/document/product/1254/70433)
- [文档详情](https://www.tencentcloud.com/document/product/1254/70216)
- [DescribeSegments 接口](https://www.tencentcloud.com/document/product/1254/70432)
- [ListModel 接口](https://www.tencentcloud.com/document/product/1254/70442)

---

**文档版权**：Copyright © 2013-2026 Tencent Cloud. All Rights Reserved.
