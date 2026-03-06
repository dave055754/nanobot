---
name: ledger-validation
description: 分录明细账校验技能，用于验证财务分录数据的有效性，包括金额、汇率、币种和日期的校验。使用场景：财务数据验证、记账凭证审核、财务系统数据校验。
---

# 分录明细账校验

## 功能说明

此技能用于校验财务分录明细账数据的有效性，包括：

- **金额校验**：确保金额非负
- **汇率校验**：确保汇率大于0
- **币种校验**：验证币种代码的有效性
- **日期校验**：验证日期格式的正确性

## 使用方法

### 输入格式

需要提供 JSON 格式的分录数据：

```json
{
  "applicationCode": "RMS", // 财务中心编码
  "enter_CR": 123, // 交易币贷方
  "account_CR": 123, // 本位币贷方
  "exchangeRateVal": 1, // 汇率值
  "exchangeDate": "2026-03-07", // 汇率日期
  "enter_current": "RMB", // 交易币币种类型
  "account_current": "CNY" // 本位币币种类型
}
```

### 输出格式

返回 JSON 格式的校验结果：

```json
{
  "valid": true, // 是否校验通过
  "errors": [], // 错误信息列表
  "data": {} // 原始输入数据
}
```

## 执行命令

使用 `exec` 工具执行校验脚本：

```bash
python3 nanobot/skills/ledger-validation/scripts/validate_ledger.py '{"applicationCode": "RMS", "enter_CR": 123, "account_CR": 123, "exchangeRateVal": 1, "exchangeDate": "2026-03-07", "enter_current": "RMB", "account_current": "CNY"}'
```

## 校验规则

1. **金额校验**：
   - 金额必须是数字格式

2. **汇率校验**：
   - 汇率必须大于0
   - 汇率必须是数字格式

3. **币种校验**：
   - 交易币币种必须是有效的币种代码
   - 本位币币种必须是有效的币种代码
   - 支持的币种：RMB, CNY, USD, EUR, JPY, GBP, HKD, AUD, CAD, SGD, CHF, SEK, NZD, KRW, THB, MYR, IDR, INR, PHP, VND

4. **日期校验**：
   - 汇率日期格式必须为 YYYY-MM-DD

## 示例

### 示例1：有效数据

输入：
```json
{
  "applicationCode": "RMS",
  "enter_CR": 123,
  "account_CR": 123,
  "exchangeRateVal": 1,
  "exchangeDate": "2026-03-07",
  "enter_current": "RMB",
  "account_current": "CNY"
}
```

输出：
```json
{
  "valid": true,
  "errors": [],
  "data": {...}
}
```

### 示例2：无效数据

输入：
```json
{
  "applicationCode": "RMS",
  "enter_CR": -123,
  "account_CR": 123,
  "exchangeRateVal": 0,
  "exchangeDate": "2026-03-07",
  "enter_current": "INVALID",
  "account_current": "CNY"
}
```

输出：
```json
{
  "valid": false,
  "errors": [
    "交易币贷方金额不能为负数",
    "汇率必须大于0",
    "无效的交易币币种: INVALID"
  ],
  "data": {...}
}
```

## 错误处理

脚本会对以下情况进行错误处理：

- 缺少必要字段
- 金额格式错误
- 汇率格式错误或值无效
- 币种代码无效
- 日期格式错误

所有错误都会以清晰的中文消息返回，便于用户理解和修正。