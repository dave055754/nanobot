#### 学习Python
- 列表推导式  
```
enabled_tools = [tool for tool in tools if tool.enabled]
```
- 字典推导式
```
tool_dict = {tool.name: tool for tool in tools}
```
- 生成器 yield（按需逐个产出值，节省内存）
```
def message_generator(messages):
    for message in messages:
        yield message
```
- 装饰器 @decorator
```
def log_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args {args} and kwargs {kwargs}")
        return func(*args, **kwargs)
    return wrapper
```
- 上下文管理器 with
```
with open("file.txt", "r") as f:
    content = f.read()
```

- 函数式编程：map/filter/lambda
```
enabled_tools = list(map(lambda tool: tool.name, filter(lambda tool: tool.enabled, tools)))
```

- 异步编程：asyncio
```
import asyncio

async def async_task():
    await asyncio.sleep(1)
    return "Async task completed"
```

- 类型注解
```
def register_tool(tool: Tool) -> None:
    tools.append(tool)
```

- 面向对象编程
```
class Tool:
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
```

- 模块导入系统
```
import asyncio
```

- 异常处理
```
try:
    result = delete_user(123)
except PermissionError as e:
    print(e)
```

- 文件操作（pathlib）
```
from pathlib import Path

file_path = Path("file.txt")
content = file_path.read_text()
```
- 网络编程（asyncio）
```
import asyncio
import aiohttp

async def fetch_data(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```
- 配置管理（Pydantic）
```
from pydantic import BaseSettings

class Settings(BaseSettings):
    api_key: str
    api_secret: str

    class Config:
        env_file = ".env"
```

## 学习计划

### 第一阶段：基础巩固（1-2周）
1. **列表和字典推导式**
   - 查看 `nanobot/agent/loop.py` 中的列表操作
   - 练习：编写推导式来处理工具注册逻辑

2. **函数式编程**
   - 分析 `_register_default_tools` 方法中的函数应用
   - 练习：使用 `map` 和 `filter` 处理工具列表

### 第二阶段：中级特性（2-3周）
3. **生成器和迭代器**
   - 查找项目中使用 `yield` 的地方
   - 练习：实现一个生成器来处理消息流

4. **装饰器**
   - 查看工具注册相关代码中的装饰器使用
   - 练习：为函数添加日志装饰器

5. **上下文管理器**
   - 分析 `AsyncExitStack` 的使用
   - 练习：实现一个文件操作的上下文管理器

### 第三阶段：高级特性（3-4周）
6. **异步编程**
   - 深入研究 `async def` 和 `await` 的使用
   - 分析 `_connect_mcp` 方法中的异步逻辑
   - 练习：实现一个简单的异步任务队列

7. **类型注解**
   - 学习项目中的类型注解模式
   - 练习：为自己的代码添加类型注解

### 第四阶段：项目实践（持续）
- **模块开发**：尝试为 nanobot 添加一个新工具
- **技能开发**：创建一个简单的 nanobot 技能
- **配置管理**：学习使用 Pydantic 进行配置
- **测试**：为自己的代码编写单元测试