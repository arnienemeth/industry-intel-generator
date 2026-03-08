"""Tests for src/ingest.py data ingestion functions."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ingest import fetch_github_trending, fetch_hackernews_top


class TestFetchGithubTrending:
    @patch("ingest.requests.get")
    def test_returns_formatted_repos(self, mock_get: MagicMock) -> None:
        mock_get.return_value.json.return_value = {
            "items": [
                {
                    "full_name": "owner/repo",
                    "description": "A cool project",
                    "language": "Python",
                    "stargazers_count": 100,
                    "forks_count": 20,
                    "open_issues_count": 5,
                    "created_at": "2026-03-01T00:00:00Z",
                    "html_url": "https://github.com/owner/repo",
                    "topics": ["ai"],
                }
            ]
        }
        mock_get.return_value.raise_for_status = MagicMock()

        repos = fetch_github_trending()

        assert len(repos) == 1
        repo = repos[0]
        assert repo["full_name"] == "owner/repo"
        assert repo["description"] == "A cool project"
        assert repo["language"] == "Python"
        assert repo["stars"] == 100
        assert repo["forks"] == 20
        assert repo["url"] == "https://github.com/owner/repo"
        assert repo["topics"] == ["ai"]

    @patch("ingest.requests.get")
    def test_handles_none_description_and_language(self, mock_get: MagicMock) -> None:
        mock_get.return_value.json.return_value = {
            "items": [
                {
                    "full_name": "owner/repo",
                    "description": None,
                    "language": None,
                    "stargazers_count": 50,
                    "forks_count": 5,
                    "open_issues_count": 0,
                    "created_at": "2026-03-01T00:00:00Z",
                    "html_url": "https://github.com/owner/repo",
                    "topics": [],
                }
            ]
        }
        mock_get.return_value.raise_for_status = MagicMock()

        repos = fetch_github_trending()

        assert len(repos) == 1
        assert repos[0]["description"] == ""
        assert repos[0]["language"] == "Unknown"


class TestFetchHackernewsTop:
    @patch("ingest.time.sleep", return_value=None)
    @patch("ingest.requests.get")
    def test_returns_formatted_stories(
        self, mock_get: MagicMock, mock_sleep: MagicMock
    ) -> None:
        top_stories_response = MagicMock()
        top_stories_response.json.return_value = [101, 102]
        top_stories_response.raise_for_status = MagicMock()

        item_101 = MagicMock()
        item_101.json.return_value = {
            "id": 101,
            "title": "Story One",
            "url": "https://example.com/1",
            "score": 200,
            "by": "alice",
            "descendants": 50,
            "time": 1709856000,
            "type": "story",
        }
        item_101.raise_for_status = MagicMock()

        item_102 = MagicMock()
        item_102.json.return_value = {
            "id": 102,
            "title": "Story Two",
            "url": "https://example.com/2",
            "score": 150,
            "by": "bob",
            "descendants": 30,
            "time": 1709856001,
            "type": "story",
        }
        item_102.raise_for_status = MagicMock()

        mock_get.side_effect = [top_stories_response, item_101, item_102]

        stories = fetch_hackernews_top()

        assert len(stories) == 2
        assert stories[0]["title"] == "Story One"
        assert stories[0]["score"] == 200
        assert stories[0]["author"] == "alice"
        assert stories[1]["title"] == "Story Two"

    @patch("ingest.time.sleep", return_value=None)
    @patch("ingest.requests.get")
    def test_handles_api_errors_gracefully(
        self, mock_get: MagicMock, mock_sleep: MagicMock
    ) -> None:
        top_stories_response = MagicMock()
        top_stories_response.json.return_value = [201, 202]
        top_stories_response.raise_for_status = MagicMock()

        item_201 = MagicMock()
        item_201.json.return_value = {
            "id": 201,
            "title": "Good Story",
            "url": "https://example.com/good",
            "score": 100,
            "by": "carol",
            "descendants": 10,
            "time": 1709856000,
            "type": "story",
        }
        item_201.raise_for_status = MagicMock()

        item_202 = MagicMock()
        item_202.raise_for_status.side_effect = requests.HTTPError("API error")

        mock_get.side_effect = [top_stories_response, item_201, item_202]

        stories = fetch_hackernews_top()

        # Should return the successful story and skip the failed one
        assert len(stories) >= 1
        assert stories[0]["title"] == "Good Story"
