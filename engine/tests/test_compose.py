"""Tests for the template composition engine."""
import json
import tempfile
from pathlib import Path
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from compose import CompositionEngine, ManifestValidationError


VALID_MANIFEST = {
    "manifest_version": "1.0",
    "system_name": "test-system",
    "org": "Infinity-X-One-Systems",
    "components": {
        "backend": {"template": "fastapi"},
        "frontend": {"template": "nextjs-pwa"},
        "infrastructure": {"docker": True, "github_actions": True},
        "governance": {"tap_enforcement": True, "test_coverage_gate": True}
    }
}


def make_engine(template_root: Path, output_root: Path, dry_run: bool = False) -> CompositionEngine:
    return CompositionEngine(template_root=template_root, output_root=output_root, dry_run=dry_run)


def test_validate_valid_manifest():
    with tempfile.TemporaryDirectory() as tmp:
        engine = make_engine(Path(tmp), Path(tmp))
        engine.validate_manifest(VALID_MANIFEST)  # Should not raise


def test_validate_missing_fields():
    with tempfile.TemporaryDirectory() as tmp:
        engine = make_engine(Path(tmp), Path(tmp))
        with pytest.raises(ManifestValidationError, match="Missing required fields"):
            engine.validate_manifest({"system_name": "test"})


def test_validate_wrong_version():
    with tempfile.TemporaryDirectory() as tmp:
        engine = make_engine(Path(tmp), Path(tmp))
        bad = {**VALID_MANIFEST, "manifest_version": "2.0"}
        with pytest.raises(ManifestValidationError, match="Unsupported manifest_version"):
            engine.validate_manifest(bad)


def test_validate_invalid_system_name():
    with tempfile.TemporaryDirectory() as tmp:
        engine = make_engine(Path(tmp), Path(tmp))
        bad = {**VALID_MANIFEST, "system_name": "Invalid Name!!"}
        with pytest.raises(ManifestValidationError, match="Invalid system_name"):
            engine.validate_manifest(bad)


def test_validate_unknown_backend_template():
    with tempfile.TemporaryDirectory() as tmp:
        engine = make_engine(Path(tmp), Path(tmp))
        bad = {**VALID_MANIFEST, "components": {**VALID_MANIFEST["components"], "backend": {"template": "rails"}}}
        with pytest.raises(ManifestValidationError, match="Unknown backend template"):
            engine.validate_manifest(bad)


def test_resolve_dependencies():
    with tempfile.TemporaryDirectory() as tmp:
        engine = make_engine(Path(tmp), Path(tmp))
        deps = engine.resolve_dependencies(VALID_MANIFEST)
        types = [d["type"] for d in deps]
        assert "core" in types
        assert "backend" in types
        assert "frontend" in types


def test_dry_run_compose():
    with tempfile.TemporaryDirectory() as tmp:
        tpl = Path(tmp) / "templates"
        out = Path(tmp) / "output"
        tpl.mkdir()
        engine = make_engine(tpl, out, dry_run=True)
        result = engine.compose(VALID_MANIFEST)
        # In dry-run mode, output dir is NOT created
        assert not result.exists() or result.is_dir()


def test_compose_creates_output():
    with tempfile.TemporaryDirectory() as tmp:
        tpl = Path(tmp) / "templates"
        out = Path(tmp) / "output"
        tpl.mkdir()
        engine = make_engine(tpl, out, dry_run=False)
        result = engine.compose(VALID_MANIFEST)
        assert result.exists()
        assert (result / "README.md").exists()
        assert (result / "system-manifest.json").exists()
