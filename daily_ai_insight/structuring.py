from __future__ import annotations

import json
import re

from .llm import DeepSeekClient
from .models import CleanedNewsItem, StructuredNewsItem


EVENT_TYPES = [
    "product_release",
    "model_release",
    "funding",
    "acquisition",
    "partnership",
    "regulation",
    "research",
    "open_source",
    "infrastructure",
    "security_risk",
    "business_update",
    "market_commentary",
    "other",
]

INDUSTRY_AREAS = [
    "foundation_model",
    "ai_agent",
    "multimodal_ai",
    "ai_infrastructure",
    "chip_compute",
    "enterprise_ai",
    "consumer_ai",
    "developer_tools",
    "ai_safety",
    "policy_regulation",
    "research",
    "capital_market",
    "other",
]


def structure_news_items(
    cleaned: list[CleanedNewsItem],
    *,
    llm: DeepSeekClient | None,
    mock_llm: bool = False,
    batch_size: int = 5,
) -> list[StructuredNewsItem]:
    if mock_llm or llm is None:
        return [_mock_structure(item) for item in cleaned]

    structured: list[StructuredNewsItem] = []
    for start in range(0, len(cleaned), batch_size):
        batch = cleaned[start : start + batch_size]
        payload = {
            "items": [
                item.model_dump(
                    mode="json",
                    include={
                        "news_id",
                        "title",
                        "source",
                        "source_type",
                        "published_at",
                        "language",
                        "url",
                        "summary",
                        "content",
                    },
                )
                for item in batch
            ]
        }
        response = llm.complete_json(
            system=_STRUCTURING_SYSTEM,
            user=json.dumps(payload, ensure_ascii=False),
        )
        records = response.get("items")
        if not isinstance(records, list):
            raise ValueError("structuring LLM output must contain items list")
        for record in records:
            structured.append(StructuredNewsItem.model_validate(record))
    return structured


_STRUCTURING_SYSTEM = f"""
You are the news-structuring module for the Daily AI Insight Engine.
Return valid JSON only: {{"items": [StructuredNewsItem, ...]}}.
Use only the input item text. Do not invent companies, dates, URLs, funding amounts,
policy details, technical releases, or external facts.

Required output fields per item:
news_id, title, source, source_type, published_at, language, url, entities,
technologies, event_type, industry_area, key_facts, summary, sentiment,
impact_scope, risk_tags, opportunity_tags, importance_score, confidence, evidence.

event_type enum: {EVENT_TYPES}
industry_area enum: {INDUSTRY_AREAS}
sentiment enum: positive, neutral, negative, mixed
confidence enum: low, medium, high
importance_score: integer 1-5 for single-news importance only.

If information is missing, use [], null, "other", or low confidence as appropriate.
Evidence should quote or tightly paraphrase fragments visible in the input.
"""


def _mock_structure(item: CleanedNewsItem) -> StructuredNewsItem:
    text = f"{item.title} {item.summary}".lower()
    event_type = _infer_event_type(text)
    industry_area = _infer_industry_area(text)
    technologies = _infer_technologies(text)
    entities = _infer_entities(item.title + " " + item.summary)
    facts = [_short_fact(item.summary)]
    risk_tags = _infer_risks(text)
    opportunity_tags = _infer_opportunities(text)
    score = 2
    if item.source_type in {"official", "research"}:
        score += 1
    if event_type in {"model_release", "regulation", "funding", "security_risk"}:
        score += 1
    if risk_tags or opportunity_tags:
        score += 1
    score = min(5, max(1, score))

    return StructuredNewsItem(
        news_id=item.news_id,
        title=item.title,
        source=item.source,
        source_type=item.source_type,
        published_at=item.published_at,
        language=item.language,
        url=item.url,
        entities=entities,
        technologies=technologies,
        event_type=event_type,  # type: ignore[arg-type]
        industry_area=industry_area,  # type: ignore[arg-type]
        key_facts=facts,
        summary=item.summary[:500],
        sentiment="neutral",
        impact_scope=["developers"] if item.source_type in {"research", "community"} else ["industry"],
        risk_tags=risk_tags or ["none"],
        opportunity_tags=opportunity_tags or ["none"],
        importance_score=score,
        confidence="medium" if len(item.summary) >= 120 else "low",
        evidence=facts,
    )


def _infer_event_type(text: str) -> str:
    if any(word in text for word in ["release", "launch", "推出", "发布", "model", "模型"]):
        return "model_release"
    if any(word in text for word in ["funding", "raises", "融资", "估值"]):
        return "funding"
    if any(word in text for word in ["regulation", "policy", "监管", "政策", "法案"]):
        return "regulation"
    if any(word in text for word in ["paper", "arxiv", "research", "研究", "论文"]):
        return "research"
    if any(word in text for word in ["open source", "github", "开源"]):
        return "open_source"
    if any(word in text for word in ["security", "risk", "漏洞", "安全"]):
        return "security_risk"
    if any(word in text for word in ["partnership", "合作"]):
        return "partnership"
    return "other"


def _infer_industry_area(text: str) -> str:
    if any(word in text for word in ["agent", "agents", "智能体"]):
        return "ai_agent"
    if any(word in text for word in ["multimodal", "image", "video", "audio", "多模态", "视频"]):
        return "multimodal_ai"
    if any(word in text for word in ["gpu", "chip", "compute", "inference", "芯片", "算力"]):
        return "chip_compute"
    if any(word in text for word in ["enterprise", "企业"]):
        return "enterprise_ai"
    if any(word in text for word in ["safety", "alignment", "安全", "对齐"]):
        return "ai_safety"
    if any(word in text for word in ["policy", "regulation", "监管", "政策"]):
        return "policy_regulation"
    if any(word in text for word in ["research", "paper", "arxiv", "研究", "论文"]):
        return "research"
    if any(word in text for word in ["model", "llm", "gpt", "大模型"]):
        return "foundation_model"
    return "other"


def _infer_technologies(text: str) -> list[str]:
    candidates = {
        "LLM": ["llm", "large language model", "大语言模型", "大模型"],
        "AI agent": ["agent", "智能体"],
        "multimodal AI": ["multimodal", "多模态"],
        "inference": ["inference", "推理"],
        "GPU": ["gpu", "芯片", "算力"],
        "RAG": ["rag", "retrieval"],
    }
    return [name for name, words in candidates.items() if any(word in text for word in words)]


def _infer_entities(text: str) -> list[str]:
    known = [
        "OpenAI",
        "Anthropic",
        "Google",
        "DeepMind",
        "Microsoft",
        "Meta",
        "NVIDIA",
        "DeepSeek",
        "xAI",
        "Apple",
        "Amazon",
        "Mistral",
        "Hugging Face",
    ]
    found = [name for name in known if name.lower() in text.lower()]
    chinese = re.findall(r"(?:OpenAI|DeepSeek|机器之心|量子位|知乎|英伟达|谷歌|微软|阿里|腾讯|字节)", text)
    return sorted(set(found + chinese))


def _short_fact(summary: str) -> str:
    parts = re.split(r"(?<=[.!?。！？])\s+", summary)
    return (parts[0] if parts else summary)[:240]


def _infer_risks(text: str) -> list[str]:
    risks = []
    if any(word in text for word in ["privacy", "隐私"]):
        risks.append("privacy")
    if any(word in text for word in ["copyright", "版权"]):
        risks.append("copyright")
    if any(word in text for word in ["security", "安全", "漏洞"]):
        risks.append("security")
    if any(word in text for word in ["regulation", "compliance", "监管", "合规"]):
        risks.append("compliance")
    return risks


def _infer_opportunities(text: str) -> list[str]:
    opportunities = []
    if any(word in text for word in ["productivity", "效率", "生产力"]):
        opportunities.append("productivity")
    if any(word in text for word in ["enterprise", "企业"]):
        opportunities.append("enterprise_adoption")
    if any(word in text for word in ["developer", "github", "开发者"]):
        opportunities.append("developer_ecosystem")
    if any(word in text for word in ["infrastructure", "gpu", "compute", "基础设施", "算力"]):
        opportunities.append("infrastructure_growth")
    if any(word in text for word in ["open source", "开源"]):
        opportunities.append("open_source_growth")
    return opportunities
