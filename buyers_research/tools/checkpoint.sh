#!/usr/bin/env bash
# Auto-checkpoint for the NJ buyer research run.
# Every INTERVAL seconds: copy the workflow scripts + agent journals into the repo, snapshot part-file
# row counts, and commit + push anything new under buyers_research/ so progress survives a credit lapse.
# Usage: bash buyers_research/tools/checkpoint.sh [interval_seconds]
REPO=/home/user/cladue
BRANCH=claude/nj-industrial-buyer-research-v4j2sy
SESS=/root/.claude/projects/-home-user-cladue/11d13300-138f-51de-822b-f9fea5fa0346
WFDIR="$SESS/subagents/workflows"
SCRIPTS="$SESS/workflows/scripts"
INTERVAL="${1:-600}"

while true; do
  sleep "$INTERVAL"
  cd "$REPO" || exit 1
  mkdir -p buyers_research/parts/_runs buyers_research/tools/workflows
  cp -f "$SCRIPTS"/*.js buyers_research/tools/workflows/ 2>/dev/null
  for d in "$WFDIR"/wf_*; do
    [ -d "$d" ] || continue
    rid=$(basename "$d")
    mkdir -p "buyers_research/parts/_runs/$rid"
    [ -f "$d/journal.jsonl" ] && cp -f "$d/journal.jsonl" "buyers_research/parts/_runs/$rid/journal.jsonl"
  done
  {
    echo "# checkpoint $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "# part file -> rows written so far"
    for f in buyers_research/parts/*/*.jsonl; do
      [ -f "$f" ] && echo "$f $(wc -l < "$f")"
    done
  } > buyers_research/parts/_runs/STATUS.txt
  git add -A buyers_research >/dev/null 2>&1
  if ! git diff --cached --quiet 2>/dev/null; then
    git commit -q -m "checkpoint: research parts $(date -u +%Y-%m-%dT%H:%MZ)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_0126gXTSDEH4CeHTDhskFo5J" || true
    for i in 1 2 3 4; do
      git push -q -u origin "$BRANCH" 2>/dev/null && break
      sleep $((2 ** i))
    done
  fi
done
