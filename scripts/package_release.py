#!/usr/bin/env python3
"""Create a source-only ZIP, excluding local state, secrets, caches, and build output."""
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT.parent / "VoiceSphere-AI-2.0.zip"
EXCLUDED_DIRS = {
    ".git", ".next", "node_modules", ".venv", "venv", "__pycache__",
    ".pytest_cache", ".ruff_cache", ".mypy_cache", ".cache", ".terraform",
    "coverage", "dist", "build", "target", "out", "test-results", "playwright-report", "blob-report",
}
EXCLUDED_NAMES = {".env", ".env.local", ".env.production", ".DS_Store", "tsconfig.tsbuildinfo"}

def include(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        return False
    if path.name in EXCLUDED_NAMES or path.suffix in {".pyc", ".db", ".sqlite", ".sqlite3", ".tsbuildinfo"}:
        return False
    if path.is_symlink():
        return False
    return path.is_file()

OUT.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as archive:
    for file in sorted(ROOT.rglob("*")):
        if include(file) and file.resolve() != OUT:
            archive.write(file, Path(ROOT.name) / file.relative_to(ROOT))
print(f"Created {OUT} ({OUT.stat().st_size:,} bytes)")
with zipfile.ZipFile(OUT) as archive:
    names = archive.namelist()
    prohibited = [name for name in names if any(f"/{part}/" in f"/{name}" for part in EXCLUDED_DIRS)]
    if prohibited:
        raise SystemExit(f"Archive contains excluded build content: {prohibited[:5]}")
    print(f"Archived {len(names)} source/documentation files; .env.example included, local .env excluded.")
