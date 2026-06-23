from __future__ import annotations

import json

from daily_ai_insight.config import load_config
from daily_ai_insight.pipeline import PipelineOptions, run_pipeline


def test_mock_pipeline_generates_artifacts() -> None:
    config = load_config()
    result = run_pipeline(config=config, options=PipelineOptions(mock_llm=True))

    assert result.report_path.exists()
    assert result.frontend_data_path.exists()

    frontend = json.loads(result.frontend_data_path.read_text(encoding="utf-8"))
    assert 10 <= len(frontend["structured_news"]) <= 20
    assert len(frontend["events"]) == len(frontend["structured_news"])
    assert frontend["visualization_data"]["top_event_scores"]
    assert "今日概览" in frontend["report"]["markdown"]

