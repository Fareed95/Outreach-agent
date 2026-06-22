"""
main.py
-------
Entry point for Syntrase.
Called by cron or manually.

Usage:
  uv run main.py --mode outreach --niche "CA firms" --location "Mumbai"
  uv run main.py --mode feedback
"""

import asyncio
import argparse
from utils.logger import logger
from config.settings import settings


async def run_outreach(niche: str, location: str) -> None:
    """Run full outreach pipeline."""
    logger.info(f"Starting outreach pipeline | niche={niche} | location={location}")
    # TODO: import and invoke core pipeline
    pass


async def run_feedback() -> None:
    """Run feedback/learning pipeline."""
    logger.info("Starting feedback pipeline")
    # TODO: import and invoke feedback pipeline
    pass


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Syntrase")
    parser.add_argument("--mode", choices=["outreach", "feedback"], required=True)
    parser.add_argument("--niche", type=str, default=settings.DEFAULT_NICHE)
    parser.add_argument("--location", type=str, default=settings.DEFAULT_LOCATION)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.mode == "outreach":
        asyncio.run(run_outreach(args.niche, args.location))
    elif args.mode == "feedback":
        asyncio.run(run_feedback())