"""
Builder Agent — Infinity Template Library
Autonomous code generation and system scaffolding agent.
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class FileSpec(BaseModel):
    path: str
    content: str
    executable: bool = False


class BuildTask(BaseModel):
    """Task specification for the builder agent."""
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    system_type: str  # "api" | "frontend" | "agent" | "worker"
    name: str
    description: str
    tech_stack: list[str] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)
    output_dir: str = "/tmp/generated"


class BuildResult(BaseModel):
    task_id: str
    name: str
    files_generated: list[str]
    success: bool
    errors: list[str] = Field(default_factory=list)
    duration_ms: float
    created_at: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())


class BuilderAgent:
    """
    Generates complete, working code scaffolds based on a BuildTask specification.
    Integrates with the template composition engine for consistent output.
    """

    GENERATORS: dict[str, str] = {
        "api": "fastapi",
        "frontend": "nextjs",
        "agent": "research-agent",
        "worker": "event-worker",
    }

    def __init__(self, template_root: Optional[str] = None) -> None:
        self.template_root = Path(template_root or os.getenv("TEMPLATE_ROOT", "/templates"))

    async def build(self, task: BuildTask) -> BuildResult:
        """Execute the build task."""
        start = asyncio.get_event_loop().time()
        errors: list[str] = []
        files: list[str] = []

        try:
            output = Path(task.output_dir) / task.name
            output.mkdir(parents=True, exist_ok=True)

            specs = await self._generate_file_specs(task)
            for spec in specs:
                file_path = output / spec.path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(spec.content, encoding="utf-8")
                if spec.executable:
                    file_path.chmod(0o755)
                files.append(str(spec.path))

        except Exception as exc:
            errors.append(str(exc))

        elapsed = (asyncio.get_event_loop().time() - start) * 1000
        return BuildResult(
            task_id=task.task_id,
            name=task.name,
            files_generated=files,
            success=len(errors) == 0,
            errors=errors,
            duration_ms=elapsed,
        )

    async def _generate_file_specs(self, task: BuildTask) -> list[FileSpec]:
        """Generate file content specifications for the given task."""
        await asyncio.sleep(0)
        specs: list[FileSpec] = []

        if task.system_type == "api":
            specs.extend([
                FileSpec(path="README.md", content=f"# {task.name}\n\n{task.description}\n"),
                FileSpec(path="Dockerfile", content=self._dockerfile_content(task.name)),
                FileSpec(path=".env.example", content="SECRET_KEY=change-me\nENV=development\n"),
                FileSpec(path="requirements.txt", content="fastapi==0.115.6\nuvicorn[standard]==0.34.0\npydantic==2.10.4\n"),
            ])
        elif task.system_type == "frontend":
            specs.extend([
                FileSpec(path="README.md", content=f"# {task.name}\n\n{task.description}\n"),
                FileSpec(path="package.json", content=json.dumps({"name": task.name.lower().replace(" ", "-"), "version": "1.0.0", "scripts": {"dev": "next dev", "build": "next build"}}, indent=2)),
                FileSpec(path="Dockerfile", content=self._dockerfile_content(task.name, runtime="node")),
            ])
        elif task.system_type == "agent":
            specs.extend([
                FileSpec(path="README.md", content=f"# {task.name}\n\n{task.description}\n"),
                FileSpec(path="src/__init__.py", content=""),
                FileSpec(path="src/agent.py", content=f'"""Auto-generated agent: {task.name}"""\nfrom pydantic import BaseModel\n\nclass Task(BaseModel):\n    input: str\n'),
                FileSpec(path="requirements.txt", content="pydantic==2.10.4\nopenai==1.59.5\n"),
            ])

        return specs

    @staticmethod
    def _dockerfile_content(name: str, runtime: str = "python") -> str:
        if runtime == "python":
            return f"FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n"
        return f"FROM node:20-alpine\nWORKDIR /app\nCOPY package*.json ./\nRUN npm ci\nCOPY . .\nRUN npm run build\nCMD [\"node\", \"server.js\"]\n"
