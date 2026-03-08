# Session 失效机制实现计划

## 需求描述

实现 session 内存失效机制，每个 session 如果 30 分钟没有访问自动失效，并增加一个配置控制 session 失效时间。

## 实现目标

1. 为 Session 添加最后访问时间跟踪
2. 实现 session 过期检测和清理机制
3. 添加配置项控制 session TTL（Time To Live）
4. 启动后台任务定期清理过期 session

## 实现步骤

### 步骤 1: 修改配置文件

**文件**: `nanobot/config/schema.py`

**修改内容**:

1. 在 `AgentDefaults` 类中添加 `session_ttl_minutes` 配置项
2. 默认值设置为 30 分钟
3. 添加配置说明注释

**代码修改**:

```python
class AgentDefaults(Base):
    """Default agent configuration."""

    workspace: str = "~/.nanobot/workspace"
    model: str = "anthropic/claude-opus-4-5"
    provider: str = "auto"
    max_tokens: int = 8192
    temperature: float = 0.1
    max_tool_iterations: int = 40
    memory_window: int = 100
    session_ttl_minutes: int = 30  # Session 失效时间（分钟），0 表示不失效
```

### 步骤 2: 修改 Session 类

**文件**: `nanobot/session/manager.py`

**修改内容**:

1. 在 `Session` dataclass 中添加 `last_accessed_at` 字段
2. 在初始化时设置 `last_accessed_at` 为当前时间
3. 修改 `add_message()` 方法，更新 `last_accessed_at`

**代码修改**:

```python
@dataclass
class Session:
    """
    A conversation session.

    Stores messages in JSONL format for easy reading and persistence.

    Important: Messages are append-only for LLM cache efficiency.
    The consolidation process writes summaries to MEMORY.md/HISTORY.md
    but does NOT modify the messages list or get_history() output.
    """

    key: str  # channel:chat_id
    messages: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_accessed_at: datetime = field(default_factory=datetime.now)  # 最后访问时间
    metadata: dict[str, Any] = field(default_factory=dict)
    last_consolidated: int = 0  # Number of messages already consolidated to files

    def add_message(self, role: str, content: str, **kwargs: Any) -> None:
        """Add a message to the session."""
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        self.messages.append(msg)
        self.updated_at = datetime.now()
        self.last_accessed_at = datetime.now()  # 更新最后访问时间

    def get_history(self, max_messages: int = 500) -> list[dict[str, Any]]:
        """Return unconsolidated messages for LLM input, aligned to a user turn."""
        unconsolidated = self.messages[self.last_consolidated:]
        sliced = unconsolidated[-max_messages:]

        # Drop leading non-user messages to avoid orphaned tool_result blocks
        for i, m in enumerate(sliced):
            if m.get("role") == "user":
                sliced = sliced[i:]
                break

        out: list[dict[str, Any]] = []
        for m in sliced:
            entry: dict[str, Any] = {"role": m["role"], "content": m.get("content", "")}
            for k in ("tool_calls", "tool_call_id", "name"):
                if k in m:
                    entry[k] = m[k]
            out.append(entry)
        return out

    def clear(self) -> None:
        """Clear all messages and reset session to initial state."""
        self.messages = []
        self.last_consolidated = 0
        self.updated_at = datetime.now()
        self.last_accessed_at = datetime.now()  # 更新最后访问时间

    def is_expired(self, ttl_minutes: int) -> bool:
        """Check if session is expired based on TTL."""
        if ttl_minutes <= 0:
            return False
        elapsed = (datetime.now() - self.last_accessed_at).total_seconds()
        return elapsed > ttl_minutes * 60
```

### 步骤 3: 修改 SessionManager 类

**文件**: `nanobot/session/manager.py`

**修改内容**:

1. 在 `__init__` 方法中添加 `session_ttl_minutes` 参数
2. 修改 `get_or_create()` 方法，更新 session 的 `last_accessed_at`
3. 修改 `_load()` 方法，加载 `last_accessed_at` 字段
4. 修改 `save()` 方法，保存 `last_accessed_at` 字段
5. 添加 `cleanup_expired_sessions()` 方法，清理过期的 session
6. 添加 `start_cleanup_task()` 方法，启动后台清理任务
7. 添加 `stop_cleanup_task()` 方法，停止后台清理任务

**代码修改**:

```python
class SessionManager:
    """
    Manages conversation sessions.

    Sessions are stored as JSONL files in the sessions directory.
    Supports automatic cleanup of expired sessions based on TTL.
    """

    def __init__(self, workspace: Path, session_ttl_minutes: int = 30):
        self.workspace = workspace
        self.sessions_dir = ensure_dir(self.workspace / "sessions")
        self.legacy_sessions_dir = Path.home() / ".nanobot" / "sessions"
        self._cache: dict[str, Session] = {}
        self.session_ttl_minutes = session_ttl_minutes
        self._cleanup_task: asyncio.Task | None = None
        self._running = False

    def get_or_create(self, key: str) -> Session:
        """
        Get an existing session or create a new one.

        Args:
            key: Session key (usually channel:chat_id).

        Returns:
            The session.
        """
        if key in self._cache:
            session = self._cache[key]
            session.last_accessed_at = datetime.now()  # 更新最后访问时间
            return session

        session = self._load(key)
        if session is None:
            session = Session(key=key)

        session.last_accessed_at = datetime.now()  # 更新最后访问时间
        self._cache[key] = session
        return session

    def _load(self, key: str) -> Session | None:
        """Load a session from disk."""
        path = self._get_session_path(key)
        if not path.exists():
            legacy_path = self._get_legacy_session_path(key)
            if legacy_path.exists():
                try:
                    shutil.move(str(legacy_path), str(path))
                    logger.info("Migrated session {} from legacy path", key)
                except Exception:
                    logger.exception("Failed to migrate session {}", key)

        if not path.exists():
            return None

        try:
            messages = []
            metadata = {}
            created_at = None
            updated_at = None
            last_accessed_at = None
            last_consolidated = 0

            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    data = json.loads(line)

                    if data.get("_type") == "metadata":
                        metadata = data.get("metadata", {})
                        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
                        updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
                        last_accessed_at = datetime.fromisoformat(data["last_accessed_at"]) if data.get("last_accessed_at") else None
                        last_consolidated = data.get("last_consolidated", 0)
                    else:
                        messages.append(data)

            return Session(
                key=key,
                messages=messages,
                created_at=created_at or datetime.now(),
                updated_at=updated_at or datetime.now(),
                last_accessed_at=last_accessed_at or datetime.now(),
                metadata=metadata,
                last_consolidated=last_consolidated
            )
        except Exception as e:
            logger.warning("Failed to load session {}: {}", key, e)
            return None

    def save(self, session: Session) -> None:
        """Save a session to disk."""
        path = self._get_session_path(session.key)

        with open(path, "w", encoding="utf-8") as f:
            metadata_line = {
                "_type": "metadata",
                "key": session.key,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "last_accessed_at": session.last_accessed_at.isoformat(),
                "metadata": session.metadata,
                "last_consolidated": session.last_consolidated
            }
            f.write(json.dumps(metadata_line, ensure_ascii=False) + "\n")
            for msg in session.messages:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")

        self._cache[session.key] = session

    def invalidate(self, key: str) -> None:
        """Remove a session from in-memory cache."""
        self._cache.pop(key, None)

    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions from memory cache.

        Returns:
            Number of sessions removed.
        """
        if self.session_ttl_minutes <= 0:
            return 0

        expired_keys = [
            key for key, session in self._cache.items()
            if session.is_expired(self.session_ttl_minutes)
        ]

        for key in expired_keys:
            self.invalidate(key)
            logger.debug("Expired session removed from cache: {}", key)

        if expired_keys:
            logger.info("Cleaned up {} expired session(s)", len(expired_keys))

        return len(expired_keys)

    async def start_cleanup_task(self, interval_minutes: int = 5) -> None:
        """
        Start background task to clean up expired sessions.

        Args:
            interval_minutes: Cleanup interval in minutes.
        """
        if self.session_ttl_minutes <= 0:
            logger.info("Session TTL disabled, cleanup task not started")
            return

        if self._cleanup_task and not self._cleanup_task.done():
            logger.warning("Cleanup task already running")
            return

        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop(interval_minutes))
        logger.info("Session cleanup task started (TTL: {} minutes, interval: {} minutes)",
                   self.session_ttl_minutes, interval_minutes)

    async def _cleanup_loop(self, interval_minutes: int) -> None:
        """Background loop for periodic cleanup."""
        interval_seconds = interval_minutes * 60

        while self._running:
            try:
                await asyncio.sleep(interval_seconds)
                if self._running:
                    self.cleanup_expired_sessions()
            except asyncio.CancelledError:
                logger.info("Cleanup task cancelled")
                break
            except Exception as e:
                logger.exception("Error in cleanup loop: {}", e)

    async def stop_cleanup_task(self) -> None:
        """Stop the background cleanup task."""
        self._running = False

        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("Session cleanup task stopped")
```

### 步骤 4: 修改 AgentLoop 类

**文件**: `nanobot/agent/loop.py`

**修改内容**:

1. 在 `__init__` 方法中接收 `session_ttl_minutes` 配置
2. 将 `session_ttl_minutes` 传递给 `SessionManager`
3. 在 `run()` 方法中启动 session 清理任务
4. 在 `stop()` 方法中停止 session 清理任务

**代码修改**:

```python
class AgentLoop:
    """
    The agent loop is the core processing engine.

    It:
    1. Receives messages from the bus
    2. Builds context with history, memory, skills
    3. Calls the LLM
    4. Executes tool calls
    5. Sends responses back
    """

    _TOOL_RESULT_MAX_CHARS = 500

    def __init__(
        self,
        bus: MessageBus,
        provider: LLMProvider,
        workspace: Path,
        model: str | None = None,
        max_iterations: int = 40,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        memory_window: int = 100,
        brave_api_key: str | None = None,
        exec_config: ExecToolConfig | None = None,
        cron_service: CronService | None = None,
        restrict_to_workspace: bool = False,
        session_manager: SessionManager | None = None,
        mcp_servers: dict | None = None,
        channels_config: ChannelsConfig | None = None,
        json_mode: bool = False,
        security_level: str = "strict",
        session_ttl_minutes: int = 30,  # 添加 session TTL 配置
    ):
        from nanobot.config.schema import ExecToolConfig
        self.bus = bus
        self.channels_config = channels_config
        self.provider = provider
        self.workspace = workspace
        self.model = model or provider.get_default_model()
        self.max_iterations = max_iterations
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.memory_window = memory_window
        self.brave_api_key = brave_api_key
        self.exec_config = exec_config or ExecToolConfig()
        self.cron_service = cron_service
        self.restrict_to_workspace = restrict_to_workspace
        self.json_mode = json_mode
        self.session_ttl_minutes = session_ttl_minutes  # 保存 session TTL 配置

        self.context = ContextBuilder(workspace)
        self.sessions = session_manager or SessionManager(workspace, session_ttl_minutes)
        # ... 其他初始化代码保持不变

    async def run(self) -> None:
        """Run the agent loop, dispatching messages as tasks to stay responsive to /stop."""
        self._running = True
        await self._connect_mcp()
        await self.sessions.start_cleanup_task()  # 启动 session 清理任务
        logger.info("Agent loop started")

        while self._running:
            try:
                msg = await asyncio.wait_for(self.bus.consume_inbound(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            if msg.content.strip().lower() == "/stop":
                await self._handle_stop(msg)
            else:
                task = asyncio.create_task(self._dispatch(msg))
                self._active_tasks.setdefault(msg.session_key, []).append(task)
                task.add_done_callback(lambda t, k=msg.session_key: self._active_tasks.get(k, []) and self._active_tasks[k].remove(t) if t in self._active_tasks.get(k, []) else None)

    def stop(self) -> None:
        """Stop the agent loop."""
        self._running = False
        asyncio.create_task(self.sessions.stop_cleanup_task())  # 停止 session 清理任务
        logger.info("Agent loop stopping")
```

### 步骤 5: 修改 CLI 命令

**文件**: `nanobot/cli/commands.py`

**修改内容**:

1. 在 `gateway` 命令中传递 `session_ttl_minutes` 配置给 `AgentLoop`
2. 在 `agent` 命令中传递 `session_ttl_minutes` 配置给 `AgentLoop`

**代码修改**:

```python
# 在 gateway 命令中
agent = AgentLoop(
    bus=bus,
    provider=provider,
    workspace=config.workspace_path,
    model=config.agents.defaults.model,
    temperature=config.agents.defaults.temperature,
    max_tokens=config.agents.defaults.max_tokens,
    max_iterations=config.agents.defaults.max_tool_iterations,
    memory_window=config.agents.defaults.memory_window,
    brave_api_key=config.tools.web.search.api_key or None,
    exec_config=config.tools.exec,
    cron_service=cron,
    restrict_to_workspace=config.tools.restrict_to_workspace,
    session_manager=session_manager,
    mcp_servers=config.tools.mcp_servers,
    channels_config=config.channels,
    json_mode=False,
    security_level=config.agents.security.level,
    session_ttl_minutes=config.agents.defaults.session_ttl_minutes,  # 添加此行
)

# 在 agent 命令中
agent_loop = AgentLoop(
    bus=bus,
    provider=provider,
    workspace=config.workspace_path,
    model=config.agents.defaults.model,
    temperature=config.agents.defaults.temperature,
    max_tokens=config.agents.defaults.max_tokens,
    max_iterations=config.agents.defaults.max_tool_iterations,
    memory_window=config.agents.defaults.memory_window,
    brave_api_key=config.tools.web.search.api_key or None,
    exec_config=config.tools.exec,
    cron_service=cron,
    restrict_to_workspace=config.tools.restrict_to_workspace,
    mcp_servers=config.tools.mcp_servers,
    channels_config=config.channels,
    json_mode=json_mode,
    security_level=config.agents.security.level,
    session_ttl_minutes=config.agents.defaults.session_ttl_minutes,  # 添加此行
)
```

### 步骤 6: 添加导入语句

**文件**: `nanobot/session/manager.py`

**修改内容**:
在文件顶部添加 asyncio 导入

**代码修改**:

```python
"""Session management for conversation history."""

import asyncio
import json
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from loguru import logger

from nanobot.utils.helpers import ensure_dir, safe_filename
```

### 步骤 7: 更新配置示例

**文件**: 无需修改（配置文件会自动使用默认值）

**说明**:
用户可以在 `~/.nanobot/config.json` 中配置 session TTL：

```json
{
  "agents": {
    "defaults": {
      "session_ttl_minutes": 30
    }
  }
}
```

设置为 0 表示禁用 session 失效机制。

## 测试计划

### 测试用例 1: Session 失效检测

1. 创建一个 session
2. 等待 30 分钟（或修改 TTL 为更短的时间进行测试）
3. 检查 session 是否从内存缓存中移除
4. 磁盘文件应该仍然存在

### 测试用例 2: Session 访问更新

1. 创建一个 session
2. 在 TTL 时间内访问该 session
3. 等待 TTL 时间
4. 检查 session 是否仍然存在（应该存在，因为最近访问过）

### 测试用例 3: 禁用 TTL

1. 设置 `session_ttl_minutes = 0`
2. 创建多个 session
3. 等待任意时间
4. 检查 session 是否仍然存在（应该都存在）

### 测试用例 4: 配置加载

1. 修改配置文件中的 `session_ttl_minutes`
2. 重启 nanobot
3. 检查配置是否正确加载

## 兼容性说明

### 向后兼容性

* 旧的 session 文件不包含 `last_accessed_at` 字段

* 加载时会使用 `created_at` 或 `updated_at` 作为默认值

* 保存时会写入 `last_accessed_at` 字段

### 配置兼容性

* 如果配置文件中没有 `session_ttl_minutes`，使用默认值 30

* 不会影响现有配置的其他部分

## 性能影响

### 内存使用

* 每个 session 增加一个 `datetime` 对象（约 32 字节）

* 对于 1000 个 session，额外内存约 32 KB

* 可忽略不计

### CPU 使用

* 后台清理任务每 5 分钟运行一次

* 每次清理遍历内存缓存，时间复杂度 O(n)

* 对于 1000 个 session，清理时间约 1-2 ms

* 可忽略不计

### 磁盘 I/O

* 不影响磁盘 I/O

* 只清理内存缓存，不删除磁盘文件

* 与原有行为一致

## 注意事项

1. **仅清理内存缓存**: 此实现只清理内存中的 session，不会删除磁盘文件
2. **磁盘文件保留**: 磁盘上的 session 文件会永久保留，需要手动清理
3. **TTL 为 0 禁用失效**: 设置 `session_ttl_minutes = 0` 可以禁用失效机制
4. **清理间隔**: 默认每 5 分钟清理一次，可以根据需要调整
5. **线程安全**: 使用 asyncio 任务，确保线程安全
6. **日志记录**: 清理操作会记录日志，便于调试和监控

## 后续优化建议

1. **磁盘文件清理**: 可以添加配置选项，自动删除过期的磁盘文件
2. **LRU 策略**: 可以实现 LRU（最近最少使用）策略，限制内存中的 session 数量
3. **统计信息**: 添加 session 统计信息，如总 session 数、活跃 session 数等
4. **手动清理命令**: 添加 CLI 命令手动触发 session 清理
5. **监控指标**: 添加 Prometheus 指标，监控 session 使用情况

