#!/usr/bin/env python3
"""Static validation of the framework: frontmatter, cross-references, inventory.
Run: ./bin/mkt  ... no — run directly:  python3.12 scripts/validate.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lib import yaml_min  # noqa: E402

problems = []
warnings = []


def frontmatter(p):
    t = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        return None, t
    return yaml_min.safe_load(m.group(1)), t[m.end():]


def check_skill(p):
    fm, body = frontmatter(p)
    rel = p.relative_to(ROOT)
    if fm is None:
        problems.append(f"{rel}: no YAML frontmatter")
        return
    if not fm.get("description"):
        problems.append(f"{rel}: missing description")
    if not fm.get("allowed-tools"):
        warnings.append(f"{rel}: no allowed-tools")
    if not isinstance(fm.get("metadata"), dict):
        warnings.append(f"{rel}: no metadata block")
    desc = (str(fm.get("description", "")) + str(fm.get("when_to_use", "")))
    if len(desc) > 1536:
        problems.append(f"{rel}: description too long ({len(desc)} > 1536)")
    if len(body.strip()) < 200:
        warnings.append(f"{rel}: body very short")


def check_cmd(p):
    fm, _ = frontmatter(p)
    rel = p.relative_to(ROOT)
    if fm is None:
        problems.append(f"{rel}: no frontmatter")
    elif not fm.get("description"):
        problems.append(f"{rel}: missing description")


def check_agent(p):
    fm, _ = frontmatter(p)
    rel = p.relative_to(ROOT)
    if fm is None:
        problems.append(f"{rel}: no frontmatter")
        return
    if not fm.get("name"):
        warnings.append(f"{rel}: missing name")
    if not fm.get("description"):
        problems.append(f"{rel}: missing description")


skills = sorted(ROOT.glob("skills/*/SKILL.md"))
cmds = sorted(ROOT.glob("commands/*.md"))
agents = sorted(ROOT.glob("agents/*.md"))
playbooks = sorted(ROOT.glob("playbooks/*.md"))
knowledge = sorted(ROOT.glob("knowledge/*.md"))

for p in skills:
    check_skill(p)
for p in cmds:
    check_cmd(p)
for p in agents:
    check_agent(p)

# cross-reference: every playbook referenced by a skill should exist
existing_playbooks = {p.name for p in playbooks}
for p in skills + cmds:
    for ref in re.findall(r"playbooks/([a-z0-9-]+\.md)", p.read_text(encoding="utf-8")):
        if ref not in existing_playbooks:
            problems.append(f"{p.relative_to(ROOT)}: references missing playbooks/{ref}")

# empty skill dirs (scaffolded but no SKILL.md)
for d in sorted(ROOT.glob("skills/*")):
    if d.is_dir() and not (d / "SKILL.md").exists():
        problems.append(f"skills/{d.name}/: empty (no SKILL.md)")

print("=== inventory ===")
print(f"  skills:    {len(skills)}")
print(f"  commands:  {len(cmds)}")
print(f"  agents:    {len(agents)}")
print(f"  playbooks: {len(playbooks)}  -> {sorted(existing_playbooks)}")
print(f"  knowledge: {len(knowledge)}  -> {[k.name for k in knowledge]}")
print()
print(f"=== {len(problems)} problems, {len(warnings)} warnings ===")
for x in problems:
    print("  PROBLEM:", x)
for x in warnings:
    print("  warn:   ", x)
sys.exit(1 if problems else 0)
