#!/usr/bin/env python3
"""
分录明细账校验脚本

输入格式:
{
    "applicationCode": "RMS", // 财务中心编码
    "enter_CR": 123, // 交易币贷方
    "account_CR": 123, // 本位币贷方
    "exchangeRateVal": 1, // 汇率值
    "exchangeDate": "2026-03-07", // 汇率日期
    "enter_current": "RMB", // 交易币币种类型
    "account_current": "CNY" // 本位币币种类型
}

返回格式:
{
    "valid": true/false,
    "errors": [],
    "data": {}
}
"""

import json
import sys
from datetime import datetime

# 有效的币种代码列表
VALID_CURRENCIES = {
    'RMB', 'CNY', 'USD', 'EUR', 'JPY', 'GBP', 'HKD', 'AUD', 'CAD', 'SGD',
    'CHF', 'SEK', 'NZD', 'KRW', 'THB', 'MYR', 'IDR', 'INR', 'PHP', 'VND'
}

def validate_ledger(data):
    """
    校验分录明细账数据
    
    Args:
        data: 包含分录数据的字典
        
    Returns:
        dict: 校验结果
    """
    errors = []
    
    # 校验必要字段
    required_fields = [
        'applicationCode', 'enter_CR', 'account_CR', 
        'exchangeRateVal', 'exchangeDate', 'enter_current', 'account_current'
    ]
    
    for field in required_fields:
        if field not in data:
            errors.append(f"缺少必要字段: {field}")
    
    if errors:
        return {
            "valid": False,
            "errors": errors,
            "data": data
        }
    
    # 校验金额
    try:
        enter_cr = float(data['enter_CR'])
        account_cr = float(data['account_CR'])
    except (ValueError, TypeError):
        errors.append("金额字段必须是数字")
    
    # 校验汇率
    try:
        exchange_rate = float(data['exchangeRateVal'])
        if exchange_rate <= 0:
            errors.append("汇率必须大于0")
    except (ValueError, TypeError):
        errors.append("汇率必须是数字")
    
    # 校验币种
    enter_current = data['enter_current']
    account_current = data['account_current']
    
    if enter_current not in VALID_CURRENCIES:
        errors.append(f"无效的交易币币种: {enter_current}")
    if account_current not in VALID_CURRENCIES:
        errors.append(f"无效的本位币币种: {account_current}")
    
    # 校验日期
    try:
        exchange_date = data['exchangeDate']
        # 尝试解析日期格式
        datetime.strptime(exchange_date, '%Y-%m-%d')
    except ValueError:
        errors.append("汇率日期格式无效，应为 YYYY-MM-DD")
    
    # 构建返回结果
    result = {
        "valid": len(errors) == 0,
        "errors": errors,
        "data": data
    }
    
    return result

def main():
    """
    主函数
    """
    if len(sys.argv) > 1:
        # 从命令行参数读取 JSON
        try:
            data = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            print(json.dumps({
                "valid": False,
                "errors": ["输入不是有效的 JSON 格式"],
                "data": {}
            }, ensure_ascii=False))
            return
    else:
        # 从标准输入读取 JSON
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError:
            print(json.dumps({
                "valid": False,
                "errors": ["输入不是有效的 JSON 格式"],
                "data": {}
            }, ensure_ascii=False))
            return
    
    # 执行校验
    result = validate_ledger(data)
    
    # 输出结果（紧凑 JSON 格式）
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
