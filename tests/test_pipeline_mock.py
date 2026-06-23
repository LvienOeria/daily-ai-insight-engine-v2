from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from daily_ai_insight.config import load_config
from daily_ai_insight.pipeline import PipelineOptions, run_pipeline


def test_mock_pipeline_generates_artifacts(tmp_path: Path) -> None:
    config = load_config()
    output_paths = {
        key: tmp_path / path.name
        for key, path in config.output_paths.items()
    }
    test_config = replace(
        config,
        output_paths=output_paths,
        frontend_data_output=tmp_path / "frontend" / "latest.json",
    )

    result = run_pipeline(config=test_config, options=PipelineOptions(mock_llm=True))

    assert result.report_path.exists()
    assert result.frontend_data_path.exists()

    frontend = json.loads(result.frontend_data_path.read_text(encoding="utf-8"))
    assert 10 <= len(frontend["structured_news"]) <= 20
    assert len(frontend["events"]) == len(frontend["structured_news"])
    assert frontend["visualization_data"]["top_event_scores"]
    assert "今日概览" in frontend["report"]["markdown"]
