"""The Python skill tagger must give the answers in tests/skill_cases.json.

The website runs the same cases (frontend/src/skills.test.mjs), so both copies agree.
"""

import json
from pathlib import Path

import pytest

from pipeline.tag.skills import SKILLS, find_skills

CASES = json.loads((Path(__file__).parent / "skill_cases.json").read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize("case", CASES, ids=[c["text"][:40] for c in CASES])
def test_shared_cases(case):
    assert sorted(find_skills(case["text"])) == case["skills"]


def test_skill_names_are_unique():
    names = [s[0] for s in SKILLS]
    assert len(names) == len(set(names))


def test_python_and_website_track_the_same_skills():
    js = (Path(__file__).parent.parent / "frontend" / "src" / "skills.js").read_text(encoding="utf-8")
    missing = [name for name, *_ in SKILLS if f"'{name}'" not in js and f'"{name}"' not in js]
    assert missing == [], f"In the Python list but not the website list: {missing}"
