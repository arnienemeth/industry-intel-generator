"""Tests for src/utils.py utility functions."""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import (
    calculate_growth_rate,
    get_latest_file,
    get_timestamp,
    load_json,
    save_json,
)


class TestGetTimestamp:
    def test_returns_10_char_string(self) -> None:
        ts = get_timestamp()
        assert isinstance(ts, str)
        assert len(ts) == 10

    def test_matches_iso_format(self) -> None:
        ts = get_timestamp()
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", ts)


class TestSaveAndLoadJson:
    def test_roundtrip(self, tmp_path: Path) -> None:
        data = {"key": "value", "numbers": [1, 2, 3]}
        filepath = tmp_path / "test.json"
        save_json(data, filepath)
        loaded = load_json(filepath)
        assert loaded == data

    def test_save_creates_parent_directories(self, tmp_path: Path) -> None:
        filepath = tmp_path / "nested" / "deep" / "file.json"
        save_json({"a": 1}, filepath)
        assert filepath.exists()
        assert load_json(filepath) == {"a": 1}

    def test_load_raises_on_missing_file(self, tmp_path: Path) -> None:
        import pytest

        with pytest.raises(FileNotFoundError):
            load_json(tmp_path / "nonexistent.json")


class TestCalculateGrowthRate:
    def test_positive_growth(self) -> None:
        assert calculate_growth_rate(150, 100) == 0.5

    def test_negative_growth(self) -> None:
        assert calculate_growth_rate(80, 100) == -0.2

    def test_zero_previous_returns_zero(self) -> None:
        assert calculate_growth_rate(100, 0) == 0.0

    def test_no_change_returns_zero(self) -> None:
        assert calculate_growth_rate(100, 100) == 0.0


class TestGetLatestFile:
    def test_finds_newest_file(self, tmp_path: Path) -> None:
        (tmp_path / "github_2026-03-01.json").write_text("{}")
        (tmp_path / "github_2026-03-05.json").write_text("{}")
        (tmp_path / "github_2026-03-03.json").write_text("{}")

        result = get_latest_file(tmp_path, "github_")
        assert result is not None
        assert result.name == "github_2026-03-05.json"

    def test_returns_none_when_no_match(self, tmp_path: Path) -> None:
        (tmp_path / "other_2026-03-01.json").write_text("{}")
        result = get_latest_file(tmp_path, "github_")
        assert result is None
