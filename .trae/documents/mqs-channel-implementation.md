# MQS 通道实现计划

## 概述
根据 `doc/channel/mqs.md` 文档，实现一个基于消息队列的通信通道（MQS通道），用于在不同服务之间异步传递消息。

## 实施步骤

### 1. 添加 MQS 配置类
**文件**: `nanobot/config/schema.py`

在 `ChannelsConfig` 类中添加 `mqs` 字段：
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
```

### 2. 创建 MQS 通道实现
**文件**: `nanobot/channels/mqs.py`

实现 `MqsChannel` 类，继承自 `BaseChannel`：

**主要功能**:
- 消息消费：循环从 MQS 获取消息
- 消息处理：Base64解码、JSON解析、字段校验
- 消息确认：处理完成后确认消息
- 消息生产：发送响应消息到 MQS

**核心方法**:
- `start()`: 启动消息消费循环
- `stop()`: 停止消费循环
- `send()`: 发送消息到 MQS
- `_consume_messages()`: 消费消息的主循环
- `_consume()`: 调用消费接口
- `_ack_message()`: 确认消息
- `_produce()`: 生产消息
- `_validate_message()`: 校验消息格式
- `_decode_and_parse_message()`: 解码和解析消息

**消息处理流程**:
1. 循环调用消费接口（间隔1秒）
2. 校验消息格式（必须包含 body 和 receiptHandle）
3. Base64解码 body 字段
4. JSON解析得到请求报文
5. 校验必填字段：businessType, messageType, businessBody, source, appid, requestId, requestTime, sessionId
6. 将数据发送到 nanobot 消息总线
7. 执行消息确认（即使处理异常也需要确认）

### 3. 注册 MQS 通道到管理器
**文件**: `nanobot/channels/manager.py`

在 `ChannelManager._init_channels()` 方法中添加 MQS 通道初始化：
```python
# MQS channel
if self.config.channels.mqs.enabled:
    try:
        from nanobot.channels.mqs import MqsChannel
        self.channels["mqs"] = MqsChannel(
            self.config.channels.mqs, self.bus
        )
        logger.info("MQS channel enabled")
    except ImportError as e:
        logger.warning("MQS channel not available: {}", e)
```

### 4. 创建测试文件
**文件**: `tests/test_mqs_channel.py`

创建单元测试，验证：
- 配置加载
- 消息消费逻辑
- 消息解码和解析
- 字段校验
- 消息确认
- 消息生产

## 技术细节

### HTTP 客户端
使用 `httpx` 或 `aiohttp` 进行异步 HTTP 请求：
- 消费接口：GET `/api/mqs/consume`
- 生产接口：POST `/api/mqs/produce`
- 确认接口：DELETE `/api/mqs/ack`

### 消息格式
**消费消息响应**:
```json
[
    {
        "body": "eyJhcHBsaWNhdGlvblN0b3BzIjoiUk1TIn0=",
        "receiptHandle": "1234567890"
    }
]
```

**消费消息 Body（解码后）**:
```json
{
  "businessType": "LEDGER_VALIDATION",
  "messageType": "JSON",
  "businessBody": "",
  "source": "RMS",
  "appid": "RMS",
  "requestId": "1234567890",
  "requestTime": "2026-03-07 12:00:00",
  "sessionId": "1234567890"
}
```

**生产消息 Body**:
```json
{
  "businessType": "LEDGER_VALIDATION",
  "messageType": "JSON",
  "businessBody": "",
  "source": "RMS",
  "appid": "RMS",
  "requestId": "1234567890",
  "responseTime": "2026-03-07 12:00:00",
  "sessionId": "1234567890"
}
```

### 错误处理
- 消息格式不符合要求：打印错误日志，完成消息确认
- 消息处理异常：捕获异常，完成消息确认，继续处理下一条消息
- HTTP 请求失败：记录错误日志，重试或跳过

### 日志记录
使用 `loguru` 记录关键操作：
- 消息消费成功/失败
- 消息解码/解析错误
- 消息确认成功/失败
- 消息生产成功/失败

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
```

## 依赖检查
确认项目中是否已安装以下依赖：
- `httpx` 或 `aiohttp`（用于异步 HTTP 请求）
- `base64`（Python 内置）
- `json`（Python 内置）

如果没有，需要在 `pyproject.toml` 中添加依赖。
