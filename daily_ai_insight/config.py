from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    api_key: str | None
    base_url: str
    default_model: str
    report_model: str
    temperature: float
    max_output_tokens: int


@dataclass(frozen=True)
class ReportConfig:
    timezone: str
    window_days: int
    min_items: int
    max_items: int
    max_items_per_source: int = 6


@dataclass(frozen=True)
class AppConfig:
    root: Path
    defaults: dict[str, Any]
    report: ReportConfig
    llm: LLMConfig
    output_paths: dict[str, Path]
    frontend_data_output: Path

    def path(self, key: str) -> Path:
        return self.output_paths[key]


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return int(raw)


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return float(raw)


def load_config(root: Path | None = None) -> AppConfig:
    root = root or PROJECT_ROOT
    load_dotenv(root / ".env")

    defaults = _read_json(root / "config" / "defaults.json")
    report_defaults = defaults["report"]
    llm_defaults = defaults["llm"]

    report = ReportConfig(
        timezone=os.getenv("REPORT_TIMEZONE", report_defaults["timezone"]),
        window_days=_env_int("REPORT_WINDOW_DAYS", report_defaults["window_days"]),
        min_items=_env_int("REPORT_MIN_ITEMS", report_defaults["min_items"]),
        max_items=_env_int("REPORT_MAX_ITEMS", report_defaults["max_items"]),
        max_items_per_source=_env_int("REPORT_MAX_ITEMS_PER_SOURCE", report_defaults.get("max_items_per_source", 6)),
    )

    api_key_env = llm_defaults.get("api_key_env", "DEEPSEEK_API_KEY")
    llm = LLMConfig(
        provider=os.getenv("LLM_PROVIDER", llm_defaults["provider"]),
        api_key=os.getenv(api_key_env),
        base_url=os.getenv("DEEPSEEK_BASE_URL", llm_defaults["base_url"]),
        default_model=os.getenv("DEEPSEEK_MODEL", llm_defaults["default_model"]),
        report_model=os.getenv("DEEPSEEK_REPORT_MODEL", llm_defaults["report_model"]),
        temperature=_env_float("LLM_TEMPERATURE", llm_defaults["temperature"]),
        max_output_tokens=_env_int("LLM_MAX_OUTPUT_TOKENS", llm_defaults["max_output_tokens"]),
    )

    output_paths = {
        key: root / value for key, value in defaults.get("output_paths", {}).items()
    }
    frontend_data_output = root / os.getenv(
        "FRONTEND_DATA_OUTPUT", defaults["frontend"]["data_output"]
    )

    return AppConfig(
        root=root,
        defaults=defaults,
        report=report,
        llm=llm,
        output_paths=output_paths,
        frontend_data_output=frontend_data_output,
    )


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

