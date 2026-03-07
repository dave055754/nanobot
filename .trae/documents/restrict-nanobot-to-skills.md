# 实现计划：nanobot 生产环境安全加固

## 需求概述

nanobot 在生产环境中运行时需要严格的安全限制：

1. **Python脚本白名单**：只能执行在 skill 中明确定义的 Python 脚本
2. **Shell命令黑名单**：禁止执行删除、更新等危险操作
3. **生产环境安全**：确保 nanobot 不能删除或修改其他文件和数据

### 安全目标

* ✅ 防止误删重要文件

* ✅ 防止未经授权的数据修改

* ✅ 限制执行范围在预定义的 skills 内

* ✅ 提供清晰的审计日志

* ✅ 支持只读模式（可选）

## 当前架构分析

### 关键组件

1. **SkillsLoader** (`nanobot/agent/skills.py`): 负责加载和管理 skills
2. **ExecTool** (`nanobot/agent/tools/shell.py`): 执行 shell 命令的工具
3. **AgentLoop** (`nanobot/agent/loop.py`): 处理消息和执行工具的核心循环
4. **ContextBuilder** (`nanobot/agent/context.py`): 构建系统提示词，包含 skills 信息

### Skills 结构

* Skills 位于 `nanobot/skills/*/SKILL.md`

* 每个 skill 包含 YAML frontmatter 和 markdown 指令

* Skills 提供如何使用特定工具的指导（如 `exec` 工具执行特定脚本）

### 当前问题

* `ExecTool` 可以执行任意 shell 命令（虽然有基础安全限制）

* 没有机制验证 Python 脚本是否来自 skill 定义

* 没有严格的删除/更新操作黑名单

* 缺少审计日志功能

* 文件操作工具（WriteFileTool、EditFileTool）没有额外的安全检查

* 用户可以请求执行任何命令，即使没有对应的 skill

### 安全风险分析

**高风险操作**：

* 删除文件：`rm`, `rmdir`, `del`, `unlink`

* 覆盖文件：`>`, `>>`, `tee`, `cp -f`

* 修改权限：`chmod`, `chown`

* 系统操作：`shutdown`, `reboot`, `format`

* 数据库操作：未经验证的 SQL 命令

* 包管理：`pip install`, `npm install`（可能引入恶意包）

**需要保护的资源**：

* 用户主目录外的文件

* 系统配置文件

* 数据库文件

* 生产数据

* 其他用户的文件

## 实施方案

### 方案概述

1. **创建 SkillCommandParser**: 解析 skills 中的命令定义，提取允许的 Python 脚本
2. **创建 SecurityGuard**: 统一的安全守卫，处理命令黑名单和白名单验证
3. **创建 AuditLogger**: 记录所有执行的命令和文件操作
4. **修改 ExecTool**: 集成安全守卫，添加严格的命令验证
5. **修改文件操作工具**: 添加额外的安全检查
6. **集成到 AgentLoop**: 在执行任何操作前进行安全验证
7. **配置选项**: 支持只读模式、严格模式等安全级别

### 安全级别

**Level 1 - 基础模式**（开发环境）：

* 允许执行 skill 中定义的命令

* 基础的危险命令黑名单

* 基本的审计日志

**Level 2 - 严格模式**（生产环境，默认）：

* 只允许执行 skill 中明确定义的 Python 脚本

* 严格的删除/更新操作黑名单

* 完整的审计日志

* 工作空间限制

**Level 3 - 只读模式**（最高安全）：

* 禁止所有写入操作

* 禁止所有修改操作

* 只允许读取和查询操作

### 详细步骤

#### 步骤 1: 创建 SecurityGuard（安全守卫）

**文件**: `nanobot/agent/security_guard.py`

**功能**:

* 统一的安全验证入口

* 命令黑名单管理

* Python 脚本白名单验证

* 安全级别控制

* 审计日志接口

**实现细节**:

```python
"""Security guard for nanobot operations."""

import re
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

class SecurityLevel(Enum):
    """Security levels for nanobot operations."""
    BASIC = "basic"      # Development: basic restrictions
    STRICT = "strict"    # Production: strict restrictions (default)
    READONLY = "readonly"  # Maximum security: read-only only

class SecurityGuard:
    """Security guard for validating operations."""

    # 危险命令黑名单（正则表达式）
    DANGEROUS_PATTERNS = [
        r'\brm\s+[-rf]+\b',           # rm -rf, rm -fr
        r'\brmdir\s+[/s]?\b',        # rmdir /s
        r'\bdel\s+[/fq]+\b',         # del /f, del /q
        r'(?:^|[;&|]\s*)format\b',   # format command
        r'\b(mkfs|diskpart)\b',      # disk operations
        r'\bdd\s+if=',               # dd command
        r'>\s*/dev/sd',              # write to disk
        r'\b(shutdown|reboot|poweroff|halt)\b',  # system power
        r':\(\)\s*\{.*\};\s*:',      # fork bomb
        r'\bchmod\s+777\b',          # dangerous chmod
        r'\bchown\b',                # chown
        r'\bsudo\b',                 # sudo (unless whitelisted)
        r'\bsu\b',                   # su
        r'\bmv\s+.*\s+/',           # move to root
        r'\bcp\s+.*\s+/',           # copy to root
        r'\b(pip|npm|yarn|gem)\s+install\b',  # package install
        r'\bapt-get\s+(install|remove|purge)\b',  # apt operations
        r'\byum\s+(install|remove)\b',  # yum operations
        r'\bbrew\s+(install|uninstall)\b',  # brew operations
        r'\b(python|node)\s+-m\s+pip\s+install\b',  # pip via python
        r'\bcurl\s+.*\|\s*(bash|sh|python|node)\b',  # pipe to shell
        r'\bwget\s+.*\|\s*(bash|sh|python|node)\b',  # wget pipe
    ]

    # 只读模式禁止的操作
    READONLY_BLOCKED_PATTERNS = [
        r'>',                         # redirect output
        r'>>',                        # append output
        r'\btee\b',                   # tee command
        r'\b(write|edit|modify|update|delete|remove)\b',  # obvious operations
        r'\b(mv|cp)\b',               # move/copy files
        r'\b(mkdir|touch)\b',         # create files/dirs
    ]

    def __init__(
        self,
        security_level: SecurityLevel = SecurityLevel.STRICT,
        workspace: Optional[Path] = None,
    ):
        self.security_level = security_level
        self.workspace = workspace
        self.python_script_whitelist: set[str] = set()
        self.allowed_tools: set[str] = set()
        self.skill_commands: dict[str, list[str]] = {}

    def set_python_script_whitelist(self, scripts: list[str]) -> None:
        """Set the whitelist of allowed Python scripts."""
        self.python_script_whitelist = set(scripts)

    def set_allowed_tools(self, tools: list[str]) -> None:
        """Set the list of allowed tools."""
        self.allowed_tools = set(tools)

    def set_skill_commands(self, commands: dict[str, list[str]]) -> None:
        """Set the commands defined in skills."""
        self.skill_commands = commands

    def is_command_safe(self, command: str) -> Tuple[bool, str]:
        """Check if a command is safe to execute.

        Args:
            command: The command to check

        Returns:
            Tuple of (is_safe, reason)
        """
        cmd_lower = command.lower().strip()

        # 检查只读模式
        if self.security_level == SecurityLevel.READONLY:
            for pattern in self.READONLY_BLOCKED_PATTERNS:
                if re.search(pattern, cmd_lower):
                    return False, f"Command blocked: Read-only mode forbids write operations"

        # 检查危险命令
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, cmd_lower):
                return False, f"Command blocked: Dangerous operation detected"

        # 检查 Python 脚本
        if cmd_lower.startswith('python') or cmd_lower.startswith('python3'):
            if self.security_level in [SecurityLevel.STRICT, SecurityLevel.READONLY]:
                if not self._is_python_script_allowed(command):
                    return False, f"Python script not in whitelist. Only scripts defined in skills are allowed."

        return True, ""

    def is_file_operation_safe(
        self,
        operation: str,
        file_path: str,
    ) -> Tuple[bool, str]:
        """Check if a file operation is safe.

        Args:
            operation: The operation type (read, write, delete, etc.)
            file_path: The file path to operate on

        Returns:
            Tuple of (is_safe, reason)
        """
        path = Path(file_path).resolve()

        # 只读模式禁止写入操作
        if self.security_level == SecurityLevel.READONLY:
            if operation in ['write', 'edit', 'delete', 'create']:
                return False, f"File operation blocked: Read-only mode forbids {operation} operations"

        # 检查工作空间限制
        if self.workspace:
            workspace_path = self.workspace.resolve()
            if path.is_absolute():
                if workspace_path not in path.parents and path != workspace_path:
                    return False, f"File operation blocked: Path outside workspace ({self.workspace})"

        # 检查危险路径
        dangerous_paths = [
            '/etc/', '/usr/', '/bin/', '/sbin/', '/lib/', '/sys/', '/proc/',
            '~/.ssh/', '~/.config/', '~/.gnupg/',
        ]
        for dangerous in dangerous_paths:
            if str(path).startswith(dangerous):
                return False, f"File operation blocked: Path in protected system directory"

        return True, ""

    def _is_python_script_allowed(self, command: str) -> bool:
        """Check if a Python script is in the whitelist."""
        # 提取脚本路径
        parts = command.split()
        for i, part in enumerate(parts):
            if part.endswith('.py'):
                script_path = Path(part).resolve()
                # 检查是否在白名单中
                for allowed in self.python_script_whitelist:
                    allowed_path = Path(allowed).resolve()
                    if script_path == allowed_path:
                        return True
        return False

    def get_security_summary(self) -> str:
        """Get a summary of current security settings."""
        lines = [
            f"Security Level: {self.security_level.value}",
            f"Python Scripts Whitelisted: {len(self.python_script_whitelist)}",
            f"Allowed Tools: {len(self.allowed_tools)}",
            f"Skills with Commands: {len(self.skill_commands)}",
        ]
        if self.workspace:
            lines.append(f"Workspace: {self.workspace}")
        return "\n".join(lines)
```

#### 步骤 2: 创建 AuditLogger（审计日志）

**文件**: `nanobot/agent/audit_logger.py`

**功能**:

* 记录所有执行的命令

* 记录所有文件操作

* 记录安全违规尝试

* 提供查询接口

**实现细节**:

```python
"""Audit logger for nanobot operations."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

class AuditLogger:
    """Audit logger for tracking nanobot operations."""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.audit_dir = workspace / "audit"
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.audit_file = self.audit_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"

    def log_command(
        self,
        command: str,
        allowed: bool,
        reason: str = "",
        skill_name: str = "",
    ) -> None:
        """Log a command execution attempt."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "command",
            "command": command,
            "allowed": allowed,
            "reason": reason,
            "skill_name": skill_name,
        }
        self._write_entry(entry)

    def log_file_operation(
        self,
        operation: str,
        file_path: str,
        allowed: bool,
        reason: str = "",
    ) -> None:
        """Log a file operation attempt."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "file_operation",
            "operation": operation,
            "file_path": file_path,
            "allowed": allowed,
            "reason": reason,
        }
        self._write_entry(entry)

    def log_security_violation(
        self,
        violation_type: str,
        details: str,
    ) -> None:
        """Log a security violation."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "security_violation",
            "violation_type": violation_type,
            "details": details,
        }
        self._write_entry(entry)

    def _write_entry(self, entry: dict) -> None:
        """Write an entry to the audit log."""
        with open(self.audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    def get_recent_violations(self, limit: int = 100) -> list[dict]:
        """Get recent security violations."""
        violations = []
        if not self.audit_file.exists():
            return violations

        with open(self.audit_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("type") == "security_violation":
                        violations.append(entry)
                        if len(violations) >= limit:
                            break
                except json.JSONDecodeError:
                    continue

        return violations
```

#### 步骤 3: 创建 SkillCommandParser（增强版）

**文件**: `nanobot/agent/skills_command_parser.py`

**功能**:

* 解析所有 skills 的 SKILL.md 文件

* 提取允许执行的 Python 脚本路径

* 提取允许的工具

* 支持多种命令格式

**实现细节**:

````python
"""Command parser for extracting allowed commands from skills."""

import json
import re
from pathlib import Path
from typing import Tuple

from nanobot.agent.skills import SkillsLoader


class SkillCommandParser:
    """Parser for extracting allowed commands from skills."""

    def __init__(self, skills_loader: SkillsLoader):
        self.skills_loader = skills_loader
        self.python_scripts: set[str] = set()
        self.allowed_tools: set[str] = set()
        self.skill_commands: dict[str, list[str]] = {}

    def parse_all_skills(self) -> None:
        """Parse all skills to extract allowed commands."""
        for skill in self.skills_loader.list_skills():
            self._parse_skill(skill["name"])

    def _parse_skill(self, skill_name: str) -> None:
        """Parse a single skill to extract commands."""
        content = self.skills_loader.load_skill(skill_name)
        if not content:
            return

        commands = []

        # 提取代码块中的命令
        code_blocks = re.findall(r'```bash\n(.*?)\n```', content, re.DOTALL)
        for block in code_blocks:
            commands.extend(self._extract_commands_from_block(block))

        # 提取 Python 脚本
        python_scripts = re.findall(r'(python3?\s+[\w/\-\.]+\.py)', content)
        for script in python_scripts:
            script_path = script.split()[-1]
            self.python_scripts.add(script_path)

        # 存储该 skill 的命令
        if commands:
            self.skill_commands[skill_name] = commands

        # 提取工具名称
        self._extract_tools_from_skill(skill_name, content)

    def _extract_commands_from_block(self, block: str) -> list[str]:
        """Extract commands from a code block."""
        commands = []
        for line in block.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                commands.append(line)
        return commands

    def _extract_tools_from_skill(self, skill_name: str, content: str) -> None:
        """Extract tool names from skill metadata."""
        meta = self.skills_loader.get_skill_metadata(skill_name)
        if meta:
            requires = meta.get('metadata', '{}')
            if isinstance(requires, str):
                try:
                    requires_data = json.loads(requires)
                    bins = requires_data.get('requires', {}).get('bins', [])
                    self.allowed_tools.update(bins)
                except json.JSONDecodeError:
                    pass

    def is_command_allowed(self, command: str) -> Tuple[bool, str]:
        """Check if a command is allowed to execute.

        Returns:
            Tuple of (is_allowed, skill_name)
        """
        command = command.strip()

        # 检查精确匹配
        for skill_name, commands in self.skill_commands.items():
            for cmd in commands:
                if command == cmd.strip():
                    return True, skill_name

        # 检查 Python 脚本
        if command.lower().startswith('python'):
            script_path = self._extract_python_script_path(command)
            if script_path and script_path in self.python_scripts:
                return True, "python_script"

        # 检查工具名称
        cmd_parts = command.split()
        if cmd_parts:
            tool = cmd_parts[0]
            if tool in self.allowed_tools:
                return True, f"tool:{tool}"

        return False, ""

    def _extract_python_script_path(self, command: str) -> str:
        """Extract Python script path from command."""
        parts = command.split()
        for part in parts:
            if part.endswith('.py'):
                return part
        return ""

    def get_python_scripts(self) -> list[str]:
        """Get list of allowed Python scripts."""
        return list(self.python_scripts)

    def get_allowed_tools(self) -> list[str]:
        """Get list of allowed tools."""
        return list(self.allowed_tools)

    def get_available_skills_summary(self) -> str:
        """Get a summary of available skills and their commands."""
        if not self.skill_commands:
            return "No skills available."

        lines = []
        for skill_name, commands in self.skill_commands.items():
            lines.append(f"\n## {skill_name}")
            for cmd in commands[:5]:
                lines.append(f"  - {cmd}")
            if len(commands) > 5:
                lines.append(f"  - ... and {len(commands) - 5} more commands")

        if self.python_scripts:
            lines.append(f"\n## Allowed Python Scripts")
            for script in list(self.python_scripts)[:5]:
                lines.append(f"  - {script}")
            if len(self.python_scripts) > 5:
                lines.append(f"  - ... and {len(self.python_scripts) - 5} more scripts")

        return "\n".join(lines)
````

#### 步骤 4: 修改 ExecTool

**文件**: `nanobot/agent/tools/shell.py`

**修改内容**:

1. 添加 `SecurityGuard` 和 `AuditLogger` 依赖注入
2. 在 `execute` 方法中添加安全验证
3. 记录所有命令执行尝试
4. 如果命令不安全，返回错误

**修改点**:

```python
"""Shell execution tool with security enhancements."""

import asyncio
import os
import re
from pathlib import Path
from typing import Any, Optional

from nanobot.agent.tools.base import Tool
from nanobot.agent.security_guard import SecurityGuard, SecurityLevel
from nanobot.agent.audit_logger import AuditLogger


class ExecTool(Tool):
    """Tool to execute shell commands with security restrictions."""

    def __init__(
        self,
        timeout: int = 60,
        working_dir: str | None = None,
        deny_patterns: list[str] | None = None,
        allow_patterns: list[str] | None = None,
        restrict_to_workspace: bool = False,
        path_append: str = "",
        security_guard: Optional[SecurityGuard] = None,
        audit_logger: Optional[AuditLogger] = None,
    ):
        self.timeout = timeout
        self.working_dir = working_dir
        self.deny_patterns = deny_patterns or []
        self.allow_patterns = allow_patterns or []
        self.restrict_to_workspace = restrict_to_workspace
        self.path_append = path_append
        self.security_guard = security_guard
        self.audit_logger = audit_logger

    @property
    def name(self) -> str:
        return "exec"

    @property
    def description(self) -> str:
        return "Execute a shell command and return its output. Security restrictions apply."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute"
                },
                "working_dir": {
                    "type": "string",
                    "description": "Optional working directory for the command"
                }
            },
            "required": ["command"]
        }

    async def execute(self, command: str, working_dir: str | None = None, **kwargs: Any) -> str:
        cwd = working_dir or self.working_dir or os.getcwd()

        # 安全验证
        if self.security_guard:
            is_safe, reason = self.security_guard.is_command_safe(command)
            if not is_safe:
                if self.audit_logger:
                    self.audit_logger.log_command(
                        command=command,
                        allowed=False,
                        reason=reason,
                    )
                return f"Error: {reason}"

        # 基础安全守卫（向后兼容）
        guard_error = self._guard_command(command, cwd)
        if guard_error:
            if self.audit_logger:
                self.audit_logger.log_command(
                    command=command,
                    allowed=False,
                    reason=guard_error,
                )
            return guard_error

        # 记录允许的命令
        if self.audit_logger:
            self.audit_logger.log_command(
                command=command,
                allowed=True,
            )

        env = os.environ.copy()
        if self.path_append:
            env["PATH"] = env.get("PATH", "") + os.pathsep + self.path_append

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    pass
                result = f"Error: Command timed out after {self.timeout} seconds"
                if self.audit_logger:
                    self.audit_logger.log_command(
                        command=command,
                        allowed=True,
                        reason=result,
                    )
                return result

            output_parts = []

            if stdout:
                output_parts.append(stdout.decode("utf-8", errors="replace"))

            if stderr:
                stderr_text = stderr.decode("utf-8", errors="replace")
                if stderr_text.strip():
                    output_parts.append(f"STDERR:\n{stderr_text}")

            if process.returncode != 0:
                output_parts.append(f"\nExit code: {process.returncode}")

            result = "\n".join(output_parts) if output_parts else "(no output)"

            max_len = 10000
            if len(result) > max_len:
                result = result[:max_len] + f"\n... (truncated, {len(result) - max_len} more chars)"

            return result

        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            if self.audit_logger:
                self.audit_logger.log_command(
                    command=command,
                    allowed=True,
                    reason=error_msg,
                )
            return error_msg

    def _guard_command(self, command: str, cwd: str) -> str | None:
        """Best-effort safety guard for potentially destructive commands."""
        cmd = command.strip()
        lower = cmd.lower()

        for pattern in self.deny_patterns:
            if re.search(pattern, lower):
                return "Error: Command blocked by safety guard (dangerous pattern detected)"

        if self.allow_patterns:
            if not any(re.search(p, lower) for p in self.allow_patterns):
                return "Error: Command blocked by safety guard (not in allowlist)"

        if self.restrict_to_workspace:
            if "..\\" in cmd or "../" in cmd:
                return "Error: Command blocked by safety guard (path traversal detected)"

            cwd_path = Path(cwd).resolve()

            win_paths = re.findall(r"[A-Za-z]:\\[^\\\"']+", cmd)
            posix_paths = re.findall(r"(?:^|[\s|>])(/[^\s\"'>]+)", cmd)

            for raw in win_paths + posix_paths:
                try:
                    p = Path(raw.strip()).resolve()
                except Exception:
                    continue
                if p.is_absolute() and cwd_path not in p.parents and p != cwd_path:
                    return "Error: Command blocked by safety guard (path outside working dir)"

        return None
```

#### 步骤 5: 修改文件操作工具

**文件**: `nanobot/agent/tools/filesystem.py`

**修改内容**:

1. 添加 `SecurityGuard` 和 `AuditLogger` 依赖注入
2. 在写入、编辑、删除操作前进行安全验证
3. 记录所有文件操作

**修改点**:

```python
"""Filesystem tools with security enhancements."""

from pathlib import Path
from typing import Any, Optional

from nanobot.agent.tools.base import Tool
from nanobot.agent.security_guard import SecurityGuard
from nanobot.agent.audit_logger import AuditLogger


class WriteFileTool(Tool):
    """Tool to write files with security restrictions."""

    def __init__(
        self,
        workspace: Path,
        allowed_dir: Path | None = None,
        security_guard: Optional[SecurityGuard] = None,
        audit_logger: Optional[AuditLogger] = None,
    ):
        self.workspace = workspace
        self.allowed_dir = allowed_dir
        self.security_guard = security_guard
        self.audit_logger = audit_logger

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file. Security restrictions apply."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to write"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        }

    async def execute(self, path: str, content: str, **kwargs: Any) -> str:
        # 安全验证
        if self.security_guard:
            is_safe, reason = self.security_guard.is_file_operation_safe(
                operation="write",
                file_path=path,
            )
            if not is_safe:
                if self.audit_logger:
                    self.audit_logger.log_file_operation(
                        operation="write",
                        file_path=path,
                        allowed=False,
                        reason=reason,
                    )
                return f"Error: {reason}"

        # 记录操作
        if self.audit_logger:
            self.audit_logger.log_file_operation(
                operation="write",
                file_path=path,
                allowed=True,
            )

        # 执行写入
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {path}"


class EditFileTool(Tool):
    """Tool to edit files with security restrictions."""

    def __init__(
        self,
        workspace: Path,
        allowed_dir: Path | None = None,
        security_guard: Optional[SecurityGuard] = None,
        audit_logger: Optional[AuditLogger] = None,
    ):
        self.workspace = workspace
        self.allowed_dir = allowed_dir
        self.security_guard = security_guard
        self.audit_logger = audit_logger

    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return "Edit a file by searching and replacing. Security restrictions apply."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to edit"},
                "old_str": {"type": "string", "description": "String to search for"},
                "new_str": {"type": "string", "description": "Replacement string"}
            },
            "required": ["path", "old_str", "new_str"]
        }

    async def execute(self, path: str, old_str: str, new_str: str, **kwargs: Any) -> str:
        # 安全验证
        if self.security_guard:
            is_safe, reason = self.security_guard.is_file_operation_safe(
                operation="edit",
                file_path=path,
            )
            if not is_safe:
                if self.audit_logger:
                    self.audit_logger.log_file_operation(
                        operation="edit",
                        file_path=path,
                        allowed=False,
                        reason=reason,
                    )
                return f"Error: {reason}"

        # 记录操作
        if self.audit_logger:
            self.audit_logger.log_file_operation(
                operation="edit",
                file_path=path,
                allowed=True,
            )

        # 执行编辑
        file_path = Path(path)
        content = file_path.read_text(encoding="utf-8")
        if old_str not in content:
            return f"Error: '{old_str}' not found in {path}"
        content = content.replace(old_str, new_str)
        file_path.write_text(content, encoding="utf-8")
        return f"Successfully edited {path}"
```

#### 步骤 6: 修改 AgentLoop 初始化

**文件**: `nanobot/agent/loop.py`

**修改内容**:

1. 创建 `SecurityGuard`、`AuditLogger` 和 `SkillCommandParser` 实例
2. 将安全组件传递给所有工具
3. 添加配置选项支持

**修改点**:

```python
from nanobot.agent.security_guard import SecurityGuard, SecurityLevel
from nanobot.agent.audit_logger import AuditLogger
from nanobot.agent.skills_command_parser import SkillCommandParser

class AgentLoop:
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
        security_level: str = "strict",  # 新增
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

        self.context = ContextBuilder(workspace)
        self.sessions = session_manager or SessionManager(workspace)
        self.tools = ToolRegistry()

        # 初始化安全组件
        self.security_level = SecurityLevel(security_level.lower())
        self.security_guard = SecurityGuard(
            security_level=self.security_level,
            workspace=workspace,
        )
        self.audit_logger = AuditLogger(workspace)

        # 初始化技能命令解析器
        self.command_parser = SkillCommandParser(self.context.skills)
        self.command_parser.parse_all_skills()

        # 配置安全守卫
        self.security_guard.set_python_script_whitelist(
            self.command_parser.get_python_scripts()
        )
        self.security_guard.set_allowed_tools(
            self.command_parser.get_allowed_tools()
        )
        self.security_guard.set_skill_commands(
            self.command_parser.skill_commands
        )

        self.subagents = SubagentManager(
            provider=provider,
            workspace=workspace,
            bus=bus,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            brave_api_key=brave_api_key,
            exec_config=self.exec_config,
            restrict_to_workspace=restrict_to_workspace,
        )

        self._running = False
        self._mcp_servers = mcp_servers or {}
        self._mcp_stack: AsyncExitStack | None = None
        self._mcp_connected = False
        self._mcp_connecting = False
        self._consolidating: set[str] = set()
        self._consolidation_tasks: set[asyncio.Task] = set()
        self._consolidation_locks: dict[str, asyncio.Lock] = {}
        self._active_tasks: dict[str, list[asyncio.Task]] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register the default set of tools."""
        allowed_dir = self.workspace if self.restrict_to_workspace else None

        # 注册文件操作工具（带安全检查）
        for cls in (ReadFileTool, WriteFileTool, EditFileTool, ListDirTool):
            self.tools.register(cls(
                workspace=self.workspace,
                allowed_dir=allowed_dir,
                security_guard=self.security_guard,
                audit_logger=self.audit_logger,
            ))

        # 注册执行工具（带安全检查）
        self.tools.register(ExecTool(
            working_dir=str(self.workspace),
            timeout=self.exec_config.timeout,
            restrict_to_workspace=self.restrict_to_workspace,
            path_append=self.exec_config.path_append,
            security_guard=self.security_guard,
            audit_logger=self.audit_logger,
        ))

        # 注册其他工具
        self.tools.register(WebSearchTool(api_key=self.brave_api_key))
        self.tools.register(WebFetchTool())
        self.tools.register(MessageTool(send_callback=self.bus.publish_outbound))
        self.tools.register(SpawnTool(manager=self.subagents))
        if self.cron_service:
            self.tools.register(CronTool(self.cron_service))
```

#### 步骤 7: 添加配置选项

**文件**: `nanobot/config/schema.py`

**修改内容**:
添加安全级别配置选项

**修改点**:

```python
class SecurityConfig(BaseModel):
    """Security configuration for nanobot."""

    level: str = Field(
        default="strict",
        description="Security level: basic, strict (default), or readonly"
    )
    enable_audit_log: bool = Field(
        default=True,
        description="Enable audit logging for all operations"
    )
    audit_log_dir: str = Field(
        default="audit",
        description="Directory for audit logs"
    )

class AgentsConfig(BaseModel):
    """Agent configuration."""

    defaults: DefaultsConfig = Field(default_factory=DefaultsConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)  # 新增
```

**配置文件示例** (`~/.nanobot/config.json`):

```json
{
  "agents": {
    "defaults": {
      "model": "openai/gpt-4",
      "temperature": 0.1,
      "max_tokens": 4096
    },
    "security": {
      "level": "strict",
      "enable_audit_log": true,
      "audit_log_dir": "audit"
    }
  }
}
```

#### 步骤 8: 测试和验证

**测试场景**:

1. **测试 Python 脚本白名单**:

   * ✅ 执行 skill 中定义的 Python 脚本（应该成功）

   * ❌ 执行不在白名单中的 Python 脚本（应该失败）

2. **测试危险命令黑名单**:

   * ❌ 执行删除命令 `rm -rf`（应该失败）

   * ❌ 执行格式化命令 `format`（应该失败）

   * ❌ 执行包安装 `pip install`（应该失败）

3. **测试文件操作安全**:

   * ✅ 读取工作空间内的文件（应该成功）

   * ❌ 写入系统目录（应该失败）

   * ❌ 删除工作空间外的文件（应该失败）

4. **测试只读模式**:

   * ✅ 读取文件（应该成功）

   * ❌ 写入文件（应该失败）

   * ❌ 编辑文件（应该失败）

5. **测试审计日志**:

   * 验证所有操作都被记录

   * 验证安全违规被记录

   * 验证日志格式正确

**测试命令示例**:

```bash
# 测试 1: Python 脚本白名单
# 应该成功（在 skill 中定义）
python3 nanobot/skills/ledger-validation/scripts/validate_ledger.py '{"applicationCode": "RMS", "enter_CR": 123, "account_CR": 123, "exchangeRateVal": 1, "exchangeDate": "2026-03-07", "enter_current": "RMB", "account_current": "CNY"}'

# 应该失败（不在白名单中）
python3 /tmp/malicious_script.py

# 测试 2: 危险命令黑名单
# 应该失败
rm -rf /important/data
format c:
pip install malicious-package

# 测试 3: 文件操作安全
# 应该成功
write_file /workspace/test.txt "Hello"

# 应该失败
write_file /etc/passwd "malicious"
edit_file /etc/hosts "127.0.0.1 malicious.com"

# 测试 4: 只读模式（security_level=readonly）
# 应该成功
read_file /workspace/test.txt

# 应该失败
write_file /workspace/test.txt "New content"
```

#### 步骤 9: 添加审计日志查询工具

**文件**: `nanobot/agent/tools/audit.py`（新建）

**功能**:

* 查询最近的审计日志

* 查询安全违规记录

* 查询特定操作的日志

**实现**:

```python
"""Audit log query tool."""

from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool
from nanobot.agent.audit_logger import AuditLogger


class AuditLogTool(Tool):
    """Tool to query audit logs."""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.audit_logger = AuditLogger(workspace)

    @property
    def name(self) -> str:
        return "audit_log"

    @property
    def description(self) -> str:
        return "Query audit logs for security and compliance monitoring."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "enum": ["violations", "recent", "all"],
                    "description": "Type of query: violations, recent, or all"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of entries to return",
                    "default": 100
                }
            },
            "required": ["query_type"]
        }

    async def execute(self, query_type: str, limit: int = 100, **kwargs: Any) -> str:
        if query_type == "violations":
            violations = self.audit_logger.get_recent_violations(limit)
            return f"Found {len(violations)} security violations:\n" + "\n".join(
                f"- {v['timestamp']}: {v['violation_type']} - {v['details']}"
                for v in violations
            )
        elif query_type == "recent":
            # 读取最近的日志条目
            audit_file = self.workspace / "audit" / self.audit_logger.audit_file.name
            if not audit_file.exists():
                return "No audit logs found."
            with open(audit_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-limit:]
            return "\n".join(lines)
        else:
            return "Invalid query_type. Use: violations, recent, or all"
```

在 `AgentLoop._register_default_tools()` 中注册：

```python
self.tools.register(AuditLogTool(self.workspace))
```

## 实施顺序

1. ✅ 创建 `SecurityGuard` 类（安全守卫）
2. ✅ 创建 `AuditLogger` 类（审计日志）
3. ✅ 创建增强版 `SkillCommandParser` 类
4. ✅ 修改 `ExecTool` 添加安全验证
5. ✅ 修改文件操作工具（WriteFileTool、EditFileTool）添加安全检查
6. ✅ 修改 `AgentLoop` 初始化，集成所有安全组件
7. ✅ 添加配置选项（SecurityConfig）
8. ✅ 创建 `AuditLogTool` 查询工具
9. ✅ 测试所有安全功能
10. ✅ 完善文档和使用指南

## 风险和注意事项

### 安全风险

1. **绕过风险**:

   * 攻击者可能尝试通过命令注入绕过安全检查

   * 缓解：使用严格的正则表达式和多层验证

2. **误报风险**:

   * 合法命令可能被误判为危险

   * 缓解：提供详细的错误信息和白名单机制

3. **性能影响**:

   * 安全检查可能增加命令执行延迟

   * 缓解：优化正则表达式，使用缓存

### 实施风险

1. **向后兼容性**:

   * 现有功能可能受到影响

   * 缓解：提供配置选项，默认使用严格模式但允许降级

2. **配置复杂度**:

   * 新增的安全配置可能增加使用复杂度

   * 缓解：提供合理的默认值和清晰的文档

3. **测试覆盖**:

   * 需要充分测试各种安全场景

   * 缓解：创建全面的测试用例

### 运维风险

1. **审计日志管理**:

   * 日志文件可能占用大量磁盘空间

   * 缓解：实现日志轮转和清理策略

2. **误操作恢复**:

   * 只读模式可能限制正常操作

   * 缓解：提供明确的错误信息和操作建议

3. **性能监控**:

   * 需要监控安全检查的性能影响

   * 缓解：添加性能指标和告警

## 预期结果

实施完成后：

### 安全保障

* ✅ nanobot 只能执行在 skills 中明确定义的 Python 脚本

* ✅ 危险命令（删除、格式化等）被严格禁止

* ✅ 文件操作受到工作空间和系统目录限制

* ✅ 所有操作都被记录在审计日志中

* ✅ 提供多种安全级别以适应不同环境

### 用户体验

* ✅ 执行未授权命令时返回清晰的错误信息

* ✅ 错误信息包含可用的 skills 列表和建议

* ✅ 审计日志查询工具方便安全审计

* ✅ 不影响现有的 skill 功能

### 配置灵活性

* ✅ 支持三种安全级别（basic、strict、readonly）

* ✅ 可配置审计日志开关和目录

* ✅ 向后兼容，不影响现有配置

* ✅ 提供合理的默认值

## 文件变更清单

### 新建文件

1. **安全核心组件**:

   * `nanobot/agent/security_guard.py` - 安全守卫，统一的安全验证入口

   * `nanobot/agent/audit_logger.py` - 审计日志，记录所有操作

2. **工具增强**:

   * `nanobot/agent/tools/audit.py` - 审计日志查询工具

### 修改文件

1. **核心组件**:

   * `nanobot/agent/skills_command_parser.py` - 增强版，提取 Python 脚本白名单

   * `nanobot/agent/tools/shell.py` - 集成安全守卫和审计日志

   * `nanobot/agent/tools/filesystem.py` - 添加文件操作安全检查

   * `nanobot/agent/loop.py` - 集成所有安全组件

2. **配置**:

   * `nanobot/config/schema.py` - 添加 SecurityConfig

### 测试文件（可选）

1. **单元测试**:

   * `tests/test_security_guard.py` - 测试安全守卫功能

   * `tests/test_audit_logger.py` - 测试审计日志功能

   * `tests/test_skills_command_parser.py` - 测试技能命令解析

2. **集成测试**:

   * `tests/test_exec_tool_security.py` - 测试 ExecTool 安全限制

   * `tests/test_filesystem_security.py` - 测试文件操作安全

   * `tests/test_security_integration.py` - 测试完整的安全集成

## 部署建议

### 开发环境

```json
{
  "agents": {
    "security": {
      "level": "basic",
      "enable_audit_log": true
    }
  }
}
```

### 生产环境（推荐）

```json
{
  "agents": {
    "security": {
      "level": "strict",
      "enable_audit_log": true,
      "audit_log_dir": "audit"
    }
  }
}
```

### 高安全环境

```json
{
  "agents": {
    "security": {
      "level": "readonly",
      "enable_audit_log": true,
      "audit_log_dir": "audit"
    }
  }
}
```

## 监控和告警

### 关键指标

1. **安全违规次数**: 监控被阻止的命令和操作
2. **审计日志大小**: 监控日志文件增长
3. **命令执行延迟**: 监控安全检查的性能影响
4. **白名单命中率**: 监控白名单使用情况

### 告警规则

1. **高频安全违规**: 如果 1 分钟内超过 10 次安全违规，发送告警
2. **审计日志异常**: 如果日志文件增长过快，发送告警
3. **未授权 Python 脚本**: 如果检测到尝试执行未授权脚本，立即告警

## 后续优化

### 短期优化

* [ ] 添加更智能的命令模式匹配

* [ ] 实现审计日志轮转和清理

* [ ] 添加安全违规的实时通知

* [ ] 优化正则表达式性能

### 长期优化

* [ ] 实现基于机器学习的异常检测

* [ ] 添加沙箱执行环境

* [ ] 实现动态白名单管理

* [ ] 添加更细粒度的权限控制

