# mqs通道

## 通道介绍
```
mqs通道是一种基于消息队列的通信通道，用于在不同服务之间异步传递消息。它通常用于解耦微服务架构中的服务之间的通信，提高系统的可扩展性和容错性。
```
## 新增配置
```
{
  "channel": "mqs",
  "consumer topic": "T_API_TEST",
  "product topic" : "T_API_TEST_RESPONSE",
  "appid": "RMS",
  "appkey": "RMS_APPKEY",
  "msgGroupId": "RMS_MSG_GROUP"
}
```

## 通道消息处理逻辑
### 消息消费
#### 接口请求
- 请求地址 
    - /api/mqs/consume
- header
    - X-HW-ID // 取配置中的appid
    - X-HW-APPKEY // 取配置中的appkey
    - MsgTopic // 取配置中的consumer topic
    - MsgGroupId // 取配置中的msgGroupId
- 请求方式 GET
- 请求响应示例
```
[
    {
        "body": "eyJhcHBsaWNhdGlvblN0b3BzIjoiUk1TIn0=",
        "receiptHandle": "1234567890"
    }
]
```

#### 消费处理逻辑
1. 循环获取消息, 间隔1s
2. 校验消息格式是否符合要求, 如果不符合要求, 打印错误日志, 完成消息确认
    - 校验消息格式必须包含字段: body, receiptHandle
3. 取出报文中body字段, Base64解码, Json解析, 解析出来请求报文, 校验必填字段
    - 校验必填字段: businessType, messageType, businessBody, source, appid, requestId, requestTime, sessionId
4. 将数据发送到 nanobot消息总线
5. 执行消息确认(消息处理过程中有异常也需要完成消息确认)

### 消息生产
#### 接口请求
- 请求地址 
    - /api/mqs/produce
- header
    - X-HW-ID // 取配置中的appid
    - X-HW-APPKEY // 取配置中的appkey
    - MsgTopic // 取配置中的product topic
    - MsgGroupId // 取配置中的msgGroupId
- 请求方式 POST
    - body // 消息体, Base64编码后的Json字符串, 必填

### 消息确认
#### 接口请求
- 请求地址 
    - /api/mqs/ack
- header
    - X-HW-ID // 取配置中的appid
    - X-HW-APPKEY // 取配置中的appkey
    - MsgTopic // 取配置中的consumer topic
    - MsgGroupId // 取配置中的msgGroupId
    - receiptHandle // 消息接收句柄,取值从消息消费接口返回, 必填
- 请求方式 DELETE

## 消息消费Body报文内容
```
{
  "businessType": "LEDGER_VALIDATION", // 业务类型, 必填
  "messageType": "JSON", // 消息类型, 必填
  "businessBody":"", // 请求规则执行 例如 LEDGER_VALIDATION, 包含业务数据, 必填
  "source" : "RMS", // 来源, 必填
  "appid": "RMS", // 应用ID, 必填
  "requestId": "1234567890", // 请求ID, 必填
  "requestTime": "2026-03-07 12:00:00", // 请求时间, 必填
  "sessionId": "1234567890" // 会话ID, 必填
}
```

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
```

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

### 配置选项
在配置文件中可以控制JSON自动检测行为：
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
    auto_detect_json: true  # 是否自动检测JSON内容，默认为true
```

### JSON检测逻辑
1. 优先使用消息的 `is_json` 标志
2. 如果 `is_json` 为 True，尝试解析 `content` 为JSON对象
3. 如果 `is_json` 为 False 且 `auto_detect_json` 为 True，仍然尝试自动检测
4. 解析失败时，回退到字符串类型，`messageType` 设置为 "TEXT"