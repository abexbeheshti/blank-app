#!/usr/bin/env python
"""CLI entrypoint for the meeting-to-code pipeline.

Usage:
    python scripts/run_pipeline.py --once          # single pass, for cron/Cloud Functions
    python scripts/run_pipeline.py                 # loop forever, polling on an interval
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.config import load_config
from pipeline.runner import run_once

Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/pipeline.log")],
)
logger = logging.getLogger("pipeline.cli")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="Run a single pass and exit")
    args = parser.parse_args()

    config = load_config()

    if args.once:
        summary = run_once(config)
        logger.info("Run summary: %s", summary)
        return

    logger.info("Starting polling loop (interval=%ss)", config.polling_interval_seconds)
    while True:
        summary = run_once(config)
        if summary["new_transcripts"] or summary["advanced"] or summary["errors"]:
            logger.info("Run summary: %s", summary)
        time.sleep(config.polling_interval_seconds)


if __name__ == "__main__":
    main()
