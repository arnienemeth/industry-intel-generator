"""Data ingestion module for GitHub trending repos and HackerNews top stories."""

import logging
import time
from datetime import datetime, timedelta, timezone

import requests

from src.utils import DATA_RAW, get_timestamp, save_json, setup_logging

logger = logging.getLogger(__name__)

# GitHub API
GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
GITHUB_LOOKBACK_DAYS = 7
GITHUB_PER_PAGE = 100

# HackerNews API
HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
HN_MAX_STORIES = 50
HN_REQUEST_DELAY = 0.5

# Shared
REQUEST_TIMEOUT = 30


def fetch_github_trending() -> list[dict]:
    """Fetches trending GitHub repositories created in the last 7 days.

    Returns:
        List of repository dicts with normalized fields.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=GITHUB_LOOKBACK_DAYS)
    cutoff_str = cutoff.strftime("%Y-%m-%d")

    params = {
        "q": f"created:>{cutoff_str}",
        "sort": "stars",
        "order": "desc",
        "per_page": GITHUB_PER_PAGE,
    }

    logger.info("Fetching GitHub repos created after %s", cutoff_str)
    response = requests.get(GITHUB_SEARCH_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    raw_items = response.json().get("items", [])
    logger.info("Received %d repositories from GitHub", len(raw_items))

    repos = []
    for item in raw_items:
        repos.append({
            "full_name": item["full_name"],
            "description": item.get("description") or "",
            "language": item.get("language") or "Unknown",
            "stars": item["stargazers_count"],
            "forks": item["forks_count"],
            "open_issues_count": item["open_issues_count"],
            "created_at": item["created_at"],
            "url": item["html_url"],
            "topics": item.get("topics", []),
        })

    return repos


def fetch_hackernews_top() -> list[dict]:
    """Fetches the top 50 stories from HackerNews.

    Uses a 0.5s delay between individual item requests. Skips items that
    fail to fetch or are not of type "story".

    Returns:
        List of story dicts with normalized fields.
    """
    logger.info("Fetching HackerNews top story IDs")
    response = requests.get(HN_TOP_STORIES_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    story_ids = response.json()[:HN_MAX_STORIES]
    logger.info("Fetching %d HackerNews stories", len(story_ids))

    stories = []
    for story_id in story_ids:
        try:
            item_url = HN_ITEM_URL.format(item_id=story_id)
            item_resp = requests.get(item_url, timeout=REQUEST_TIMEOUT)
            item_resp.raise_for_status()
            item = item_resp.json()
        except (requests.RequestException, ValueError) as exc:
            logger.warning("Failed to fetch HN item %s: %s", story_id, exc)
            time.sleep(HN_REQUEST_DELAY)
            continue

        if item.get("type") != "story":
            time.sleep(HN_REQUEST_DELAY)
            continue

        stories.append({
            "id": item["id"],
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "score": item.get("score", 0),
            "author": item.get("by", ""),
            "comments": item.get("descendants", 0),
            "time": item.get("time", 0),
        })

        time.sleep(HN_REQUEST_DELAY)

    logger.info("Collected %d HackerNews stories", len(stories))
    return stories


def run_ingestion() -> dict:
    """Runs the full ingestion pipeline for all sources.

    Fetches data from GitHub and HackerNews, saves timestamped JSON files
    into data/raw/, and returns a summary dict.

    Returns:
        Summary dict with source names mapped to record counts.
    """
    timestamp = get_timestamp()

    github_repos = fetch_github_trending()
    github_path = DATA_RAW / f"github_{timestamp}.json"
    save_json(github_repos, github_path)

    hn_stories = fetch_hackernews_top()
    hn_path = DATA_RAW / f"hackernews_{timestamp}.json"
    save_json(hn_stories, hn_path)

    summary = {
        "timestamp": timestamp,
        "github_repos": len(github_repos),
        "hackernews_stories": len(hn_stories),
    }
    logger.info("Ingestion complete: %s", summary)
    return summary


if __name__ == "__main__":
    setup_logging()
    run_ingestion()
