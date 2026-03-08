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

    css = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            line-height: 1.6;
            padding: 2rem;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 2rem; }
        header h1 { font-size: 2rem; color: #e2e8f0; margin-bottom: 0.25rem; }
        header p { color: #94a3b8; font-size: 1rem; }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .kpi-card {
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        }
        .kpi-card .value {
            font-size: 2rem;
            font-weight: 700;
            color: #3b82f6;
        }
        .kpi-card .label {
            color: #94a3b8;
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        .chart-card {
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
        }
        .chart-card h2 {
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: #e2e8f0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 2rem;
        }
        th, td {
            text-align: left;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #334155;
        }
        th { color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; }
        td a { color: #3b82f6; text-decoration: none; }
        td a:hover { text-decoration: underline; }
        .badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            background: #3b82f6;
            color: #e2e8f0;
        }
        .cat-badge { background: #6366f1; }
        .section {
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }
        .section h2 {
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: #e2e8f0;
        }
        footer {
            text-align: center;
            color: #94a3b8;
            font-size: 0.8rem;
            padding-top: 1rem;
            border-top: 1px solid #334155;
        }
    """

    script = (
        "        const langLabels = " + lang_labels + ";\n"
        "        const langCounts = " + lang_counts + ";\n"
        "        const catLabels = " + cat_labels + ";\n"
        "        const catCounts = " + cat_counts + ";\n"
        "\n"
        "        const colors = [\n"
        "            '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',\n"
        "            '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e',\n"
        "            '#14b8a6', '#06b6d4'\n"
        "        ];\n"
        "\n"
        "        new Chart(document.getElementById('langChart'), {\n"
        "            type: 'bar',\n"
        "            data: {\n"
        "                labels: langLabels,\n"
        "                datasets: [{\n"
        "                    label: 'Repositories',\n"
        "                    data: langCounts,\n"
        "                    backgroundColor: colors.slice(0, langLabels.length),\n"
        "                    borderRadius: 6\n"
        "                }]\n"
        "            },\n"
        "            options: {\n"
        "                responsive: true,\n"
        "                plugins: { legend: { display: false } },\n"
        "                scales: {\n"
        "                    y: {\n"
        "                        ticks: { color: '#94a3b8' },\n"
        "                        grid: { color: '#334155' }\n"
        "                    },\n"
        "                    x: {\n"
        "                        ticks: { color: '#94a3b8' },\n"
        "                        grid: { display: false }\n"
        "                    }\n"
        "                }\n"
        "            }\n"
        "        });\n"
        "\n"
        "        new Chart(document.getElementById('catChart'), {\n"
        "            type: 'doughnut',\n"
        "            data: {\n"
        "                labels: catLabels,\n"
        "                datasets: [{\n"
        "                    data: catCounts,\n"
        "                    backgroundColor: colors.slice(0, catLabels.length),\n"
        "                    borderWidth: 0\n"
        "                }]\n"
        "            },\n"
        "            options: {\n"
        "                responsive: true,\n"
        "                plugins: {\n"
        "                    legend: {\n"
        "                        position: 'bottom',\n"
        "                        labels: { color: '#94a3b8', padding: 16 }\n"
        "                    }\n"
        "                }\n"
        "            }\n"
        "        });\n"
    )

    html = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '    <meta charset="UTF-8">\n'
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f"    <title>Industry Intelligence Report - {date}</title>\n"
        '    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>\n'
        f"    <style>{css}    </style>\n"
        "</head>\n"
        "<body>\n"
        '    <div class="container">\n'
        "        <header>\n"
        "            <h1>Industry Intelligence Report</h1>\n"
        f"            <p>{date} &mdash; {total_repos} repos,"
        f" {total_stories} stories analyzed</p>\n"
        "        </header>\n"
        "\n"
        '        <div class="kpi-grid">\n'
        '            <div class="kpi-card">\n'
        f'                <div class="value">{total_repos}</div>\n'
        '                <div class="label">Total Trending Repos</div>\n'
        "            </div>\n"
        '            <div class="kpi-card">\n'
        f'                <div class="value">{top_language}</div>\n'
        '                <div class="label">Top Language</div>\n'
        "            </div>\n"
        '            <div class="kpi-card">\n'
        f'                <div class="value">{hottest_category}</div>\n'
        '                <div class="label">Hottest Category</div>\n'
        "            </div>\n"
        '            <div class="kpi-card">\n'
        f'                <div class="value">{avg_hn_score}</div>\n'
        '                <div class="label">Avg HN Score</div>\n'
        "            </div>\n"
        "        </div>\n"
        "\n"
        '        <div class="charts-grid">\n'
        '            <div class="chart-card">\n'
        "                <h2>Top 10 Languages by Count</h2>\n"
        '                <canvas id="langChart"></canvas>\n'
        "            </div>\n"
        '            <div class="chart-card">\n'
        "                <h2>Category Breakdown</h2>\n"
        '                <canvas id="catChart"></canvas>\n'
        "            </div>\n"
        "        </div>\n"
        "\n"
        '        <div class="section">\n'
        "            <h2>Top 10 Repositories</h2>\n"
        "            <table>\n"
        "                <thead>\n"
        "                    <tr>\n"
        "                        <th>Repository</th>\n"
        "                        <th>Language</th>\n"
        "                        <th>Stars</th>\n"
        "                        <th>Forks</th>\n"
        "                        <th>Category</th>\n"
        "                    </tr>\n"
        "                </thead>\n"
        f"                <tbody>\n                    {repo_rows}"
        "                </tbody>\n"
        "            </table>\n"
        "        </div>\n"
        "\n"
        '        <div class="section">\n'
        "            <h2>Top 5 HackerNews Stories</h2>\n"
        "            <table>\n"
        "                <thead>\n"
        "                    <tr>\n"
        "                        <th>Title</th>\n"
        "                        <th>Score</th>\n"
        "                        <th>Comments</th>\n"
        "                    </tr>\n"
        "                </thead>\n"
        f"                <tbody>\n                    {story_rows}"
        "                </tbody>\n"
        "            </table>\n"
        "        </div>\n"
        "\n"
        "        <footer>\n"
        "            Generated by Industry Intelligence Pipeline &mdash;\n"
        "            Built with Claude Code + Claude Cowork\n"
        "        </footer>\n"
        "    </div>\n"
        "\n"
        f"    <script>\n{script}    </script>\n"
        "</body>\n"
        "</html>"
    )
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
