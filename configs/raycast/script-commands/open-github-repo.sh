#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Open GitHub Repo
# @raycast.mode compact
# @raycast.packageName Git

# Optional parameters:
# @raycast.icon 🐙
# @raycast.description Open the current Finder directory's GitHub repo in Chrome

dir=$(osascript -e 'tell application "Finder"
  if (count of windows) > 0 then
    return POSIX path of (target of front window as alias)
  else
    return ""
  end if
end tell' 2>/dev/null)

if [ -z "$dir" ] || ! git -C "$dir" rev-parse --is-inside-work-tree &>/dev/null; then
  echo "Not a git repository"
  exit 1
fi

url=$(git -C "$dir" remote get-url origin 2>/dev/null)
if [ -z "$url" ]; then
  echo "No remote found"
  exit 1
fi

# Normalize SSH → HTTPS
url=$(echo "$url" | sed -e 's|git@github.com:|https://github.com/|' \
                         -e 's|\.git$||')

open "$url"
echo "Opened $url"
