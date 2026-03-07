"""Shared utility functions for the industry intel generator."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DATA_RAW: Path = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED: Path = PROJECT_ROOT / "data" / "processed"

DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


def get_timestamp() -> str:
    """Returns the current UTC date as an ISO 8601 string.

    Returns:
        Current date in "YYYY-MM-DD" format.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def save_json(data: Any, filepath: Path) -> None:
    """Saves data as formatted JSON to the given filepath.

    Creates parent directories if they don't exist.

    Args:
        data: The data to serialize as JSON.
        filepath: Destination path for the JSON file.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Saved JSON to %s", filepath)


def load_json(filepath: Path) -> Any:
    """Loads and returns parsed JSON from the given filepath.

    Args:
        filepath: Path to the JSON file.

    Returns:
        The parsed JSON data.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    return json.loads(filepath.read_text(encoding="utf-8"))


def setup_logging(level: int = logging.INFO) -> None:
    """Configures root logging with a standard format.

    Args:
        level: The logging level (e.g. logging.DEBUG, logging.INFO).
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )


def get_latest_file(
    directory: Path, prefix: str, suffix: str = ".json"
) -> Path | None:
    """Finds the most recent file in a directory by name sorting.

    Matches files that start with the given prefix and end with the given
    suffix, then returns the last one in sorted order (newest by ISO 8601
    date convention).

    Args:
        directory: The directory to search in.
        prefix: The filename prefix to filter by.
        suffix: The filename suffix to filter by.

    Returns:
        Path to the most recent matching file, or None if no match.
    """
    matches = sorted(directory.glob(f"{prefix}*{suffix}"))
    return matches[-1] if matches else None


def calculate_growth_rate(current: float, previous: float) -> float:
    """Calculates the decimal growth rate between two values.

    Args:
        current: The current value.
        previous: The previous value.

    Returns:
        The growth rate as a decimal (e.g. 0.25 for 25% growth).
        Returns 0.0 if previous is zero.
    """
    if previous == 0:
        return 0.0
    return (current - previous) / previous
