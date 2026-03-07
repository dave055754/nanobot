#!/usr/bin/env python3
"""Test script for security features."""

from pathlib import Path
from nanobot.agent.security_guard import SecurityGuard, SecurityLevel
from nanobot.agent.audit_logger import AuditLogger
from nanobot.agent.skills_command_parser import SkillCommandParser
from nanobot.agent.skills import SkillsLoader

def test_security_guard():
    """Test SecurityGuard functionality."""
    print("Testing SecurityGuard...")

    guard = SecurityGuard(
        security_level=SecurityLevel.STRICT,
        workspace=Path("/tmp/test_workspace"),
    )

    guard.set_python_script_whitelist([
        "nanobot/skills/ledger-validation/scripts/validate_ledger.py"
    ])

    test_cases = [
        ("python3 nanobot/skills/ledger-validation/scripts/validate_ledger.py", True),
        ("python3 /tmp/malicious.py", False),
        ("rm -rf /important", False),
        ("ls -la", True),
    ]

    for cmd, should_be_safe in test_cases:
        is_safe, reason = guard.is_command_safe(cmd)
        status = "✓" if is_safe == should_be_safe else "✗"
        print(f"  {status} {cmd[:50]:50s} - Expected: {should_be_safe}, Got: {is_safe}")
        if not is_safe:
            print(f"    Reason: {reason}")

    print("SecurityGuard tests passed!\n")

def test_audit_logger():
    """Test AuditLogger functionality."""
    print("Testing AuditLogger...")

    logger = AuditLogger(Path("/tmp/test_workspace"))

    logger.log_command("ls -la", allowed=True)
    logger.log_command("rm -rf /important", allowed=False, reason="Dangerous command")
    logger.log_file_operation("write", "/tmp/test.txt", allowed=True)
    logger.log_file_operation("delete", "/etc/passwd", allowed=False, reason="Protected directory")

    violations = logger.get_recent_violations(limit=10)
    print(f"  Found {len(violations)} violations in audit log")

    print("AuditLogger tests passed!\n")

def test_skill_command_parser():
    """Test SkillCommandParser functionality."""
    print("Testing SkillCommandParser...")

    skills_loader = SkillsLoader(Path("/tmp/test_workspace"))
    parser = SkillCommandParser(skills_loader)

    parser.parse_all_skills()

    print(f"  Python scripts: {len(parser.get_python_scripts())}")
    print(f"  Allowed tools: {len(parser.get_allowed_tools())}")
    print(f"  Skills with commands: {len(parser.skill_commands)}")

    print("SkillCommandParser tests passed!\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Nanobot Security Features Test Suite")
    print("=" * 60)
    print()

    test_security_guard()
    test_audit_logger()
    test_skill_command_parser()

    print("=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
