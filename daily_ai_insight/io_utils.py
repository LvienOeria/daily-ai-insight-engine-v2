from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from pydantic import BaseModel

from .config import ensure_parent


def stable_id(prefix: str, *parts: str | None) -> str:
    material = "||".join(part or "" for part in parts)
    digest = hashlib.sha1(material.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def model_dump(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [model_dump(item) for item in value]
    if isinstance(value, dict):
        return {key: model_dump(item) for key, item in value.items()}
    return value


def write_json(path: Path, value: Any) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(model_dump(value), fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_text(path: Path, value: str) -> None:
    ensure_parent(path)
    path.write_text(value, encoding="utf-8")


def read_json_if_exists(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return read_json(path)


def flatten(values: Iterable[Iterable[Any]]) -> list[Any]:
    return [item for group in values for item in group]

