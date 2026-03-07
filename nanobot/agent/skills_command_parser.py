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

        code_blocks = re.findall(r'```bash\n(.*?)\n```', content, re.DOTALL)
        for block in code_blocks:
            commands.extend(self._extract_commands_from_block(block))

        python_scripts = re.findall(r'(python3?\s+[\w/\-\.]+\.py)', content)
        for script in python_scripts:
            script_path = script.split()[-1]
            self.python_scripts.add(script_path)

        if commands:
            self.skill_commands[skill_name] = commands

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

        for skill_name, commands in self.skill_commands.items():
            for cmd in commands:
                if command == cmd.strip():
                    return True, skill_name

        if command.lower().startswith('python'):
            script_path = self._extract_python_script_path(command)
            if script_path and script_path in self.python_scripts:
                return True, "python_script"

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
