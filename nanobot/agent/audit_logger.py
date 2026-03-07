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
        """Write an entry to audit log."""
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
