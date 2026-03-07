"""Trend analysis engine for GitHub and HackerNews data."""

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.utils import (
    DATA_PROCESSED,
    DATA_RAW,
    calculate_growth_rate,
    get_latest_file,
    get_timestamp,
    load_json,
    save_json,
    setup_logging,
)

logger = logging.getLogger(__name__)

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "AI/ML": [
        "ai", "ml", "machine-learning", "deep-learning",
        "llm", "gpt", "neural", "transformer",
    ],
    "Web Development": [
        "web", "react", "vue", "angular", "nextjs",
        "frontend", "backend", "api",
    ],
    "DevOps/Infra": [
        "docker", "kubernetes", "ci-cd", "terraform",
        "cloud", "devops", "infrastructure",
    ],
    "Security": [
        "security", "crypto", "encryption", "vulnerability",
        "auth", "pentest",
    ],
    "Data Engineering": [
        "data", "pipeline", "etl", "database",
        "sql", "analytics", "streaming",
    ],
    "Mobile": [
        "ios", "android", "flutter", "react-native",
        "mobile", "swift", "kotlin",
    ],
}


def classify_category(repo: dict) -> str:
    """Classifies a repository into a technology category based on keywords.

    Joins the repo's topics, description, and full_name into a single
    lowercase string and scores each category by counting keyword matches.

    Args:
        repo: A repository dict with "topics", "description", and "full_name".

    Returns:
        The highest-scoring category name, or "Other" if no keywords match.
    """
    text = " ".join([
        " ".join(repo.get("topics", [])),
        repo.get("description", ""),
        repo.get("full_name", ""),
    ]).lower()

    best_category = "Other"
    best_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_category = category

    return best_category


def analyze_languages(repos: list[dict]) -> list[dict]:
    """Analyzes programming language distribution across repositories.

    Args:
        repos: List of repository dicts with "language" and "stars" fields.

    Returns:
        List of language stats sorted by repo count descending. Each entry
        contains language, count, percentage, and total_stars.
    """
    lang_counts: dict[str, int] = {}
    lang_stars: dict[str, int] = {}

    for repo in repos:
        lang = repo.get("language", "Unknown")
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
        lang_stars[lang] = lang_stars.get(lang, 0) + repo.get("stars", 0)

    total = len(repos) or 1
    results = []
    for lang, count in lang_counts.items():
        results.append({
            "language": lang,
            "count": count,
            "percentage": round(count / total * 100, 1),
            "total_stars": lang_stars[lang],
        })

    results.sort(key=lambda x: x["count"], reverse=True)
    return results


def analyze_top_repos(repos: list[dict], limit: int = 10) -> list[dict]:
    """Returns the top repositories sorted by star count.

    Args:
        repos: List of repository dicts.
        limit: Maximum number of repos to return.

    Returns:
        List of top repo dicts with key metrics and category classification.
    """
    sorted_repos = sorted(repos, key=lambda r: r.get("stars", 0), reverse=True)

    top = []
    for repo in sorted_repos[:limit]:
        stars = repo.get("stars", 0)
        forks = repo.get("forks", 0)
        engagement = round(forks / stars, 3) if stars > 0 else 0.0
        description = repo.get("description", "")
        if len(description) > 120:
            description = description[:120]

        top.append({
            "name": repo.get("full_name", ""),
            "description": description,
            "language": repo.get("language", "Unknown"),
            "stars": stars,
            "forks": forks,
            "engagement_ratio": engagement,
            "category": classify_category(repo),
            "url": repo.get("url", ""),
        })

    return top


def analyze_categories(repos: list[dict]) -> list[dict]:
    """Analyzes category distribution across all repositories.

    Args:
        repos: List of repository dicts.

    Returns:
        List of category stats sorted by count descending, each with
        category name, count, and percentage.
    """
    cat_counts: dict[str, int] = {}
    for repo in repos:
        category = classify_category(repo)
        cat_counts[category] = cat_counts.get(category, 0) + 1

    total = len(repos) or 1
    results = []
    for category, count in cat_counts.items():
        results.append({
            "category": category,
            "count": count,
            "percentage": round(count / total * 100, 1),
        })

    results.sort(key=lambda x: x["count"], reverse=True)
    return results


def analyze_hackernews(stories: list[dict]) -> dict:
    """Computes summary statistics for HackerNews stories.

    Args:
        stories: List of story dicts with "score", "descendants"/"comments",
            and "title" fields.

    Returns:
        Dict with total_stories, avg_score, avg_comments, max_score,
        and top_5_stories.
    """
    if not stories:
        return {
            "total_stories": 0,
            "avg_score": 0.0,
            "avg_comments": 0.0,
            "max_score": 0,
            "top_5_stories": [],
        }

    scores = [s.get("score", 0) for s in stories]
    comments = [s.get("comments", 0) for s in stories]

    sorted_stories = sorted(stories, key=lambda s: s.get("score", 0), reverse=True)
    top_5 = [
        {
            "title": s.get("title", ""),
            "url": s.get("url", ""),
            "score": s.get("score", 0),
            "comments": s.get("comments", 0),
            "author": s.get("author", ""),
        }
        for s in sorted_stories[:5]
    ]

    return {
        "total_stories": len(stories),
        "avg_score": round(sum(scores) / len(scores), 1),
        "avg_comments": round(sum(comments) / len(comments), 1),
        "max_score": max(scores),
        "top_5_stories": top_5,
    }


def compute_week_over_week(
    current_langs: list[dict],
    previous_langs: list[dict],
) -> list[dict]:
    """Computes week-over-week changes in language popularity.

    Args:
        current_langs: Current week's language stats from analyze_languages.
        previous_langs: Previous week's language stats from analyze_languages.

    Returns:
        List of dicts with language, current/previous counts, delta, and
        growth_rate percentage for the top 15 current languages.
    """
    prev_map = {entry["language"]: entry["count"] for entry in previous_langs}

    results = []
    for entry in current_langs[:15]:
        lang = entry["language"]
        current_count = entry["count"]
        previous_count = prev_map.get(lang, 0)
        delta = current_count - previous_count
        growth = calculate_growth_rate(current_count, previous_count)

        results.append({
            "language": lang,
            "current_count": current_count,
            "previous_count": previous_count,
            "delta": delta,
            "growth_rate": round(growth * 100, 1),
        })

    return results


def run_analysis() -> dict:
    """Runs the full analysis pipeline on the latest raw data.

    Loads the most recent GitHub and HackerNews JSON files from data/raw/,
    performs all analyses, and saves the compiled results to
    data/processed/analysis_YYYY-MM-DD.json.

    Returns:
        The complete analysis results dict.
    """
    timestamp = get_timestamp()

    github_file = get_latest_file(DATA_RAW, "github_")
    if github_file is None:
        logger.error("No GitHub data found in %s", DATA_RAW)
        return {}
    logger.info("Loading GitHub data from %s", github_file)
    repos = load_json(github_file)

    hn_file = get_latest_file(DATA_RAW, "hackernews_")
    hn_stories: list[dict] = []
    if hn_file is not None:
        logger.info("Loading HackerNews data from %s", hn_file)
        hn_stories = load_json(hn_file)
    else:
        logger.warning("No HackerNews data found, skipping HN analysis")

    languages = analyze_languages(repos)
    top_repos = analyze_top_repos(repos)
    categories = analyze_categories(repos)
    hn_analysis = analyze_hackernews(hn_stories)

    # Week-over-week comparison
    wow: list[dict] = []
    prev_date = (
        datetime.now(timezone.utc) - timedelta(days=7)
    ).strftime("%Y-%m-%d")
    prev_file = DATA_RAW / f"github_{prev_date}.json"
    if prev_file.exists():
        logger.info("Found previous week data at %s", prev_file)
        prev_repos = load_json(prev_file)
        prev_languages = analyze_languages(prev_repos)
        wow = compute_week_over_week(languages, prev_languages)
    else:
        logger.info("No previous week data found for week-over-week comparison")

    # Compile results
    top_language = languages[0]["language"] if languages else "N/A"
    top_category = categories[0]["category"] if categories else "N/A"

    results = {
        "metadata": {
            "analysis_date": timestamp,
            "github_source": str(github_file),
            "hackernews_source": str(hn_file) if hn_file else None,
            "total_repos_analyzed": len(repos),
            "total_stories_analyzed": len(hn_stories),
        },
        "languages": languages,
        "top_repositories": top_repos,
        "categories": categories,
        "hackernews": hn_analysis,
        "week_over_week": wow,
        "summary": {
            "dominant_language": top_language,
            "dominant_category": top_category,
            "total_repos": len(repos),
            "total_stars": sum(r.get("stars", 0) for r in repos),
            "avg_stars": round(
                sum(r.get("stars", 0) for r in repos) / (len(repos) or 1), 1
            ),
        },
    }

    output_path = DATA_PROCESSED / f"analysis_{timestamp}.json"
    save_json(results, output_path)
    logger.info("Analysis saved to %s", output_path)

    return results


if __name__ == "__main__":
    setup_logging()
    run_analysis()
