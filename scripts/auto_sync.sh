#!/bin/bash
# Auto-sync all Hermes config repos to GitHub

set -e

REPOS=(
  "$HOME/.hermes"
  "$HOME/.hermes/skills"
  "$HOME/.learnings"
  "$HOME/agentic-stack"
  "$HOME/Hermes"
)

HERMES_REPO="$HOME/Hermes"

for repo in "${REPOS[@]}"; do
  if [ ! -d "$repo/.git" ]; then
    continue
  fi

  cd "$repo"

  # Check for changes (tracked or untracked, respecting .gitignore)
  if [ -z "$(git status --porcelain)" ]; then
    continue
  fi

  # Add all changes (respects .gitignore for ~/.hermes/)
  git add -A

  # Commit with timestamp
  git commit -m "auto-sync $(date '+%Y-%m-%d %H:%M')"

  # Push to origin
  git push 2>&1 || echo "push failed for $repo"
done

# After all sub-repos are pushed, update Hermes umbrella submodule pointers
cd "$HERMES_REPO"
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "auto-sync: update submodule pointers $(date '+%Y-%m-%d %H:%M')"
  git push 2>&1 || echo "push failed for Hermes"
fi

echo "auto-sync complete"
