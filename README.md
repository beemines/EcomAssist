# Ecommerce customer service

Python configuration and request contracts for the pure chat backend. This initial
task provides validated settings and schemas; API routes are added in later tasks.

## Setup

Use Python 3.11–3.13 and uv. Portable commands from the project directory:

```powershell
$env:UV_CACHE_DIR = '.cache/uv'
uv sync --locked --python 3.13
Copy-Item .env.example .env
uv run --locked pytest -q
```

On this workstation, create the virtual environment with the installed interpreter:

```powershell
$env:UV_CACHE_DIR = '.cache/uv'
uv sync --locked --python E:/miniconda3/python.exe
```

For POSIX shells, use `UV_CACHE_DIR=.cache/uv uv sync --locked --python 3.13`
and `UV_CACHE_DIR=.cache/uv uv run --locked pytest -q`.

Replace the API key placeholder in the project `.env` before using a real upstream.
Only declared keys are accepted. Constructor values override process environment,
which overrides dotenv, followed by secrets and defaults. `load_settings()` reads
`.env` in the process working directory, or accepts an explicit path. Keys stay
masked in settings representations; avoid logging raw validation `.errors()` data.

The input estimate budget defaults to 2,000 and the model output limit defaults to
512. Both budgets and the timeout must be positive. `.env.example` documents how
to select the upstream URL and its token limit field. Tests use dummy keys and
temporary dotenv files and do not make model calls.
