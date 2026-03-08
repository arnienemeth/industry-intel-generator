"""End-to-end pipeline orchestrator for the Industry Intelligence Generator."""

import logging
import sys
from pathlib import Path

# Add src/ to the import path so modules resolve correctly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from utils import setup_logging  # noqa: E402

logger = logging.getLogger(__name__)


def main() -> None:
    """Runs the full ingestion → analysis → dashboard pipeline."""
    setup_logging()
    logger.info("INDUSTRY INTELLIGENCE PIPELINE — FULL RUN")

    # Step 1: Ingestion
    logger.info("Step 1/3: Data ingestion")
    from ingest import run_ingestion  # noqa: E402

    try:
        ingestion_summary = run_ingestion()
    except Exception:
        logger.exception("Ingestion failed")
        sys.exit(1)

    # Step 2: Analysis
    logger.info("Step 2/3: Trend analysis")
    from analyze import run_analysis  # noqa: E402

    try:
        analysis = run_analysis()
    except Exception:
        logger.exception("Analysis failed")
        sys.exit(1)

    # Step 3: Dashboard
    logger.info("Step 3/3: Dashboard generation")
    from dashboard import run_dashboard  # noqa: E402

    dashboard_path = run_dashboard()

    # Summary
    metadata = analysis.get("metadata", {})
    summary = analysis.get("summary", {})
    repos = metadata.get("total_repos_analyzed", 0)
    stories = metadata.get("total_stories_analyzed", 0)
    top_lang = summary.get("dominant_language", "N/A")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Repos analyzed:    {repos}")
    print(f"  Stories analyzed:  {stories}")
    print(f"  Top language:      {top_lang}")
    print(f"  Dashboard:         {dashboard_path}")
    print("=" * 60)
    print("\nNext step: Open Claude Desktop → Cowork → point to data/processed/")


if __name__ == "__main__":
    main()
