# CLAUDE.md — Project Conventions

## Language & Style

- Python 3.10+ required
- Type hints on all functions (parameters and return types)
- Use `pathlib.Path` for file paths — never string concatenation
- Google-style docstrings on every public function
- Max line length: 100 characters
- Linter: `ruff` (config follows requirements.txt version)

## File Naming

- All data files use ISO 8601 dates in filenames: `<source>_YYYY-MM-DD.json`
  - Example: `github_2026-03-07.json`, `hackernews_2026-03-07.json`

## Directory Structure

- `src/` — Core library code: API clients, data processing, report generation
- `data/raw/` — Raw JSON responses from external APIs (git-ignored via .gitignore)
- `data/processed/` — Cleaned/transformed data ready for analysis
- `deliverables/` — Final outputs: weekly reports, trend summaries, charts
- `tests/` — Pytest test suite mirroring `src/` structure
- `scripts/` — CLI entry points and automation scripts (e.g. weekly pipeline runner)
- `docs/` — Project documentation and architecture notes
- `.github/workflows/` — GitHub Actions CI/CD definitions

## API Rate Limits

- **GitHub API:** 60 requests/hour unauthenticated. Use a token when possible.
- **HackerNews API:** No official rate limit, but use 0.5s delays between requests.

## Testing

- Run tests: `py -m pytest tests/ -v`
- All external API calls must be mocked in tests — no live network requests
- Use `unittest.mock.patch` or `pytest-mock` for mocking
