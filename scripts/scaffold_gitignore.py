"""
scaffold_gitignore.py — Idempotent .gitignore scaffolding.

Provides ``append_missing_gitignore_entries(path)`` which ensures the given
.gitignore file contains all entries defined in ``REQUIRED_GITIGNORE_ENTRIES``.

- If the file does not exist: it is created with all required entries.
- If the file already exists: only the entries not already present are
  appended under a clearly-marked section comment so existing content is
  never overwritten or duplicated.
"""

from __future__ import annotations

import pathlib

# ---------------------------------------------------------------------------
# Canonical list of required .gitignore entries
# ---------------------------------------------------------------------------

REQUIRED_GITIGNORE_ENTRIES: list[str] = [
    # Python
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    # Virtual environments
    "venv/",
    ".venv/",
    "env/",
    # IDE
    ".idea/",
    ".vscode/",
    # OS
    ".DS_Store",
    "Thumbs.db",
    # Secrets
    ".env",
    # Data files
    "data/*.csv",
    "data/*.parquet",
    "data/*.json",
    "data/**/*.csv",
    "data/**/*.parquet",
    "data/**/*.json",
    # Build / dist
    "dist/",
    "*.egg-info/",
]

_SCAFFOLD_SECTION_COMMENT = "# --- ai-project-foundation scaffold ---"


def append_missing_gitignore_entries(path: str | pathlib.Path) -> None:
    """Ensure *path* contains all entries in ``REQUIRED_GITIGNORE_ENTRIES``.

    Parameters
    ----------
    path:
        Path to the ``.gitignore`` file (need not exist yet).

    Behaviour
    ---------
    * **File absent** — creates the file and writes every required entry,
      preceded by the scaffold section comment.
    * **File present** — reads all existing non-blank lines, computes the set
      of required entries not yet present, and appends them under the scaffold
      section comment.  Blank lines and comment lines in the existing file are
      preserved but are not counted as "present" entries for the purposes of
      the set-difference calculation.

    The function is idempotent: calling it multiple times on the same file
    produces the same result as calling it once.
    """
    target = pathlib.Path(path)

    if not target.exists():
        # File does not exist — create it from scratch.
        lines = [_SCAFFOLD_SECTION_COMMENT]
        lines.extend(REQUIRED_GITIGNORE_ENTRIES)
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    # File exists — append only what is missing.
    existing_text = target.read_text(encoding="utf-8")
    existing_lines = existing_text.splitlines()

    # Build a set of non-blank, non-comment existing entries for fast lookup.
    existing_entries: set[str] = {
        line.strip()
        for line in existing_lines
        if line.strip() and not line.strip().startswith("#")
    }

    missing: list[str] = [
        entry for entry in REQUIRED_GITIGNORE_ENTRIES if entry not in existing_entries
    ]

    if not missing:
        # Nothing to add.
        return

    # Append missing entries under the scaffold section comment.
    suffix = "\n" + _SCAFFOLD_SECTION_COMMENT + "\n" + "\n".join(missing) + "\n"

    # Ensure there is exactly one trailing newline before our block.
    if not existing_text.endswith("\n"):
        suffix = "\n" + suffix

    with target.open("a", encoding="utf-8") as fh:
        fh.write(suffix)


# ---------------------------------------------------------------------------
# CLI entry point (optional convenience usage)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    target_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".gitignore")
    append_missing_gitignore_entries(target_path)
    print(f"✓ .gitignore updated: {target_path.resolve()}")
