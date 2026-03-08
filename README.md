# Industry Intelligence Report Generator

### From raw API data to polished executive reports — fully automated.

Built entirely with **Claude Code** (engineering) and **Claude Cowork** (business deliverables).

---

## The Problem

Compiling weekly industry intelligence reports is tedious, repetitive work that eats hours every Monday morning. Analysts manually pull data from multiple sources, crunch numbers in spreadsheets, and format the same slides and docs week after week.

## The Solution

1. **Pulls data** from the GitHub Trending API and HackerNews Top Stories API
2. **Analyzes trends** — language popularity, category classification, week-over-week growth, and engagement metrics
3. **Generates an interactive dashboard** — a self-contained HTML report with Chart.js visualizations
4. **Produces executive deliverables** — polished Word reports, PowerPoint decks, and Excel workbooks ready for stakeholders

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Claude Code                        │
│                                                         │
│   ingest.py ──► analyze.py ──► dashboard.py             │
│       │              │               │                  │
│   data/raw/    data/processed/   dashboard.html         │
│   (GitHub,     (analysis JSON)   (Chart.js)             │
│    HackerNews)                                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼  JSON exports
┌──────────────────────────────────────────────────────────┐
│                    Claude Cowork                          │
│                                                          │
│   analysis.json ──► Weekly Report (docx)                 │
│                 ──► Executive Deck (pptx)                 │
│                 ──► Data Workbook (xlsx)                  │
└──────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
git clone https://github.com/arnienemeth/industry-intel-generator.git
cd industry-intel-generator
pip install -r requirements.txt
python scripts/run_pipeline.py
```

## Project Structure

```
industry-intel-generator/
├── src/                        # Core library code
│   ├── ingest.py               # GitHub + HackerNews API clients
│   ├── analyze.py              # Trend analysis engine
│   ├── dashboard.py            # Interactive HTML dashboard generator
│   └── utils.py                # Shared helpers (paths, JSON I/O, logging)
├── tests/                      # Pytest test suite
│   ├── test_ingest.py          # Ingestion module tests
│   ├── test_analyze.py         # Analysis module tests
│   └── test_utils.py           # Utility function tests
├── scripts/                    # CLI entry points and automation
├── data/
│   ├── raw/                    # Raw API responses (git-ignored)
│   └── processed/              # Cleaned analysis JSON + dashboards
├── deliverables/               # Final Word, PowerPoint, Excel outputs
├── docs/                       # Project documentation
├── .github/workflows/
│   ├── ci.yml                  # CI: lint + test on push/PR
│   └── weekly-pipeline.yml     # Scheduled weekly data pull (Monday 6am UTC)
├── requirements.txt            # Python dependencies
└── CLAUDE.md                   # Project conventions for Claude Code
```

## How It Was Built

### Engineering — Claude Code

The entire codebase was built through conversational prompts with Claude Code. Examples:

- *"Create an ingestion module that pulls GitHub trending repos and HackerNews top stories, saves them as timestamped JSON"*
- *"Add a trend analysis engine — classify repos by category, compute language stats, week-over-week growth"*
- *"Generate an interactive HTML dashboard with Chart.js — dark theme, KPI cards, bar and doughnut charts"*
- *"Add CI with GitHub Actions — matrix test across Python 3.10-3.12, lint with ruff, run pytest"*
- *"Create a weekly scheduled pipeline that ingests, analyzes, builds the dashboard, and auto-commits"*

Each prompt produced working, tested code in a single pass. Claude Code handled the architecture decisions, file organization, error handling, and test coverage.

### Business Deliverables — Claude Cowork

The machine-readable JSON output from the pipeline feeds directly into Claude Cowork, which transforms it into executive-ready deliverables:

- **Word Report** — narrative summary with key findings, charts, and recommendations
- **PowerPoint Deck** — slide-by-slide executive briefing with embedded visualizations
- **Excel Workbook** — multi-sheet data workbook with pivot-ready tables and charts

The Cowork workflow reads the analysis JSON, interprets the trends, and produces formatted documents that are ready to send to stakeholders — no manual formatting required.

## Key Insight

> **Claude Code** produces machine-readable output (JSON, HTML, Python).
> **Claude Cowork** produces human-readable output (docx, pptx, xlsx).
>
> Together, they cover the full pipeline from raw data to boardroom-ready deliverables.

## Technologies

- **Python** — Core language (3.10+)
- **Requests** — HTTP client for API calls
- **Pandas** — Data manipulation and analysis
- **Chart.js** — Interactive browser-based visualizations
- **GitHub Actions** — CI/CD and scheduled automation
- **Claude Code** — AI-powered software engineering
- **Claude Cowork** — AI-powered business document generation

## License

MIT
