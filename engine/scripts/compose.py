#!/usr/bin/env python3
"""
Template Composition Engine — Infinity Template Library
Reads a system manifest and scaffolds a complete production system.

Usage:
    python compose.py --manifest path/to/manifest.json --output /path/to/output
    python compose.py --manifest path/to/manifest.json --dry-run
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timezone


class ManifestValidationError(Exception):
    pass


class CompositionEngine:
    """
    Reads a system manifest, resolves template dependencies,
    and scaffolds a complete repository structure.
    """

    REQUIRED_MANIFEST_FIELDS = {"manifest_version", "system_name", "org", "components"}
    SUPPORTED_BACKEND_TEMPLATES = {"fastapi", "express", "graphql", "websocket", "ai-inference", "event-worker"}
    SUPPORTED_FRONTEND_TEMPLATES = {"nextjs-pwa", "vite-react", "dashboard", "admin-panel", "saas-landing", "ai-console", "chat-ui"}
    SUPPORTED_AI_AGENTS = {"research", "builder", "validator", "financial", "real-estate", "orchestrator", "content-gen", "social-automation"}

    def __init__(self, template_root: Path, output_root: Path, dry_run: bool = False) -> None:
        self.template_root = template_root
        self.output_root = output_root
        self.dry_run = dry_run
        self._log: list[str] = []

    def log(self, message: str) -> None:
        timestamp = datetime.now(tz=timezone.utc).strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}"
        self._log.append(line)
        print(line)

    def validate_manifest(self, manifest: dict[str, Any]) -> None:
        missing = self.REQUIRED_MANIFEST_FIELDS - set(manifest.keys())
        if missing:
            raise ManifestValidationError(f"Missing required fields: {missing}")

        if manifest.get("manifest_version") != "1.0":
            raise ManifestValidationError(f"Unsupported manifest_version: {manifest.get('manifest_version')}. Expected '1.0'")

        import re
        if not re.match(r"^[a-z][a-z0-9-]{2,63}$", manifest["system_name"]):
            raise ManifestValidationError(f"Invalid system_name: must be kebab-case, 3-64 chars")

        components = manifest.get("components", {})
        if backend := components.get("backend"):
            tmpl = backend.get("template")
            if tmpl and tmpl not in self.SUPPORTED_BACKEND_TEMPLATES:
                raise ManifestValidationError(f"Unknown backend template: {tmpl}")

        if frontend := components.get("frontend"):
            tmpl = frontend.get("template")
            if tmpl and tmpl not in self.SUPPORTED_FRONTEND_TEMPLATES:
                raise ManifestValidationError(f"Unknown frontend template: {tmpl}")

    def resolve_dependencies(self, manifest: dict[str, Any]) -> list[dict[str, Any]]:
        """Build an ordered list of components to scaffold."""
        components = manifest.get("components", {})
        infra = components.get("infrastructure", {})
        gov = components.get("governance", {})
        deps: list[dict[str, Any]] = []

        # Core always included
        deps.append({"type": "core", "name": "root-structure"})

        # Backend
        if backend := components.get("backend"):
            deps.append({"type": "backend", "name": backend.get("template", "fastapi"), "config": backend.get("config", {})})

        # Frontend
        if frontend := components.get("frontend"):
            deps.append({"type": "frontend", "name": frontend.get("template", "nextjs-pwa"), "config": frontend.get("config", {})})

        # AI Agents
        for agent in components.get("ai_agents", []):
            deps.append({"type": "ai_agent", "name": agent["template"], "instance": agent.get("instance_name", agent["template"]), "config": agent.get("config", {})})

        # Business module
        if business := components.get("business"):
            deps.append({"type": "business", "name": business.get("template", ""), "config": business.get("config", {})})

        # Infrastructure
        if infra.get("docker", True):
            deps.append({"type": "infra", "name": "docker-compose"})
        if infra.get("github_actions", True):
            deps.append({"type": "infra", "name": "github-actions-ci"})
        if infra.get("github_pages"):
            deps.append({"type": "infra", "name": "github-pages"})
        if infra.get("github_projects"):
            deps.append({"type": "infra", "name": "github-projects"})

        # Governance
        if gov.get("tap_enforcement", True):
            deps.append({"type": "governance", "name": "tap-enforcement"})
        if gov.get("test_coverage_gate", True):
            deps.append({"type": "governance", "name": "test-coverage-gate"})
        if gov.get("security_scan", True):
            deps.append({"type": "governance", "name": "security-gate"})

        return deps

    def scaffold_component(self, component: dict[str, Any], system_name: str) -> None:
        """Copy template files into the output directory."""
        comp_type = component["type"]
        comp_name = component["name"]
        output_dir = self.output_root / system_name

        # Resolve template source directory with fallback aliases
        _ai_agent_aliases = {
            "orchestrator": "orchestrator",
            "research": "research-agent",
            "builder": "builder-agent",
            "validator": "validator-agent",
            "financial": "financial-agent",
            "real-estate": "real-estate-agent",
        }
        _business_aliases = {
            "crm": "crm-automation",
            "lead-gen": "lead-gen",
            "billing": "billing",
            "saas-subscription": "saas-subscription",
        }
        _infra_aliases = {
            "docker-compose": "docker-local-mesh",
            "github-actions-ci": "github-actions",
            "github-pages": "github-pages",
            "github-projects": "github-projects",
            "gitops": "gitops",
            "observability": "observability",
        }
        ai_dir = _ai_agent_aliases.get(comp_name, f"{comp_name}-agent")
        biz_dir = _business_aliases.get(comp_name, comp_name)
        infra_dir = _infra_aliases.get(comp_name, comp_name)

        src_map = {
            "backend": self.template_root / "core" / f"api-{comp_name}" if (self.template_root / "core" / f"api-{comp_name}").exists()
                       else self.template_root / "backend" / f"{comp_name}-api" if (self.template_root / "backend" / f"{comp_name}-api").exists()
                       else self.template_root / "backend" / comp_name,
            "frontend": self.template_root / "core" / "frontend-nextjs" if comp_name.startswith("nextjs")
                        else self.template_root / "frontend" / comp_name,
            "ai_agent": self.template_root / "ai" / ai_dir,
            "business": self.template_root / "business" / biz_dir,
            "infra": self.template_root / "infrastructure" / infra_dir,
            "governance": self.template_root / "governance" / comp_name,
            "core": None,
        }

        src = src_map.get(comp_type)
        if comp_type == "core":
            self._scaffold_root_structure(output_dir, system_name)
            return

        if src is None or not src.exists():
            self.log(f"  ⚠  Template not found for {comp_type}/{comp_name} at {src} — generating stub")
            self._scaffold_stub(output_dir, component)
            return

        dest_subdir = {
            "backend": "backend",
            "frontend": "frontend",
            "ai_agent": f"agents/{component.get('instance', comp_name)}",
            "business": "business",
            "infra": f".infra/{comp_name}",
            "governance": f".governance/{comp_name}",
        }.get(comp_type, comp_name)

        dest = output_dir / dest_subdir
        if not self.dry_run:
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(str(src), str(dest))
        self.log(f"  ✓  {comp_type}/{comp_name} → {dest_subdir}")

    def _scaffold_root_structure(self, output_dir: Path, system_name: str) -> None:
        if not self.dry_run:
            for d in ["backend", "frontend", "agents", "business", ".github/workflows", "docs", "scripts"]:
                (output_dir / d).mkdir(parents=True, exist_ok=True)

            # Root README
            readme = output_dir / "README.md"
            readme.write_text(f"# {system_name}\n\nGenerated by Infinity Template Library.\n\n## Architecture\n\nThis system was composed from the Infinity Template Library manifest.\n")

            # Root docker-compose stub
            dc = output_dir / "docker-compose.yml"
            dc.write_text(f"version: \"3.9\"\nservices:\n  # Add services here\n  # Generated by Infinity Template Library\n")

        self.log(f"  ✓  root structure for {system_name}")

    def _scaffold_stub(self, output_dir: Path, component: dict[str, Any]) -> None:
        """Generate a minimal stub when the template is not found."""
        if self.dry_run:
            return
        stub_dir = output_dir / component["type"] / component["name"]
        stub_dir.mkdir(parents=True, exist_ok=True)
        (stub_dir / "README.md").write_text(f"# {component['name']}\n\nStub generated — implement this component.\n")

    def compose(self, manifest: dict[str, Any]) -> Path:
        """Main entry point: validate, resolve, scaffold."""
        self.log("▶ Validating manifest...")
        self.validate_manifest(manifest)
        self.log("  ✓  Manifest valid")

        system_name = manifest["system_name"]
        output_dir = self.output_root / system_name
        if not self.dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)

        self.log(f"▶ Resolving dependencies for '{system_name}'...")
        deps = self.resolve_dependencies(manifest)
        self.log(f"  ✓  {len(deps)} components to scaffold")

        self.log("▶ Scaffolding components...")
        for component in deps:
            self.scaffold_component(component, system_name)

        # Write manifest copy into output
        if not self.dry_run:
            (output_dir / "system-manifest.json").write_text(json.dumps(manifest, indent=2))

        self.log(f"▶ System '{system_name}' composed successfully → {output_dir}")
        return output_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Infinity Template Composition Engine")
    parser.add_argument("--manifest", required=True, help="Path to system manifest JSON")
    parser.add_argument("--output", default="./generated", help="Output directory")
    parser.add_argument("--template-root", default=str(Path(__file__).parent.parent.parent), help="Template library root")
    parser.add_argument("--dry-run", action="store_true", help="Validate and show plan without generating files")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"ERROR: Manifest file not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    with manifest_path.open() as f:
        manifest = json.load(f)

    engine = CompositionEngine(
        template_root=Path(args.template_root),
        output_root=Path(args.output),
        dry_run=args.dry_run,
    )
    engine.compose(manifest)


if __name__ == "__main__":
    main()
