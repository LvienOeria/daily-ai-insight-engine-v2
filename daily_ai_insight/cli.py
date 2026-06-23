from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import load_config
from .pipeline import PipelineOptions, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="daily-ai-insight")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run the end-to-end MVP pipeline.")
    run.add_argument(
        "--mock-llm",
        action="store_true",
        help="Use deterministic local fallback instead of DeepSeek LLM calls.",
    )
    run.add_argument(
        "--sources",
        type=Path,
        default=None,
        help="Path to source configuration JSON. Defaults to config/sources.json.",
    )
    run.add_argument(
        "--max-fetch-items",
        type=int,
        default=None,
        help="Cap fetched items per source for development.",
    )

    subparsers.add_parser("config", help="Print effective runtime configuration.")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_config()

    if args.command == "config":
        payload = {
            "report": {
                "timezone": config.report.timezone,
                "window_days": config.report.window_days,
                "min_items": config.report.min_items,
                "max_items": config.report.max_items,
            },
            "llm": {
                "provider": config.llm.provider,
                "base_url": config.llm.base_url,
                "default_model": config.llm.default_model,
                "report_model": config.llm.report_model,
                "has_api_key": bool(config.llm.api_key),
            },
            "frontend_data_output": str(config.frontend_data_output),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if args.command == "run":
        result = run_pipeline(
            config=config,
            options=PipelineOptions(
                mock_llm=args.mock_llm,
                sources_path=args.sources,
                max_fetch_items=args.max_fetch_items,
            ),
        )
        print(f"report: {result.report_path}")
        print(f"frontend data: {result.frontend_data_path}")
        print(f"quality passed: {result.quality_passed}")
        if not result.quality_passed:
            sys.exit(2)

