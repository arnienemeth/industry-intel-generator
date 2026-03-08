"""Interactive HTML dashboard generator for industry intelligence reports."""

import json
import logging
from pathlib import Path
from typing import Any

try:
    from src.utils import DATA_PROCESSED, get_latest_file, get_timestamp, load_json, setup_logging
except ImportError:
    from utils import DATA_PROCESSED, get_latest_file, get_timestamp, load_json, setup_logging

logger = logging.getLogger(__name__)


def generate_dashboard(analysis: dict[str, Any]) -> str:
    """Builds an interactive HTML dashboard from analysis data.

    Args:
        analysis: Parsed analysis JSON containing languages, repos, categories,
            hackernews data, and summary.

    Returns:
        Complete HTML string for the dashboard.
    """
    metadata = analysis.get("metadata", {})
    summary = analysis.get("summary", {})
    languages = analysis.get("languages", [])
    categories = analysis.get("categories", [])
    top_repos = analysis.get("top_repositories", [])
    hn_data = analysis.get("hackernews", {})
    top_stories = hn_data.get("top_5_stories", [])

    date = metadata.get("analysis_date", get_timestamp())
    total_repos = metadata.get("total_repos_analyzed", 0)
    total_stories = metadata.get("total_stories_analyzed", 0)

    top_language = summary.get("dominant_language", "N/A")
    hottest_category = summary.get("dominant_category", "N/A")
    avg_hn_score = hn_data.get("avg_score", 0)

    # Prepare chart data
    lang_labels = json.dumps([l["language"] for l in languages[:10]])
    lang_counts = json.dumps([l["count"] for l in languages[:10]])
    cat_labels = json.dumps([c["category"] for c in categories])
    cat_counts = json.dumps([c["count"] for c in categories])

    # Build repo rows
    repo_rows = ""
    for repo in top_repos[:10]:
        name = repo.get("name", "")
        url = repo.get("url", "#")
        lang = repo.get("language", "Unknown")
        stars = repo.get("stars", 0)
        forks = repo.get("forks", 0)
        cat = repo.get("category", "Other")
        repo_rows += f"""<tr>
            <td><a href="{url}" target="_blank">{name}</a></td>
            <td><span class="badge">{lang}</span></td>
            <td>{stars:,}</td>
            <td>{forks:,}</td>
            <td><span class="badge cat-badge">{cat}</span></td>
        </tr>\n"""

    # Build story rows
    story_rows = ""
    for story in top_stories[:5]:
        title = story.get("title", "")
        url = story.get("url", "")
        link = f'<a href="{url}" target="_blank">{title}</a>' if url else title
        score = story.get("score", 0)
        comments = story.get("comments", 0)
        story_rows += f"""<tr>
            <td>{link}</td>
            <td>{score:,}</td>
            <td>{comments:,}</td>
        </tr>\n"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Industry Intelligence Report - {date}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ text-align: center; margin-bottom: 2rem; }}
        header h1 {{ font-size: 2rem; color: #e2e8f0; margin-bottom: 0.25rem; }}
        header p {{ color: #94a3b8; font-size: 1rem; }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .kpi-card {{
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        }}
        .kpi-card .value {{
            font-size: 2rem;
            font-weight: 700;
            color: #3b82f6;
        }}
        .kpi-card .label {{
            color: #94a3b8;
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .chart-card {{
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
        }}
        .chart-card h2 {{
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: #e2e8f0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 2rem;
        }}
        th, td {{
            text-align: left;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #334155;
        }}
        th {{ color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; }}
        td a {{ color: #3b82f6; text-decoration: none; }}
        td a:hover {{ text-decoration: underline; }}
        .badge {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            background: #3b82f6;
            color: #e2e8f0;
        }}
        .cat-badge {{ background: #6366f1; }}
        .section {{
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .section h2 {{
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: #e2e8f0;
        }}
        footer {{
            text-align: center;
            color: #94a3b8;
            font-size: 0.8rem;
            padding-top: 1rem;
            border-top: 1px solid #334155;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Industry Intelligence Report</h1>
            <p>{date} &mdash; {total_repos} repos, {total_stories} stories analyzed</p>
        </header>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="value">{total_repos}</div>
                <div class="label">Total Trending Repos</div>
            </div>
            <div class="kpi-card">
                <div class="value">{top_language}</div>
                <div class="label">Top Language</div>
            </div>
            <div class="kpi-card">
                <div class="value">{hottest_category}</div>
                <div class="label">Hottest Category</div>
            </div>
            <div class="kpi-card">
                <div class="value">{avg_hn_score}</div>
                <div class="label">Avg HN Score</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-card">
                <h2>Top 10 Languages by Count</h2>
                <canvas id="langChart"></canvas>
            </div>
            <div class="chart-card">
                <h2>Category Breakdown</h2>
                <canvas id="catChart"></canvas>
            </div>
        </div>

        <div class="section">
            <h2>Top 10 Repositories</h2>
            <table>
                <thead>
                    <tr>
                        <th>Repository</th>
                        <th>Language</th>
                        <th>Stars</th>
                        <th>Forks</th>
                        <th>Category</th>
                    </tr>
                </thead>
                <tbody>
                    {repo_rows}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Top 5 HackerNews Stories</h2>
            <table>
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Score</th>
                        <th>Comments</th>
                    </tr>
                </thead>
                <tbody>
                    {story_rows}
                </tbody>
            </table>
        </div>

        <footer>
            Generated by Industry Intelligence Pipeline &mdash;
            Built with Claude Code + Claude Cowork
        </footer>
    </div>

    <script>
        const langLabels = {lang_labels};
        const langCounts = {lang_counts};
        const catLabels = {cat_labels};
        const catCounts = {cat_counts};

        const colors = [
            '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
            '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e',
            '#14b8a6', '#06b6d4'
        ];

        new Chart(document.getElementById('langChart'), {{
            type: 'bar',
            data: {{
                labels: langLabels,
                datasets: [{{
                    label: 'Repositories',
                    data: langCounts,
                    backgroundColor: colors.slice(0, langLabels.length),
                    borderRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{
                        ticks: {{ color: '#94a3b8' }},
                        grid: {{ color: '#334155' }}
                    }},
                    x: {{
                        ticks: {{ color: '#94a3b8' }},
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});

        new Chart(document.getElementById('catChart'), {{
            type: 'doughnut',
            data: {{
                labels: catLabels,
                datasets: [{{
                    data: catCounts,
                    backgroundColor: colors.slice(0, catLabels.length),
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{ color: '#94a3b8', padding: 16 }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
    return html


def run_dashboard() -> Path:
    """Loads the latest analysis JSON, generates the dashboard, and saves it.

    Returns:
        Path to the generated HTML dashboard file.
    """
    setup_logging()
    analysis_path = get_latest_file(DATA_PROCESSED, "analysis_")
    if analysis_path is None:
        raise FileNotFoundError("No analysis JSON found in data/processed/")

    logger.info("Loading analysis from %s", analysis_path)
    analysis = load_json(analysis_path)

    html = generate_dashboard(analysis)
    timestamp = get_timestamp()
    output_path = DATA_PROCESSED / f"dashboard_{timestamp}.html"
    output_path.write_text(html, encoding="utf-8")
    logger.info("Dashboard saved to %s", output_path)
    return output_path


if __name__ == "__main__":
    path = run_dashboard()
    print(f"Dashboard generated: {path}")
