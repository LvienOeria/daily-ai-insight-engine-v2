"""Load skill prompts from the skills/ directory.

Usage:
    from .skill_loader import load_prompt
    system_prompt = load_prompt("news-structuring")
"""

from __future__ import annotations

from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[1] / "skills"


def load_prompt(skill_name: str) -> str:
    """Load the system prompt for a skill.

    Reads <skill_name>/prompt.txt from the skills directory.
    Falls back to SKILL.md if prompt.txt is absent (for documentation-only skills).
    """
    prompt_path = SKILLS_DIR / skill_name / "prompt.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()

    # Fallback: skills without prompt.txt are programmatic (no LLM call)
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if skill_path.exists():
        raise FileNotFoundError(
            f"Skill '{skill_name}' has no prompt.txt (programmatic skill, no LLM call needed)"
        )
    raise FileNotFoundError(f"Skill '{skill_name}' not found in {SKILLS_DIR}")
