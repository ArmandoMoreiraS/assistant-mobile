# Implementation Plan: ai-project-foundation

## Overview

Generate the foundational repository scaffold for an LLM and AI Agentic systems project. Implementation proceeds in layers: directory structure first, then configuration files, then the `src/ai_foundation` Python package, then tooling validation. Each task produces runnable, lint-clean output before the next task begins.

## Tasks

- [x] 1. Create directory tree and `.gitkeep` placeholders
  - Create all top-level directories: `agents/`, `notebooks/`, `data/raw/`, `data/processed/`, `data/outputs/`, `configs/`, `tests/`, `docs/`, `scripts/`
  - Create `src/ai_foundation/utils/` directory hierarchy
  - Add `.gitkeep` to every directory that is intentionally empty: `agents/`, `notebooks/`, `data/raw/`, `data/processed/`, `data/outputs/`, `configs/`, `tests/`, `docs/`, `scripts/`
  - Use `pathlib.Path.mkdir(parents=True, exist_ok=True)` so the scaffold is idempotent
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9_

- [x] 2. Create `.gitignore` with merge logic
  - [x] 2.1 Implement `append_missing_gitignore_entries(path)` function
    - Define the canonical `REQUIRED_GITIGNORE_ENTRIES` list (Python bytecode, venvs, IDE, OS, secrets, data files, build artifacts) as specified in the design
    - If `.gitignore` does not exist, write all required entries
    - If `.gitignore` already exists, read current content, compute missing entries, and append only the diff — never overwrite or duplicate existing lines
    - Use a section comment (`# --- ai-project-foundation scaffold ---`) to clearly mark appended entries
    - _Requirements: 3.2, 4.1, 4.3_

  - [ ]* 2.2 Write property test for `.gitignore` append behavior
    - **Property 2: .gitignore append preserves existing content**
    - Use `hypothesis` with `@given(existing_lines=st.lists(...))` and `@settings(max_examples=100)` as specified in the design
    - Assert every original line is preserved in the output
    - Assert every required entry appears exactly once (no duplicates)
    - **Validates: Requirements 4.3**

- [x] 3. Create `pyproject.toml`
  - Write `pyproject.toml` at the project root with:
    - `[project]` section: name, version (`0.1.0`), description, `requires-python = ">=3.11"`
    - `[project.dependencies]`: `openai>=1.0`, `langchain>=0.3`, `langchain-openai>=0.2`, `langgraph>=0.2`, `python-dotenv>=1.0`, `pydantic>=2.0`, `pydantic-settings>=2.0`
    - `[project.optional-dependencies]` `dev` group: `ruff`, `pytest`, `pytest-cov`, `jupyterlab`, `ipykernel`
    - `[tool.ruff]`: `line-length = 100`, `target-version = "py311"`
    - `[tool.ruff.lint]`: `select = ["E", "F", "I"]`
    - `[tool.pytest.ini_options]`: `testpaths = ["tests"]`, `addopts = "-v"`
    - `[build-system]` using a PEP 517-compliant backend (hatchling or flit-core)
  - _Requirements: 2.1, 2.2, 2.3, 5.1, 5.2, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [x] 4. Create `.env.example`
  - Write `.env.example` at the project root with all four required keys and inline comments:
    - `OPENAI_API_KEY` — OpenAI API key for direct API access
    - `ANTHROPIC_API_KEY` — Anthropic API key for Claude models
    - `LANGCHAIN_API_KEY` — LangSmith API key for tracing
    - `LANGCHAIN_TRACING_V2` — Enable LangSmith tracing (`true`/`false`), defaulting to `false`
  - _Requirements: 3.1, 3.4_

- [x] 5. Implement `src/ai_foundation` Python package
  - [x] 5.1 Create `src/ai_foundation/__init__.py`
    - Minimal content: version string `__version__ = "0.1.0"` only, to avoid circular import issues
    - _Requirements: 7.1_

  - [x] 5.2 Create `src/ai_foundation/config.py` — Settings class
    - Implement the `Settings(BaseSettings)` class exactly as designed:
      - `model_config` with `env_file=".env"`, `env_file_encoding="utf-8"`, `case_sensitive=False`, `extra="ignore"`
      - Fields: `openai_api_key: str`, `anthropic_api_key: str`, `langchain_api_key: str`, `langchain_tracing_v2: bool` — all with `Field(default=...)` as specified
    - Instantiate module-level `settings = Settings()` singleton
    - _Requirements: 3.3, 7.2_

  - [ ]* 5.3 Write property test for Settings env var round-trip
    - **Property 1: Settings env var round-trip**
    - Use `hypothesis` with `@given(openai_key, anthropic_key, langchain_key, tracing)` and `@settings(max_examples=100)` as specified in the design
    - Write values to a temp `.env` file, instantiate `Settings(_env_file=str(env_file))`, assert all fields match the written values
    - **Validates: Requirements 3.3, 7.2**

  - [x] 5.4 Create `src/ai_foundation/llm.py` — LLM factory
    - Implement `get_llm(model: str = "gpt-4o-mini", temperature: float = 0.0) -> ChatOpenAI` as designed
    - Import `ChatOpenAI` from `langchain_openai` and `settings` from `ai_foundation.config`
    - _Requirements: 7.3_

  - [ ]* 5.5 Write unit tests for LLM factory
    - Test that `get_llm()` returns a `ChatOpenAI` instance when called with a mock API key (patch `settings.openai_api_key`)
    - Test that `model` and `temperature` parameters are passed through correctly
    - _Requirements: 7.3_

  - [x] 5.6 Create `src/ai_foundation/utils/__init__.py`
    - Empty `__init__.py` to make `utils` a package
    - _Requirements: 7.4_

  - [x] 5.7 Create `src/ai_foundation/utils/logging.py` — structured logging
    - Implement `configure_logging(level: int = logging.INFO) -> logging.Logger` as designed
    - Module-level `logger = configure_logging()` singleton
    - _Requirements: 7.4_

  - [ ]* 5.8 Write unit tests for logging module
    - Test that `configure_logging()` returns a `Logger` instance with the name `"ai_foundation"`
    - Test that calling `configure_logging()` multiple times does not raise errors (idempotent)
    - _Requirements: 7.4_

- [x] 6. Checkpoint — verify package imports cleanly
  - Ensure `from ai_foundation.config import Settings` imports without errors
  - Ensure `from ai_foundation.llm import get_llm` imports without errors
  - Ensure all tests written so far pass: `pytest tests/ -v`
  - Ensure all tests pass, ask the user if questions arise.
  - _Requirements: 7.5_

- [x] 7. Create `README.md`
  - Write `README.md` at the project root with the following sections:
    - **Project purpose** — what this repo is for (LLM / AI agentic systems development)
    - **Folder structure** — table or tree listing all top-level directories and their purposes
    - **Prerequisites** — Python 3.11+, `uv` installation instructions
    - **Setup instructions** — clone → `uv sync --all-extras` → copy `.env.example` to `.env` → fill in keys
  - _Requirements: 4.2_

- [x] 8. Run `uv sync` and export `requirements.txt`
  - Run `uv sync --all-extras` to create the virtual environment and resolve all dependencies from `pyproject.toml`
  - Export pinned dependencies to `requirements.txt` via `uv export --no-hashes -o requirements.txt` (or equivalent `uv pip freeze`)
  - Verify `uv sync` exits with code 0 (no dependency conflicts)
  - _Requirements: 2.4, 2.5_

- [x] 9. Run `ruff` linter against generated source files
  - Run `ruff check src/` and verify zero errors are reported
  - Run `ruff format --check src/` and verify all files are already formatted correctly
  - Fix any lint or format issues introduced by earlier tasks if they arise
  - _Requirements: 5.3_

- [x] 10. Final checkpoint — all tests pass and scaffold is clean
  - Run the full test suite: `pytest tests/ -v`
  - Confirm `uv.lock` and `requirements.txt` are present at the project root
  - Confirm all expected directories and files exist as specified in the design architecture diagram
  - Ensure all tests pass, ask the user if questions arise.
  - _Requirements: 2.4, 2.5, 5.3_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints (tasks 6 and 10) ensure incremental validation at key milestones
- Property tests (2.2, 5.3) use `hypothesis` and validate universal correctness properties
- Unit tests (5.5, 5.8) validate specific examples and edge cases
- Integration tests (`uv sync`, `ruff check`) are in tasks 8 and 9 and require `uv` and `ruff` installed in the environment
