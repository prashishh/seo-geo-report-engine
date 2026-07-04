#!/usr/bin/env bash
# Health check for the seo-geo-report-engine framework. Run: bash scripts/doctor.sh
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
echo "== seo-geo-report-engine doctor =="
echo "- root: $ROOT"
echo
echo "== runtime + tools =="
./bin/mkt selftest || echo "  (selftest reported an issue above)"
echo
echo "== inventory =="
printf "  skills:   %s\n" "$(find skills -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')"
printf "  commands: %s\n" "$(find commands -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
printf "  agents:   %s\n" "$(find agents -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
printf "  playbooks:%s\n" "$(find playbooks -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
printf "  projects: %s\n" "$(find projects -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
echo
echo "== config =="
[ -f config/secrets.env ] && echo "  secrets.env: present" || echo "  secrets.env: MISSING (cp config/secrets.example.env config/secrets.env) — Ahrefs MCP needs no key"
echo
echo "== plugin wiring =="
for d in skills commands agents; do
  if [ -L ".claude/$d" ]; then echo "  .claude/$d -> $(readlink ".claude/$d")"; else echo "  .claude/$d: NOT a symlink"; fi
done
echo "done."
