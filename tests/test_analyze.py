"""Tests for src/analyze.py trend analysis functions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analyze import analyze_categories, analyze_languages, analyze_top_repos, classify_category

SAMPLE_REPOS: list[dict] = [
    {
        "full_name": "org/ml-framework",
        "description": "A deep learning neural network framework",
        "language": "Python",
        "stars": 5000,
        "forks": 800,
        "open_issues_count": 50,
        "topics": ["machine-learning", "ai"],
        "url": "https://github.com/org/ml-framework",
    },
    {
        "full_name": "org/web-app",
        "description": "Modern React frontend dashboard",
        "language": "TypeScript",
        "stars": 3000,
        "forks": 400,
        "open_issues_count": 30,
        "topics": ["react", "frontend"],
        "url": "https://github.com/org/web-app",
    },
    {
        "full_name": "org/deploy-tool",
        "description": "Kubernetes container orchestration CLI",
        "language": "Go",
        "stars": 2000,
        "forks": 200,
        "open_issues_count": 15,
        "topics": ["kubernetes", "docker", "devops"],
        "url": "https://github.com/org/deploy-tool",
    },
    {
        "full_name": "org/data-pipeline",
        "description": "A transformer model training pipeline",
        "language": "Python",
        "stars": 1500,
        "forks": 150,
        "open_issues_count": 10,
        "topics": ["transformer", "nlp"],
        "url": "https://github.com/org/data-pipeline",
    },
]


class TestClassifyCategory:
    def test_ai_ml(self) -> None:
        assert classify_category(SAMPLE_REPOS[0]) == "AI/ML"

    def test_web_development(self) -> None:
        assert classify_category(SAMPLE_REPOS[1]) == "Web Development"

    def test_devops_infra(self) -> None:
        assert classify_category(SAMPLE_REPOS[2]) == "DevOps/Infra"

    def test_unknown_returns_other(self) -> None:
        repo = {
            "full_name": "org/misc-tool",
            "description": "A random utility",
            "language": "Rust",
            "topics": [],
        }
        assert classify_category(repo) == "Other"


class TestAnalyzeLanguages:
    def test_sorted_by_count(self) -> None:
        result = analyze_languages(SAMPLE_REPOS)
        assert result[0]["language"] == "Python"
        assert result[0]["count"] == 2

    def test_percentages_sum_to_100(self) -> None:
        result = analyze_languages(SAMPLE_REPOS)
        total = sum(entry["percentage"] for entry in result)
        assert abs(total - 100.0) < 1.0

    def test_includes_star_totals(self) -> None:
        result = analyze_languages(SAMPLE_REPOS)
        python_entry = next(e for e in result if e["language"] == "Python")
        assert python_entry["total_stars"] == 6500


class TestAnalyzeTopRepos:
    def test_returns_correct_limit(self) -> None:
        result = analyze_top_repos(SAMPLE_REPOS, limit=2)
        assert len(result) == 2

    def test_sorted_by_stars(self) -> None:
        result = analyze_top_repos(SAMPLE_REPOS, limit=4)
        stars = [r["stars"] for r in result]
        assert stars == sorted(stars, reverse=True)

    def test_includes_engagement_ratio(self) -> None:
        result = analyze_top_repos(SAMPLE_REPOS, limit=1)
        assert "engagement_ratio" in result[0]
        assert result[0]["engagement_ratio"] == 800 / 5000

    def test_includes_category(self) -> None:
        result = analyze_top_repos(SAMPLE_REPOS, limit=1)
        assert "category" in result[0]


class TestAnalyzeCategories:
    def test_returns_all_found_categories(self) -> None:
        result = analyze_categories(SAMPLE_REPOS)
        category_names = [c["category"] for c in result]
        assert "AI/ML" in category_names
        assert "Web Development" in category_names
        assert "DevOps/Infra" in category_names

    def test_sorted_by_count(self) -> None:
        result = analyze_categories(SAMPLE_REPOS)
        counts = [c["count"] for c in result]
        assert counts == sorted(counts, reverse=True)
