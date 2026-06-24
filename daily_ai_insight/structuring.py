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
        source_by_id = {item.news_id: item for item in batch}
        for record in records:
            structured.append(
                StructuredNewsItem.model_validate(
                    _normalize_structured_record(record, source_by_id)
                )
            )
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
    is_research = item.source_type == "research" or "arxiv" in item.source.lower()

    event_type = _infer_event_type(text, is_research=is_research)
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
    if risk_tags and risk_tags != ["none"]:
        score += 1
    if opportunity_tags and opportunity_tags != ["none"]:
        score += 1
    if item.source_type == "official":
        score = max(score, 3)
    score = min(5, max(1, score))

    # Impact scope depends on source and event type
    if item.source_type == "official":
        impact_scope = ["industry"]
    elif is_research:
        impact_scope = ["research"]
    elif item.source_type == "community":
        impact_scope = ["developers"]
    else:
        impact_scope = ["industry"]

    # Confidence: research papers with clear abstracts get higher confidence
    if is_research and len(item.summary) >= 200:
        confidence = "high"
    elif len(item.summary) >= 120:
        confidence = "medium"
    else:
        confidence = "low"

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
        impact_scope=impact_scope,
        risk_tags=risk_tags or ["none"],
        opportunity_tags=opportunity_tags or ["none"],
        importance_score=score,
        confidence=confidence,  # type: ignore[arg-type]
        evidence=facts,
    )


def _normalize_structured_record(
    record: dict,
    source_by_id: dict[str, CleanedNewsItem],
) -> dict:
    news_id = record.get("news_id")
    source = source_by_id.get(news_id)

    if source:
        for field in [
            "news_id",
            "title",
            "source",
            "source_type",
            "published_at",
            "language",
            "url",
        ]:
            record.setdefault(field, getattr(source, field))

    for field in [
        "entities",
        "technologies",
        "key_facts",
        "impact_scope",
        "risk_tags",
        "opportunity_tags",
        "evidence",
    ]:
        record[field] = _as_list(record.get(field))

    if record.get("event_type") not in EVENT_TYPES:
        record["event_type"] = "other"
    if record.get("industry_area") not in INDUSTRY_AREAS:
        record["industry_area"] = "other"
    if record.get("sentiment") not in {"positive", "neutral", "negative", "mixed"}:
        record["sentiment"] = "neutral"
    if record.get("confidence") not in {"low", "medium", "high"}:
        record["confidence"] = "medium"

    try:
        score = int(record.get("importance_score", 1))
    except (TypeError, ValueError):
        score = 1
    record["importance_score"] = min(5, max(1, score))

    if not record.get("summary") and source:
        record["summary"] = source.summary
    if not record.get("key_facts") and record.get("summary"):
        record["key_facts"] = [_short_fact(record["summary"])]
    if not record.get("evidence"):
        record["evidence"] = record.get("key_facts", [])
    if not record.get("risk_tags"):
        record["risk_tags"] = ["none"]
    if not record.get("opportunity_tags"):
        record["opportunity_tags"] = ["none"]

    return record


def _as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    return [str(value)]


def _infer_event_type(text: str, *, is_research: bool = False) -> str:
    # Research papers: default to "research" unless there's strong signal otherwise
    if is_research:
        if any(word in text for word in ["release", "launch", "推出", "发布"]):
            if any(word in text for word in ["gpt-", "claude", "gemini", "llama", "model card"]):
                return "model_release"
        if any(word in text for word in ["funding", "raises", "融资", "估值"]):
            return "funding"
        if any(word in text for word in ["regulation", "policy", "监管", "政策", "法案"]):
            return "regulation"
        if any(word in text for word in ["security", "risk", "漏洞", "adversarial", "attack"]):
            return "security_risk"
        if any(word in text for word in ["open source", "github", "开源"]):
            return "open_source"
        if any(word in text for word in ["benchmark", "dataset", "corpus"]):
            return "research"
        return "research"

    if any(word in text for word in ["release", "launch", "推出", "发布"]):
        if any(word in text for word in ["model", "模型", "gpt", "claude", "gemini", "llama"]):
            return "model_release"
        return "product_release"
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
    if any(word in text for word in ["multimodal", "image", "video", "audio", "多模态", "视频", "vision"]):
        return "multimodal_ai"
    if any(word in text for word in ["gpu", "chip", "compute", "inference", "芯片", "算力", "hardware"]):
        return "chip_compute"
    if any(word in text for word in ["enterprise", "企业"]):
        return "enterprise_ai"
    if any(word in text for word in ["safety", "alignment", "安全", "对齐", "adversarial", "jailbreak"]):
        return "ai_safety"
    if any(word in text for word in ["policy", "regulation", "监管", "政策"]):
        return "policy_regulation"
    if any(word in text for word in ["benchmark", "dataset", "training", "optimizer", "transformer",
                                     "attention", "fine-tun", "pretrain", "pre-train", "arxiv"]):
        return "research"
    if any(word in text for word in ["model", "llm", "gpt", "大模型", "language model"]):
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
    # Company/institution entities - only match when capitalized in original text
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
        "Intel",
        "AMD",
        "Tesla",
        "Stability AI",
        "Cohere",
    ]
    # Only match if the entity name appears as a capitalized proper noun in the original
    found = []
    for name in known:
        # Use word-boundary matching to avoid "Perplexity" matching "perplexity"
        pattern = re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE)
        if pattern.search(text):
            # Check if the match is capitalized (proper noun) in the original
            original_match = pattern.search(text)
            if original_match:
                matched_text = original_match.group(0)
                # Accept if starts with uppercase (proper noun), or is a known acronym
                if matched_text[0].isupper() or name in {"NVIDIA", "AMD", "xAI"}:
                    found.append(name)

    chinese = re.findall(
        r"(?:OpenAI|DeepSeek|机器之心|量子位|知乎|英伟达|谷歌|微软|阿里|腾讯|字节|百度|华为|商汤|科大讯飞)",
        text,
    )
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
