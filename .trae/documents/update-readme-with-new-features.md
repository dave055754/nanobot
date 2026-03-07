# 计划：将 ledger_validate 校验规则和 JSON 格式返回功能添加到 README

## 目标
将以下两个新功能添加到 README.md 文档中：
1. 新增的 ledger-validation 技能（分录明细账校验）
2. 新增的 JSON 模式返回功能

## 实施步骤

### 步骤 1：更新 News 部分
在 "📢 News" 部分添加最新功能更新
- 在 2026-02-24 的条目之前添加新的新闻条目
- 添加日期：2026-03-06
- 描述新增的 ledger-validation 技能和 JSON 模式功能

### 步骤 2：更新 CLI Reference 部分
在 "## CLI Reference" 表格中添加新的 `--json` 参数说明
- 在现有命令列表中添加：
  - `nanobot agent --json` - Enable JSON mode for structured output
- 保持现有格式和风格一致

### 步骤 3：添加 Skills 文档部分
在合适的位置添加关于 ledger-validation 技能的说明
- 可以在 "## 📁 Project Structure" 之前添加新的 "## 🎯 Skills" 部分
- 详细说明 ledger-validation 技能的功能和使用方法
- 包含输入输出格式示例

### 步骤 4：更新 Project Structure 部分
在 "## 📁 Project Structure" 部分更新 skills 目录说明
- 在 skills 部分的描述中明确提到 ledger-validation 技能

## 具体修改内容

### News 部分添加内容：
```markdown
- **2026-03-06** ✨ 新增 ledger-validation 技能（分录明细账校验）和 JSON 模式支持
```

### CLI Reference 部分添加内容：
```markdown
| Command | Description |
|---------|-------------|
| `nanobot agent --json` | Enable JSON mode for structured output |
```

### 新增 Skills 部分内容：
```markdown
## 🎯 Skills

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
```

## 验证要点

1. ✅ News 部分添加了新功能条目
2. ✅ CLI Reference 部分添加了 --json 参数说明
3. ✅ 新增了 Skills 部分并详细说明了 ledger-validation 技能
4. ✅ Project Structure 部分更新了 skills 目录说明
5. ✅ 所有修改保持了 README 的现有格式和风格
6. ✅ 代码示例使用了正确的语法高亮
7. ✅ JSON 示例格式正确且易读
