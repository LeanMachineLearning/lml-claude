#!/usr/bin/env bash
# Session-start check of the tools the lml skills rely on. It prints nothing when everything is
# there. Otherwise it prints one JSON object for Claude Code: the missing tools, as context for
# the model and as a short message for the user. It never fails the session.
missing=()
command -v git >/dev/null 2>&1 || missing+=("git")
command -v uv >/dev/null 2>&1 || missing+=("uv")
command -v elan >/dev/null 2>&1 || missing+=("elan")
command -v jq >/dev/null 2>&1 || missing+=("jq")
if command -v gh >/dev/null 2>&1; then
  gh auth status --hostname github.com >/dev/null 2>&1 || missing+=("a GitHub login (gh auth login)")
else
  missing+=("gh")
fi
[ ${#missing[@]} -eq 0 ] && exit 0

list=$(printf '%s, ' "${missing[@]}")
list=${list%, }
context="The lml plugin's prerequisites are not all available: missing ${list}. START.md in https://github.com/LeanMachineLearning/lml-claude says how to install each one."
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"},"systemMessage":"lml plugin: missing %s"}\n' "$context" "$list"
exit 0
