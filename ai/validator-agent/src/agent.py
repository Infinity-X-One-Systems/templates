"""
Validator Agent — Infinity Template Library
Validates data, code, and system outputs against defined schemas and rules.
"""
from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Optional
from uuid import uuid4
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ValidationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    severity: str = "error"  # "error" | "warning" | "info"
    rule_type: str  # "schema" | "regex" | "range" | "custom" | "security"
    params: dict[str, Any] = Field(default_factory=dict)


class ValidationIssue(BaseModel):
    rule_id: str
    rule_name: str
    severity: str
    message: str
    path: str = ""
    actual_value: Optional[Any] = None
    expected: Optional[str] = None


class ValidationResult(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    target: str
    passed: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
    warnings: int = 0
    errors: int = 0
    validated_at: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())

    def model_post_init(self, __context: object) -> None:
        self.errors = sum(1 for i in self.issues if i.severity == "error")
        self.warnings = sum(1 for i in self.issues if i.severity == "warning")
        self.passed = self.errors == 0


class ValidatorAgent:
    """
    Validates data structures, API responses, code output, and system configurations
    against defined rules and schemas.
    """

    SECURITY_PATTERNS = [
        (r"(?i)(password|secret|api_key|token)\s*=\s*['\"](?!.*\*\*\*)([^'\"]{8,})['\"]", "Potential hardcoded credential"),
        (r"(?i)eval\s*\(", "Dangerous eval() usage"),
        (r"(?i)exec\s*\(", "Dangerous exec() usage"),
        (r"\b(?:127\.0\.0\.1|0\.0\.0\.0)\b.*production", "Localhost binding in production config"),
    ]

    def __init__(self, rules: Optional[list[ValidationRule]] = None) -> None:
        self.rules = rules or []

    def add_rule(self, rule: ValidationRule) -> None:
        self.rules.append(rule)

    async def validate_json(self, data: Any, schema: dict[str, Any], target: str = "data") -> ValidationResult:
        """Validate JSON data against a schema."""
        await asyncio.sleep(0)
        issues: list[ValidationIssue] = []

        if not isinstance(data, dict):
            issues.append(ValidationIssue(rule_id="schema-type", rule_name="Type Check", severity="error", message="Expected object/dict", path="$"))
        else:
            required = schema.get("required", [])
            props = schema.get("properties", {})
            for field in required:
                if field not in data:
                    issues.append(ValidationIssue(rule_id=f"required-{field}", rule_name="Required Field", severity="error", message=f"Missing required field: {field}", path=f"$.{field}"))
            for key, value in data.items():
                if key in props:
                    prop_type = props[key].get("type")
                    if prop_type:
                        type_map = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "array": list, "object": dict}
                        expected_type = type_map.get(prop_type)
                        if expected_type and not isinstance(value, expected_type):
                            issues.append(ValidationIssue(rule_id=f"type-{key}", rule_name="Type Check", severity="error", message=f"Field {key} should be {prop_type}", path=f"$.{key}", actual_value=type(value).__name__, expected=prop_type))

        return ValidationResult(target=target, passed=len([i for i in issues if i.severity == "error"]) == 0, issues=issues)

    async def validate_code(self, code: str, language: str = "python", target: str = "code") -> ValidationResult:
        """Scan code for security issues and best-practice violations."""
        await asyncio.sleep(0)
        issues: list[ValidationIssue] = []

        for pattern, message in self.SECURITY_PATTERNS:
            if re.search(pattern, code):
                issues.append(ValidationIssue(rule_id="security-scan", rule_name="Security Scan", severity="error", message=message, path="code"))

        # Python-specific checks
        if language == "python":
            if "import *" in code:
                issues.append(ValidationIssue(rule_id="no-star-import", rule_name="Import Check", severity="warning", message="Wildcard imports (import *) are discouraged", path="code"))
            if len(code.splitlines()) > 500:
                issues.append(ValidationIssue(rule_id="file-length", rule_name="File Length", severity="warning", message="File exceeds 500 lines — consider splitting", path="code"))

        return ValidationResult(target=target, passed=len([i for i in issues if i.severity == "error"]) == 0, issues=issues)

    async def validate_manifest(self, manifest: dict[str, Any]) -> ValidationResult:
        """Validate a system manifest against required fields."""
        await asyncio.sleep(0)
        schema = {
            "required": ["manifest_version", "system_name", "org", "components"],
            "properties": {
                "manifest_version": {"type": "string"},
                "system_name": {"type": "string"},
                "org": {"type": "string"},
                "components": {"type": "object"},
            },
        }
        return await self.validate_json(manifest, schema, target="system-manifest")
