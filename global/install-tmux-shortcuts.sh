#!/bin/sh
set -eu

config="$HOME/.codex/skills/global/tmux.zsh"
zshrc="${ZDOTDIR:-$HOME}/.zshrc"
loader='source "$HOME/.codex/skills/global/tmux.zsh"'

if [ ! -f "$config" ]; then
  printf 'Missing %s; clone or sync MySkills first.\n' "$config" >&2
  exit 1
fi

if ! grep -Fqx "$loader" "$zshrc" 2>/dev/null; then
  printf '\n%s\n' "$loader" >> "$zshrc"
fi

printf 'Configured tmux shortcuts in %s.\n' "$zshrc"
printf 'For this terminal, run: %s\n' "$loader"
