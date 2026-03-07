"""Security guard for nanobot operations."""

import re
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple


class SecurityLevel(Enum):
    """Security levels for nanobot operations."""
    BASIC = "basic"
    STRICT = "strict"
    READONLY = "readonly"


class SecurityGuard:
    """Security guard for validating operations."""

    DANGEROUS_PATTERNS = [
        r'\brm\s+[-rf]+\b',
        r'\brmdir\s+[/s]?\b',
        r'\bdel\s+[/fq]+\b',
        r'(?:^|[;&|]\s*)format\b',
        r'\b(mkfs|diskpart)\b',
        r'\bdd\s+if=',
        r'>\s*/dev/sd',
        r'\b(shutdown|reboot|poweroff|halt)\b',
        r':\(\)\s*\{.*\};\s*:',
        r'\bchmod\s+777\b',
        r'\bchown\b',
        r'\bsudo\b',
        r'\bsu\b',
        r'\bmv\s+.*\s+/',
        r'\bcp\s+.*\s+/',
        r'\b(pip|npm|yarn|gem)\s+install\b',
        r'\bapt-get\s+(install|remove|purge)\b',
        r'\byum\s+(install|remove)\b',
        r'\bbrew\s+(install|uninstall)\b',
        r'\b(python|node)\s+-m\s+pip\s+install\b',
        r'\bcurl\s+.*\|\s*(bash|sh|python|node)\b',
        r'\bwget\s+.*\|\s*(bash|sh|python|node)\b',
    ]

    READONLY_BLOCKED_PATTERNS = [
        r'>',
        r'>>',
        r'\btee\b',
        r'\b(write|edit|modify|update|delete|remove)\b',
        r'\b(mv|cp)\b',
        r'\b(mkdir|touch)\b',
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
        """Set whitelist of allowed Python scripts."""
        self.python_script_whitelist = set(scripts)

    def set_allowed_tools(self, tools: list[str]) -> None:
        """Set list of allowed tools."""
        self.allowed_tools = set(tools)

    def set_skill_commands(self, commands: dict[str, list[str]]) -> None:
        """Set commands defined in skills."""
        self.skill_commands = commands

    def is_command_safe(self, command: str) -> Tuple[bool, str]:
        """Check if a command is safe to execute.

        Args:
            command: The command to check

        Returns:
            Tuple of (is_safe, reason)
        """
        cmd_lower = command.lower().strip()

        if self.security_level == SecurityLevel.READONLY:
            for pattern in self.READONLY_BLOCKED_PATTERNS:
                if re.search(pattern, cmd_lower):
                    return False, f"Command blocked: Read-only mode forbids write operations"

        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, cmd_lower):
                return False, f"Command blocked: Dangerous operation detected"

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

        if self.security_level == SecurityLevel.READONLY:
            if operation in ['write', 'edit', 'delete', 'create']:
                return False, f"File operation blocked: Read-only mode forbids {operation} operations"

        if self.workspace:
            workspace_path = self.workspace.resolve()
            if path.is_absolute():
                if workspace_path not in path.parents and path != workspace_path:
                    return False, f"File operation blocked: Path outside workspace ({self.workspace})"

        dangerous_paths = [
            '/etc/', '/usr/', '/bin/', '/sbin/', '/lib/', '/sys/', '/proc/',
            '~/.ssh/', '~/.config/', '~/.gnupg/',
        ]
        for dangerous in dangerous_paths:
            if str(path).startswith(dangerous):
                return False, f"File operation blocked: Path in protected system directory"

        return True, ""

    def _is_python_script_allowed(self, command: str) -> bool:
        """Check if a Python script is in whitelist."""
        parts = command.split()
        for part in parts:
            if part.endswith('.py'):
                script_path = Path(part).resolve()
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
