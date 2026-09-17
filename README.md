# AI Project Foundation

A repository for building LLM-powered applications and AI agentic systems. It contains reusable scaffolding for LangChain/LangGraph apps, autonomous AI agents, experiments and prototypes, and shared utilities for configuration, logging, and LLM client management.

---

## Folder Structure

```
project-root/
├── src/ai_foundation/   # Core Python package (Settings, LLM factory, logging utilities)
├── agents/              # AI agent definitions, graphs, and orchestration logic
├── notebooks/           # Jupyter notebooks for experimentation and exploration
├── data/
│   ├── raw/             # Raw input data
│   ├── processed/       # Cleaned and transformed data
│   └── outputs/         # Model outputs and generated artifacts
├── configs/             # Environment-specific YAML/TOML configuration files
├── tests/               # Unit, integration, and evaluation tests
├── docs/                # Project documentation and architecture decision records
└── scripts/             # Standalone utility and automation scripts
```

---

## Prerequisites

- **Python 3.11+**
- **uv** — fast Python package and project manager

Install `uv` by following the [official installation instructions](https://docs.astral.sh/uv/getting-started/installation/).

---

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Install all dependencies (including dev extras):
   ```bash
   uv sync --all-extras
   ```

3. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

4. Fill in your API keys in `.env`:
   ```
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   LANGCHAIN_API_KEY=ls__...
   LANGCHAIN_TRACING_V2=false
   ```

5. (Optional) Activate the virtual environment:
   - Linux / macOS: `source .venv/bin/activate`
   - Windows: `.venv\Scripts\activate`

---

## Quick Start

```python
from ai_foundation.llm import get_llm

llm = get_llm()
response = llm.invoke("Hello!")
print(response.content)
```

`get_llm()` accepts optional `model` and `temperature` arguments and defaults to `gpt-4o-mini` with `temperature=0.0`.

---

## Development

Run the test suite:
```bash
uv run pytest
```

Lint the source code:
```bash
uv run ruff check src/
```

Format the source code:
```bash
uv run ruff format src/
```
