from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .cleaning import clean_news_items
from .clustering import cluster_events
from .config import AppConfig, load_config
from .fetchers import fetch_candidate, load_candidates
from .io_utils import write_json, write_text
from .llm import DeepSeekClient
from .models import PipelineManifest, RawNewsItem, utc_now_iso
from .quality import run_quality_check
from .reporting import generate_report
from .scoring import score_events
from .source_evaluation import evaluate_source
from .structuring import structure_news_items
from .visualization import build_visualization_data


@dataclass(frozen=True)
class PipelineOptions:
    mock_llm: bool = False
    sources_path: Path | None = None
    max_fetch_items: int | None = None


@dataclass(frozen=True)
class PipelineResult:
    manifest: PipelineManifest
    quality_passed: bool
    report_path: Path
    frontend_data_path: Path


def run_pipeline(
    *,
    config: AppConfig | None = None,
    options: PipelineOptions | None = None,
) -> PipelineResult:
    config = config or load_config()
    options = options or PipelineOptions()
    sources_path = options.sources_path or config.root / "config" / "sources.json"

    candidates = load_candidates(sources_path)
    fetch_results = [fetch_candidate(candidate, config) for candidate in candidates]

    raw_items: list[RawNewsItem] = []
    source_profiles = []
    for result in fetch_results:
        items = result.items
        if options.max_fetch_items is not None:
            items = items[: options.max_fetch_items]
        raw_items.extend(items)
        source_profiles.append(evaluate_source(result.candidate, items, result.error))

    write_json(config.path("source_evaluation"), source_profiles)
    write_json(config.path("raw_news"), raw_items)

    cleaned = clean_news_items(
        raw_items,
        timezone=config.report.timezone,
        window_days=config.report.window_days,
    )
    cleaned = cleaned[: config.report.max_items]
    write_json(config.path("cleaned_news"), cleaned)

    llm = None if options.mock_llm else DeepSeekClient(config.llm)

    structured = structure_news_items(cleaned, llm=llm, mock_llm=options.mock_llm)
    write_json(config.path("structured_news"), structured)

    events = cluster_events(structured, llm=llm, mock_llm=options.mock_llm)
    write_json(config.path("clustered_events"), {"events": events})

    ranked_events = score_events(events, structured)
    write_json(config.path("importance_scores"), {"ranked_events": ranked_events})

    visualization_data = build_visualization_data(structured, events, ranked_events)
    write_json(config.path("visualization_data"), visualization_data)

    report_markdown = generate_report(
        structured=structured,
        events=events,
        ranked_events=ranked_events,
        source_profiles=source_profiles,
        visualization_data=visualization_data,
        llm=llm,
        mock_llm=options.mock_llm,
    )
    write_text(config.path("report"), report_markdown)

    quality = run_quality_check(
        cleaned=cleaned,
        structured=structured,
        events=events,
        ranked_events=ranked_events,
        source_profiles=source_profiles,
        visualization_data=visualization_data,
        report_markdown=report_markdown,
        min_items=config.report.min_items,
        max_items=config.report.max_items,
    )
    write_json(config.path("quality_check"), quality)

    frontend_payload = {
        "generated_at": utc_now_iso(),
        "report": {
            "timezone": config.report.timezone,
            "window_days": config.report.window_days,
            "markdown": report_markdown,
        },
        "source_profiles": source_profiles,
        "structured_news": structured,
        "events": events,
        "ranked_events": ranked_events,
        "visualization_data": visualization_data,
        "quality_check": quality,
    }
    write_json(config.frontend_data_output, frontend_payload)

    manifest = PipelineManifest(
        generated_at=utc_now_iso(),
        report_timezone=config.report.timezone,
        report_window_days=config.report.window_days,
        source_profiles=source_profiles,
        raw_count=len(raw_items),
        cleaned_count=len(cleaned),
        structured_count=len(structured),
        event_count=len(events),
        ranked_event_count=len(ranked_events),
        notes=[
            "DeepSeek websearch observations are consumed only from the allowlisted observation file.",
            "React frontend is display-only and reads frontend/public/data/latest.json.",
        ],
    )

    return PipelineResult(
        manifest=manifest,
        quality_passed=quality.passed,
        report_path=config.path("report"),
        frontend_data_path=config.frontend_data_output,
    )

