from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
}

TRACKED_PREFIXES = (
    "backend/",
    "docs/",
    "scripts/",
    "README.md",
    "requirements.txt",
    ".gitignore",
)


def include_file(path: Path) -> bool:
    if not path.is_file():
        return False

    rel = path.relative_to(ROOT).as_posix()

    if any(part in IGNORE_DIRS for part in path.parts):
        return False

    if rel.endswith((".pyc", ".pyo", ".DS_Store")):
        return False

    return rel.startswith(TRACKED_PREFIXES)


def file_type(rel: str) -> str:
    if rel.startswith("backend/app/schemas/"):
        return "schema"
    if rel.startswith("backend/app/engines/"):
        return "engine"
    if rel.startswith("backend/app/tests/"):
        return "test"
    if rel.startswith("backend/app/api/") or rel.startswith("backend/app/routers/"):
        return "api_router"
    if rel.startswith("scripts/"):
        return "script_or_verifier"
    if rel.startswith("reports/"):
        return "report"
    if rel.startswith("docs/"):
        return "documentation"
    if rel.startswith("frontend/"):
        return "frontend"
    if rel.startswith("datasets/"):
        return "dataset"
    if rel.startswith("exports/"):
        return "export"
    if rel == "README.md":
        return "readme"
    if rel == "requirements.txt":
        return "dependency_file"
    return "project_file"


def chunk_owner(rel: str) -> str:
    lower = rel.lower()

    if "pre_chunk6" in lower or "chunk_1_to_5" in lower or "chunk1_to_5" in lower:
        return "pre_chunk_6_upgrade"
    if "chunk6" in lower or "deep_world" in lower:
        return "chunk_6"
    if "chunk5" in lower or "story_generation" in lower:
        return "chunk_5"
    if "chunk4" in lower or "simulation" in lower or "state_delta" in lower:
        return "chunk_4"
    if "character" in lower or "emotion" in lower or "memory" in lower or "destiny" in lower:
        return "chunk_3"
    if "world" in lower or "civilization" in lower or "society" in lower or "faction" in lower:
        return "chunk_2"
    if "foundation" in lower or "registry" in lower or "health" in lower:
        return "chunk_1"

    return "unknown_or_cross_chunk"


def purpose(rel: str, kind: str) -> str:
    name = Path(rel).name

    if kind == "schema":
        return "Defines structured data contracts and validation models."
    if kind == "engine":
        return "Implements MythOS engine logic for a story/world subsystem."
    if kind == "test":
        return "Tests related MythOS functionality."
    if kind == "script_or_verifier":
        return "Runs automation, verification, report generation, or tracking."
    if kind == "report":
        return "Generated report or verification artifact."
    if kind == "documentation":
        return "Documentation, roadmap, memory, or tracker file."

    return "Project file: " + name


def parse_imports(path: Path) -> list[str]:
    if path.suffix != ".py":
        return []

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)

    return sorted(set(imports))


def line_count(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except Exception:
        return 0


def related_tests(rel: str, all_files: list[str]) -> list[str]:
    stem = Path(rel).stem.replace("test_", "")
    matches = []

    for candidate in all_files:
        if not candidate.startswith("backend/app/tests/"):
            continue

        candidate_stem = Path(candidate).stem.replace("test_", "")
        if stem in candidate_stem or candidate_stem in stem:
            matches.append(candidate)

    return sorted(set(matches))


def connected_files(rel: str, imports: list[str], all_files: list[str]) -> list[str]:
    connected = set()

    for item in imports:
        if not item.startswith("backend."):
            continue

        possible = item.replace(".", "/") + ".py"
        if possible in all_files:
            connected.add(possible)

    if rel.startswith("backend/app/engines/deep_world/"):
        connected.add("backend/app/schemas/deep_world.py")

    return sorted(connected)


def likely_dependents(rel: str, all_imports: dict[str, list[str]]) -> list[str]:
    if not rel.endswith(".py"):
        return []

    module = rel[:-3].replace("/", ".")
    dependents = []

    for file_path, imports in all_imports.items():
        if file_path != rel and module in imports:
            dependents.append(file_path)

    return sorted(dependents)



def related_docs(rel: str, all_files: list[str]) -> list[str]:
    owner = chunk_owner(rel)
    return sorted(
        candidate for candidate in all_files
        if candidate.startswith("docs/") and chunk_owner(candidate) == owner
    )[:25]


def related_reports(rel: str, all_files: list[str]) -> list[str]:
    owner = chunk_owner(rel)
    return sorted(
        candidate for candidate in all_files
        if candidate.startswith("reports/") and chunk_owner(candidate) == owner
    )[:25]

def main() -> int:
    files = sorted(
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*")
        if include_file(p)
    )

    imports_by_file = {
        rel: parse_imports(ROOT / rel)
        for rel in files
    }

    records = []

    for rel in files:
        path = ROOT / rel
        kind = file_type(rel)
        imports = imports_by_file[rel]

        records.append(
            {
                "file_path": rel,
                "file_type": kind,
                "chunk_owner": chunk_owner(rel),
                "purpose": purpose(rel, kind),
                "imports": imports,
                "connected_files": connected_files(rel, imports, files),
                "likely_dependents": likely_dependents(rel, imports_by_file),
                "related_tests": related_tests(rel, files),
                "line_count": line_count(path),
                "last_modified_utc": datetime.fromtimestamp(
                    path.stat().st_mtime,
                    timezone.utc,
                ).isoformat(),
                "status": "active_project_file",
            }
        )

    generated_at = datetime.now(timezone.utc).isoformat()

    payload = {
        "project": "MythOS Engine",
        "generated_at_utc": generated_at,
        "total_tracked_files": len(records),
        "records": records,
    }

    docs = ROOT / "docs"
    docs.mkdir(parents=True, exist_ok=True)

    (docs / "mythos_file_tracker.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines = [
        "# MythOS Engine File Tracker",
        "",
        "Generated at UTC: " + generated_at,
        "Total tracked files: " + str(len(records)),
        "",
        "This file records every current project file, what it does, and what it connects to.",
        "",
    ]

    grouped = {}

    for record in records:
        grouped.setdefault(record["chunk_owner"], []).append(record)

    max_markdown_records_per_chunk = 300

    for chunk in sorted(grouped):
        lines.append("## " + chunk)
        lines.append("")

        chunk_records = sorted(grouped[chunk], key=lambda item: item["file_path"])
        if len(chunk_records) > max_markdown_records_per_chunk:
            lines.append(f"_Showing first {max_markdown_records_per_chunk} of {len(chunk_records)} files for this chunk. Full data is in mythos_file_tracker.json._")
            lines.append("")

        for record in chunk_records[:max_markdown_records_per_chunk]:
            lines.append("### `" + record["file_path"] + "`")
            lines.append("")
            lines.append("- Type: `" + record["file_type"] + "`")
            lines.append("- Status: `" + record["status"] + "`")
            lines.append("- Purpose: " + record["purpose"])
            lines.append("- Line count: " + str(record["line_count"]))

            if record["imports"]:
                lines.append("- Imports:")
                for item in record["imports"][:20]:
                    lines.append("  - `" + item + "`")

            if record["connected_files"]:
                lines.append("- Connected files:")
                for item in record["connected_files"][:20]:
                    lines.append("  - `" + item + "`")

            if record["likely_dependents"]:
                lines.append("- Likely dependents:")
                for item in record["likely_dependents"][:20]:
                    lines.append("  - `" + item + "`")

            if record["related_tests"]:
                lines.append("- Related tests:")
                for item in record["related_tests"][:20]:
                    lines.append("  - `" + item + "`")

            lines.append("")

    (docs / "mythos_file_tracker.md").write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
    )

    print("Updated docs/mythos_file_tracker.md")
    print("Updated docs/mythos_file_tracker.json")
    print("Tracked files:", len(records))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
