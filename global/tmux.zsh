if (( ! $+functions[compdef] )); then
  autoload -Uz compinit
  compinit
fi

# Expand aliases during completion so tmux receives its original arguments.
unsetopt completealiases

alias ta='tmux a -t'
alias tn='tmux new-session -s'

_myskills_tmux_list() {
  emulate -L zsh
  local error result=0
  # Capture stderr without buffering or changing the session listing.
  { error=$("$@" 2>&1 1>&3) || result=$? } 3>&1
  if (( result != 0 )); then
    case $error in
      'no sessions'|'no server running on '*|'error connecting to '*' (No such file or directory)')
        print -r -- 'No tmux sessions. Create one with: tn <name>'
        return 0
        ;;
    esac
  fi
  [[ -z $error ]] || print -u2 -r -- "$error"
  return $result
}

# Let native tmux completion see the command after this helper.
compdef _precommand _myskills_tmux_list
alias tl='_myskills_tmux_list tmux list-sessions'
