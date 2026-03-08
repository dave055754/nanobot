# nanobot Session 创建机制分析

## 研究目标
分析 nanobot 在什么情况下会重新新建 session，包括 session 的创建、管理和清除机制。

## 核心发现

### 1. Session 的基本概念

**Session 定义** ([`Session`](file:///Users/dave/workspace/project/nanobot/nanobot/session/manager.py#L16-L32)):
- 存储对话历史的容器
- 以 JSONL 格式持久化到磁盘
- 包含 messages、metadata、created_at、updated_at 等字段
- 使用 `last_consolidated` 追踪已归档的消息数量

**Session Key 格式**:
- 默认格式：`{channel}:{chat_id}`（如 `telegram:123456789`）
- 可通过 `session_key_override` 覆盖

### 2. Session 创建的时机

#### 2.1 首次对话 - 创建新 Session

**触发条件**：
- 某个 `channel:chat_id` 组合第一次收到消息
- 磁盘上不存在对应的 session 文件

**代码位置**：
- [`SessionManager.get_or_create()`](file:///Users/dave/workspace/project/nanobot/nanobot/session/manager.py#L95-L113)
- [`AgentLoop._process_message()`](file:///Users/dave/workspace/project/nanobot/nanobot/agent/loop.py#L388-L389)

**流程**：
```python
def get_or_create(self, key: str) -> Session:
    if key in self._cache:
        return self._cache[key]

    session = self._load(key)
    if session is None:  # 磁盘上没有找到
        session = Session(key=key)  # 创建新 session

    self._cache[key] = session
    return session
```

#### 2.2 用户发送 `/new` 命令 - 清空并重用 Session

**触发条件**：
- 用户发送 `/new` 命令

**代码位置**：
- [`AgentLoop._process_message()`](file:///Users/dave/workspace/project/nanobot/nanobot/agent/loop.py#L393-L422)

**流程**：
1. 先将当前未归档的消息进行归档（写入 MEMORY.md/HISTORY.md）
2. 调用 `session.clear()` 清空所有消息
3. 重置 `last_consolidated` 为 0
4. 更新 `updated_at` 时间戳
5. 返回 "New session started." 消息

**关键代码**：
```python
if cmd == "/new":
    # 先归档当前历史
    snapshot = session.messages[session.last_consolidated:]
    if snapshot:
        temp = Session(key=session.key)
        temp.messages = list[dict[str, Any]](snapshot)
        if not await self._consolidate_memory(temp, archive_all=True):
            return OutboundMessage(..., content="Memory archival failed...")

    # 清空 session
    session.clear()
    self.sessions.save(session)
    self.sessions.invalidate(session.key)
    return OutboundMessage(..., content="New session started.")
```

#### 2.3 Session 文件不存在 - 创建新 Session

**触发条件**：
- Session 文件被删除或从未创建过
- 内存缓存中没有该 session

**代码位置**：
- [`SessionManager._load()`](file:///Users/dave/workspace/project/nanobot/nanobot/session/manager.py#L115-L160)

**流程**：
1. 尝试从 `workspace/sessions/` 目录加载 session 文件
2. 如果文件不存在，返回 `None`
3. `get_or_create()` 收到 `None` 后创建新 Session

### 3. Session 的持久化机制

**存储位置**：
- 主目录：`{workspace}/sessions/{safe_key}.jsonl`
- 兼容目录：`~/.nanobot/sessions/{safe_key}.jsonl`（旧版本）

**文件格式**：
- JSONL（每行一个 JSON 对象）
- 第一行是 metadata（包含 `_type: "metadata"`）
- 后续行是消息记录

**自动保存时机**：
- 每次消息处理完成后
- 调用 `SessionManager.save(session)`

### 4. Session 的生命周期

#### 4.1 创建阶段
- **触发**：首次收到某 channel:chat_id 的消息
- **动作**：创建新的 Session 对象，初始化空 messages 列表
- **持久化**：首次保存时写入磁盘

#### 4.2 使用阶段
- **触发**：每次收到消息
- **动作**：添加新消息到 messages 列表
- **持久化**：每次处理完消息后保存
- **归档**：当未归档消息数 >= memory_window 时自动归档

#### 4.3 清空阶段
- **触发**：用户发送 `/new` 命令
- **动作**：先归档历史，然后清空 messages
- **持久化**：保存清空后的 session

#### 4.4 失效阶段
- **触发**：调用 `SessionManager.invalidate(key)`
- **动作**：从内存缓存中移除，但磁盘文件保留
- **影响**：下次访问时会重新从磁盘加载

### 5. 特殊场景

#### 5.1 Cron 任务
- **Session Key**：`cron:{job_id}`
- **特点**：每个 cron 任务有独立的 session
- **代码位置**：[`commands.py:301`](file:///Users/dave/workspace/project/nanobot/nanobot/cli/commands.py#L301)

#### 5.2 Heartbeat 任务
- **Session Key**：`heartbeat`
- **特点**：所有 heartbeat 共享同一个 session
- **代码位置**：[`commands.py:344`](file:///Users/dave/workspace/project/nanobot/nanobot/cli/commands.py#L344)

#### 5.3 System 消息
- **Session Key**：从 chat_id 解析（格式：`channel:chat_id`）
- **特点**：用于系统触发的消息
- **代码位置**：[`loop.py:364-383`](file:///Users/dave/workspace/project/nanobot/nanobot/agent/loop.py#L364-L383)

### 6. Session 管理的关键方法

| 方法 | 位置 | 功能 |
|------|------|------|
| `get_or_create(key)` | [`SessionManager`](file:///Users/dave/workspace/project/nanobot/nanobot/session/manager.py#L95-L113) | 获取或创建 session |
| `_load(key)` | [`SessionManager`](file:///Users/dave/workspace/project/nanobot/nanobot/session/manager.py#L115-L160) | 从磁盘加载 session |
| `save(session)` | [`SessionManager`](file:///Users/dave/workspace/project/nanobot/nanobot/session/manager.py#L162-L179) | 保存 session 到磁盘 |
| `invalidate(key)` | [`SessionManager`](file:///Users/dave/workspace/project/nanobot/nanobot/session/manager.py#L181-L183) | 从缓存中移除 session |
| `clear()` | [`Session`](file:///Users/dave/workspace/project/nanobot/nanobot/session/manager.py#L65-L69) | 清空 session 的所有消息 |

### 7. 总结：新建 Session 的所有情况

1. **首次对话**：某个 `channel:chat_id` 组合第一次收到消息
2. **Session 文件丢失**：磁盘上的 session 文件被删除或从未创建
3. **手动清空**：用户发送 `/new` 命令（实际上是清空而非新建）
4. **缓存失效后重新加载**：调用 `invalidate()` 后再次访问
5. **特殊任务类型**：cron 任务、heartbeat 等使用独立的 session key

**注意**：
- `/new` 命令不会创建新的 session 对象，而是清空现有 session 的消息
- Session 的唯一标识是 `channel:chat_id`，只要这个组合不变，session 对象就会复用
- Session 的持久化是自动的，每次消息处理完成后都会保存
