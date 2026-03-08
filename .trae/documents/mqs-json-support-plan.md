# MQS通道JSON格式返回支持计划

## 概述

为MQS通道添加JSON格式返回支持，使其能够正确处理和返回skill返回的JSON内容，而不是将JSON作为普通文本字符串处理。

## 当前问题分析

### 现状

1. MQS通道已实现基本的消息消费和生产功能
2. `messageType` 字段默认为 "JSON"，但实际上 `businessBody` 字段存储的是字符串类型
3. 当skill返回JSON格式的数据时，被作为普通文本字符串处理，导致接收方需要再次解析

### 需求

* 支持将skill返回的JSON内容作为真正的JSON对象返回

* 保持向后兼容性，非JSON内容仍作为字符串处理

* 确保 `messageType` 字段准确反映 `businessBody` 的实际类型

## 实施步骤

### 1. 修改 `OutboundMessage` 数据结构

**文件**: `nanobot/bus/events.py`

为 `OutboundMessage` 添加一个字段来标识内容是否为JSON对象：

```python
@dataclass
class OutboundMessage:
    """Message to send to a chat channel."""

    channel: str
    chat_id: str
    content: str
    reply_to: str | None = None
    media: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    is_json: bool = False  # 新增：标识content是否为JSON对象
```

### 2. 修改 `MqsChannel._prepare_outbound_message` 方法

**文件**: `nanobot/channels/mqs.py`

修改出站消息准备逻辑，支持JSON对象处理：

```python
def _prepare_outbound_message(self, msg: OutboundMessage) -> dict[str, Any]:
    """Prepare outbound message for MQS produce endpoint."""
    metadata = msg.metadata or {}

    # 处理businessBody：如果是JSON对象，则解析为dict；否则保持为字符串
    business_body = msg.content or ""
    message_type = metadata.get("messageType", "TEXT")

    # 如果msg.is_json为True，尝试解析content为JSON对象
    if msg.is_json:
        try:
            # 尝试解析JSON字符串为对象
            business_body = json.loads(business_body)
            message_type = "JSON"
        except (json.JSONDecodeError, TypeError):
            # 解析失败，保持为字符串
            message_type = "TEXT"
    else:
        # 检查content是否为有效的JSON字符串
        try:
            json.loads(business_body)
            message_type = "JSON"
        except (json.JSONDecodeError, TypeError):
            message_type = "TEXT"

    message_body = {
        "businessType": metadata.get("businessType", ""),
        "messageType": message_type,
        "businessBody": business_body,
        "source": metadata.get("source", self.config.appid),
        "appid": self.config.appid,
        "requestId": metadata.get("requestId", ""),
        "responseTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sessionId": msg.chat_id,
    }

    if not self._validate_required_fields(message_body, self.REQUIRED_OUTBOUND_FIELDS):
        logger.warning("Outbound message missing required fields: {}", message_body)

    return message_body
```

### 3. 修改 `MqsChannel._produce` 方法

**文件**: `nanobot/channels/mqs.py`

确保JSON对象正确序列化：

```python
async def _produce(self, message_body: dict[str, Any]) -> None:
    """Produce a message to MQS."""
    if not self._http_client:
        return

    url = f"{self.config.base_url}/api/mqs/produce"
    headers = self._build_headers(topic=self.config.product_topic)

    # 确保businessBody如果是dict，会被正确序列化
    body_json = json.dumps(message_body, ensure_ascii=False)
    body_base64 = base64.b64encode(body_json.encode("utf-8")).decode("utf-8")

    try:
        response = await self._http_client.post(url, headers=headers, content=body_base64)
        response.raise_for_status()
        logger.debug("Message produced successfully")
    except httpx.HTTPStatusError as e:
        logger.error("HTTP error producing message: {}", e)
        raise
    except Exception as e:
        logger.error("Error producing message: {}", e)
        raise
```

### 4. 修改 `AgentLoop._process_message` 方法

**文件**: `nanobot/agent/loop.py`

在创建 `OutboundMessage` 时，检测响应内容是否为JSON：

```python
# 在_process_message方法的返回OutboundMessage之前添加JSON检测
def _is_json_content(self, content: str) -> bool:
    """检测内容是否为有效的JSON字符串"""
    if not content:
        return False
    try:
        json.loads(content)
        return True
    except (json.JSONDecodeError, TypeError):
        return False

# 修改返回OutboundMessage的代码
preview = final_content[:120] + "..." if len(final_content) > 120 else final_content
logger.info("Response to {}:{}: {}", msg.channel, msg.sender_id, preview)

# 检测内容是否为JSON
is_json = self._is_json_content(final_content)

return OutboundMessage(
    channel=msg.channel,
    chat_id=msg.chat_id,
    content=final_content,
    metadata=msg.metadata or {},
    is_json=is_json,  # 新增参数
)
```

### 5. 添加配置选项（可选）

**文件**: `nanobot/config/schema.py`

在 `MqsConfig` 中添加配置选项，控制是否自动检测JSON：

```python
class MqsConfig(Base):
    """MQS channel configuration."""

    enabled: bool = False
    base_url: str = ""  # MQS服务基础URL
    consumer_topic: str = ""  # 消费主题
    product_topic: str = ""  # 生产主题
    appid: str = ""  # 应用ID
    appkey: str = ""  # 应用密钥
    msg_group_id: str = ""  # 消息组ID
    poll_interval_seconds: int = 1  # 消息轮询间隔（秒）
    auto_detect_json: bool = True  # 新增：是否自动检测JSON内容
```

### 6. 更新测试用例

**文件**: `tests/test_mqs_channel.py`

添加新的测试用例，验证JSON格式返回功能：

```python
def test_prepare_outbound_message_with_json_content() -> None:
    """测试JSON内容正确处理"""
    channel = MqsChannel(_make_config(), MessageBus())
    json_content = '{"result": "success", "data": {"key": "value"}}'
    msg = OutboundMessage(
        channel="mqs",
        chat_id="1234567890",
        content=json_content,
        is_json=True,
        metadata={
            "businessType": "LEDGER_VALIDATION",
            "source": "RMS",
            "requestId": "1234567890",
        },
    )

    result = channel._prepare_outbound_message(msg)

    assert result["messageType"] == "JSON"
    assert result["businessBody"] == json.loads(json_content)
    assert isinstance(result["businessBody"], dict)

def test_prepare_outbound_message_with_text_content() -> None:
    """测试普通文本内容正确处理"""
    channel = MqsChannel(_make_config(), MessageBus())
    text_content = "This is a plain text message"
    msg = OutboundMessage(
        channel="mqs",
        chat_id="1234567890",
        content=text_content,
        is_json=False,
        metadata={
            "businessType": "LEDGER_VALIDATION",
            "source": "RMS",
            "requestId": "1234567890",
        },
    )

    result = channel._prepare_outbound_message(msg)

    assert result["messageType"] == "TEXT"
    assert result["businessBody"] == text_content
    assert isinstance(result["businessBody"], str)

def test_prepare_outbound_message_auto_detect_json() -> None:
    """测试自动检测JSON内容"""
    channel = MqsChannel(_make_config(), MessageBus())
    json_content = '{"status": "ok"}'
    msg = OutboundMessage(
        channel="mqs",
        chat_id="1234567890",
        content=json_content,
        metadata={
            "businessType": "LEDGER_VALIDATION",
            "source": "RMS",
            "requestId": "1234567890",
        },
    )

    result = channel._prepare_outbound_message(msg)

    assert result["messageType"] == "JSON"
    assert result["businessBody"] == json.loads(json_content)
```

### 7. 更新文档

**文件**: `nanobot/doc/channel/mqs.md`

更新文档，说明JSON格式返回功能：

````markdown
## 消息生产Body报文内容

### JSON格式返回
当skill返回JSON格式的内容时，MQS通道会自动检测并将 `businessBody` 设置为JSON对象，`messageType` 设置为 "JSON"。

**示例**：
```json
{
  "businessType": "LEDGER_VALIDATION",
  "messageType": "JSON",
  "businessBody": {
    "result": "success",
    "data": {
      "validation_status": "passed",
      "details": {...}
    }
  },
  "source": "RMS",
  "appid": "RMS",
  "requestId": "1234567890",
  "responseTime": "2026-03-08 12:00:00",
  "sessionId": "1234567890"
}
````

### 文本格式返回

当内容不是有效的JSON时，`businessBody` 保持为字符串，`messageType` 设置为 "TEXT"。

**示例**：

```json
{
  "businessType": "LEDGER_VALIDATION",
  "messageType": "TEXT",
  "businessBody": "This is a plain text response",
  "source": "RMS",
  "appid": "RMS",
  "requestId": "1234567890",
  "responseTime": "2026-03-08 12:00:00",
  "sessionId": "1234567890"
}
```

````

## 技术细节

### JSON检测逻辑
1. 优先使用 `msg.is_json` 标志
2. 如果 `msg.is_json` 为 True，尝试解析 `content` 为JSON对象
3. 如果 `msg.is_json` 为 False，仍然尝试自动检测（可配置）
4. 解析失败时，回退到字符串类型

### 向后兼容性
- 保持现有的消息格式不变
- 非JSON内容仍然作为字符串处理
- 不影响其他通道的实现

### 错误处理
- JSON解析失败时，记录警告日志
- 保持消息的完整性，确保即使解析失败也能正常发送

## 配置示例

在配置文件中添加：
```yaml
channels:
  mqs:
    enabled: true
    base_url: "http://mqs-server:8080"
    consumer_topic: "T_API_TEST"
    product_topic: "T_API_TEST_RESPONSE"
    appid: "RMS"
    appkey: "RMS_APPKEY"
    msg_group_id: "RMS_MSG_GROUP"
    poll_interval_seconds: 1
    auto_detect_json: true  # 是否自动检测JSON内容
````

## 测试计划

1. 单元测试：验证JSON检测和解析逻辑
2. 集成测试：验证完整的消息流程
3. 边界测试：测试各种边界情况（空内容、无效JSON、嵌套JSON等）
4. 回归测试：确保不影响现有功能

## 实施顺序

1. 修改 `OutboundMessage` 数据结构
2. 修改 `MqsChannel._prepare_outbound_message` 方法
3. 修改 `AgentLoop._process_message` 方法
4. 添加配置选项（可选）
5. 更新测试用例
6. 更新文档
7. 运行测试验证

## 风险评估

### 低风险

* 修改仅限于MQS通道

* 保持向后兼容性

* 有完善的测试覆盖

### 注意事项

* 确保JSON序列化时使用 `ensure_ascii=False` 以支持中文

* 处理大JSON对象时的性能问题

* 确保错误处理不会导致消息丢失

