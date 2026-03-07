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
            if not violations:
                return "No security violations found."
            lines = [f"Found {len(violations)} security violations:\n"]
            for v in violations:
                lines.append(f"- {v['timestamp']}: {v['violation_type']} - {v['details']}")
            return "\n".join(lines)
        elif query_type == "recent":
            audit_file = self.workspace / "audit" / self.audit_logger.audit_file.name
            if not audit_file.exists():
                return "No audit logs found."
            with open(audit_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-limit:]
            return "".join(lines)
        elif query_type == "all":
            audit_file = self.workspace / "audit" / self.audit_logger.audit_file.name
            if not audit_file.exists():
                return "No audit logs found."
            with open(audit_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return content[:10000] + ("\n... (truncated)" if len(content) > 10000 else "")
        else:
            return "Invalid query_type. Use: violations, recent, or all"
