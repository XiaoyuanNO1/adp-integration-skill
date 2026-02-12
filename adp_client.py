#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADP 平台 HTTP SSE 对接客户端
支持流式响应处理和多种事件类型解析
"""

import requests
import json
import time
import uuid
from typing import Optional, Dict, Any, Callable, Generator
from dataclasses import dataclass, field
from enum import Enum


class EventType(Enum):
    """SSE 事件类型枚举"""
    REPLY = "reply"
    REFERENCE = "reference"
    TOKEN_STAT = "token_stat"
    THOUGHT = "thought"
    ERROR = "error"


class ReplyMethod(Enum):
    """回复方式枚举"""
    LLM = 1  # 大模型回复
    UNKNOWN = 2  # 未知问题
    SENSITIVE = 3  # 敏感内容
    FAQ = 4  # FAQ回复


@dataclass
class ADPConfig:
    """ADP 配置类"""
    bot_app_key: str
    base_url: str = "https://wss.lke.tencentcloud.com/v1/qbot/chat/sse"
    timeout: int = 60
    streaming_throttle: int = 5  # 流式回复频率控制


@dataclass
class ChatMessage:
    """聊天消息类"""
    content: str
    session_id: str
    visitor_biz_id: str
    request_id: Optional[str] = None
    incremental: bool = False
    model_name: Optional[str] = None
    custom_variables: Optional[Dict[str, Any]] = None
    system_role: Optional[str] = None


@dataclass
class ADPResponse:
    """ADP 响应数据类"""
    event_type: EventType
    data: Dict[str, Any]
    raw_data: str
    
    @property
    def is_reply(self) -> bool:
        return self.event_type == EventType.REPLY
    
    @property
    def is_final(self) -> bool:
        """判断是否为最终回复"""
        if self.is_reply:
            return self.data.get("is_final", False)
        return False
    
    @property
    def reply_content(self) -> str:
        """获取回复内容"""
        if self.is_reply:
            # data 已经是 payload 了（在 _parse_sse_event 中提取）
            return self.data.get("content", "")
        return ""
    
    @property
    def record_id(self) -> Optional[str]:
        """获取消息记录ID"""
        if self.is_reply:
            return self.data.get("record_id")
        return None
    
    @property
    def is_evil(self) -> bool:
        """判断是否命中敏感内容"""
        if self.is_reply:
            return self.data.get("is_evil", False)
        return False
    
    @property
    def reply_method(self) -> Optional[ReplyMethod]:
        """获取回复方式"""
        if self.is_reply:
            method = self.data.get("reply_method")
            if method:
                try:
                    return ReplyMethod(method)
                except ValueError:
                    return None
        return None


class ADPClient:
    """ADP 平台客户端"""
    
    def __init__(self, config: ADPConfig):
        self.config = config
        self.session = requests.Session()
    
    def _build_request_body(self, message: ChatMessage) -> Dict[str, Any]:
        """构建请求体"""
        body = {
            "bot_app_key": self.config.bot_app_key,
            "session_id": message.session_id,
            "visitor_biz_id": message.visitor_biz_id,
            "content": message.content,
            "streaming_throttle": self.config.streaming_throttle,
            "incremental": message.incremental,
        }
        
        # 添加可选参数
        if message.request_id:
            body["request_id"] = message.request_id
        if message.model_name:
            body["model_name"] = message.model_name
        if message.custom_variables:
            body["custom_variables"] = message.custom_variables
        if message.system_role:
            body["system_role"] = message.system_role
        
        return body
    
    def _parse_sse_line(self, line: str) -> tuple[Optional[str], Optional[str]]:
        """解析 SSE 单行，返回 (field, value)"""
        if ':' not in line:
            return None, None
        
        field, _, value = line.partition(':')
        return field.strip(), value.strip()
    
    def _parse_sse_event(self, event_name: str, data_json: str) -> Optional[ADPResponse]:
        """解析 SSE 事件"""
        try:
            if not data_json:
                return None
            
            data = json.loads(data_json)
            
            # 优先使用 event_name，然后尝试从数据中获取
            event_type_str = event_name or data.get("type")
            if not event_type_str:
                return None
            
            try:
                event_type = EventType(event_type_str)
            except ValueError:
                # 未知事件类型，跳过（静默处理）
                return None
            
            # 提取 payload（如果存在）
            payload = data.get("payload", data)
            
            return ADPResponse(
                event_type=event_type,
                data=payload,
                raw_data=data_json
            )
        except json.JSONDecodeError:
            # JSON 不完整（流式传输分片），静默跳过
            return None
        except Exception:
            # 其他错误，静默跳过
            return None
    
    def chat_stream(
        self,
        message: ChatMessage,
        on_event: Optional[Callable[[ADPResponse], None]] = None
    ) -> Generator[ADPResponse, None, None]:
        """
        发送聊天消息并处理流式响应
        
        Args:
            message: 聊天消息对象
            on_event: 事件回调函数（可选）
        
        Yields:
            ADPResponse: 响应事件对象
        """
        body = self._build_request_body(message)
        
        try:
            response = self.session.post(
                self.config.base_url,
                json=body,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                },
                stream=True,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            # 处理 SSE 流：event: 和 data: 两行格式
            current_event = None
            buffer = ""
            in_data_field = False  # 标记是否在 data 字段内
            
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    # 空行表示事件结束
                    if current_event and buffer:
                        event_obj = self._parse_sse_event(current_event, buffer)
                        if event_obj:
                            # 触发回调
                            if on_event:
                                on_event(event_obj)
                            
                            yield event_obj
                            
                            # 只有当是 AI 的最终回复时才结束（跳过用户消息回显）
                            if event_obj.is_final and event_obj.is_reply:
                                if not event_obj.data.get("is_from_self", False):
                                    break
                        
                        current_event = None
                        buffer = ""
                        in_data_field = False
                    continue
                
                # 如果已经在 data 字段内，所有非空行都是 data 的一部分
                if in_data_field:
                    buffer += line
                    continue
                
                # 否则，解析字段
                field, value = self._parse_sse_line(line)
                
                if field == "event":
                    current_event = value
                elif field == "data":
                    # SSE data 字段开始
                    buffer += value
                    in_data_field = True
        
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            raise
        except Exception as e:
            print(f"未知错误: {e}")
            raise
    
    def chat(
        self,
        content: str,
        session_id: Optional[str] = None,
        visitor_biz_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        发送聊天消息并返回完整回复（简化接口）
        
        Args:
            content: 消息内容
            session_id: 会话ID（可选，自动生成）
            visitor_biz_id: 访客ID（可选，自动生成）
            **kwargs: 其他可选参数
        
        Returns:
            str: 完整的回复内容
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        if not visitor_biz_id:
            visitor_biz_id = f"user_{int(time.time())}"
        
        message = ChatMessage(
            content=content,
            session_id=session_id,
            visitor_biz_id=visitor_biz_id,
            **kwargs
        )
        
        full_reply = ""
        for event in self.chat_stream(message):
            if event.is_reply:
                # 跳过用户自己的消息（回显）
                if event.data.get("is_from_self", False):
                    continue
                
                if event.data.get("incremental", False):
                    # 增量模式：累加内容
                    full_reply += event.reply_content
                else:
                    # 全量模式：直接替换
                    full_reply = event.reply_content
                
                if event.is_final:
                    break
        
        return full_reply
    
    def close(self):
        """关闭客户端连接"""
        self.session.close()


def create_client(app_key: str, **kwargs) -> ADPClient:
    """
    创建 ADP 客户端的便捷函数
    
    Args:
        app_key: 应用密钥
        **kwargs: 其他配置参数
    
    Returns:
        ADPClient: 客户端实例
    """
    config = ADPConfig(bot_app_key=app_key, **kwargs)
    return ADPClient(config)


# ============= 示例用法 =============

def example_simple_chat():
    """简单对话示例"""
    print("=== 简单对话示例 ===\n")
    
    # 创建客户端
    client = create_client(
        app_key="YOUR_APP_KEY_HERE"
    )
    
    try:
        # 发送消息并获取完整回复
        response = client.chat("你好，请介绍一下你自己")
        print(f"AI 回复: {response}\n")
    finally:
        client.close()


def example_stream_chat():
    """流式对话示例"""
    print("=== 流式对话示例 ===\n")
    
    client = create_client(
        app_key="YOUR_APP_KEY_HERE"
    )
    
    try:
        message = ChatMessage(
            content="请写一首关于春天的诗",
            session_id=str(uuid.uuid4()),
            visitor_biz_id="test_user_001",
            incremental=False  # 全量输出模式
        )
        
        print("AI 回复（流式）:")
        for event in client.chat_stream(message):
            if event.is_reply:
                print(event.reply_content, end="", flush=True)
                
                if event.is_final:
                    print("\n\n[回复完成]")
                    print(f"Record ID: {event.record_id}")
                    print(f"Reply Method: {event.reply_method}")
            
            elif event.event_type == EventType.REFERENCE:
                print(f"\n[参考来源]: {event.data}")
            
            elif event.event_type == EventType.TOKEN_STAT:
                print(f"\n[Token 统计]: {event.data}")
            
            elif event.event_type == EventType.ERROR:
                print(f"\n[错误]: {event.data}")
    
    finally:
        client.close()


def example_with_context():
    """带上下文的多轮对话示例"""
    print("=== 多轮对话示例 ===\n")
    
    client = create_client(
        app_key="YOUR_APP_KEY_HERE"
    )
    
    try:
        # 使用相同的 session_id 保持上下文
        session_id = str(uuid.uuid4())
        visitor_id = "test_user_002"
        
        # 第一轮对话
        response1 = client.chat(
            "我想了解一下人工智能",
            session_id=session_id,
            visitor_biz_id=visitor_id
        )
        print(f"第1轮 - AI: {response1}\n")
        
        # 第二轮对话（带上下文）
        response2 = client.chat(
            "它有哪些应用场景？",
            session_id=session_id,
            visitor_biz_id=visitor_id
        )
        print(f"第2轮 - AI: {response2}\n")
    
    finally:
        client.close()


if __name__ == "__main__":
    # 运行示例（需要替换 YOUR_APP_KEY_HERE）
    print("ADP 客户端示例\n")
    print("请在代码中替换 YOUR_APP_KEY_HERE 为实际的 AppKey\n")
    
    # example_simple_chat()
    # example_stream_chat()
    # example_with_context()
