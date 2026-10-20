#!/usr/bin/env zsh
emulate -LR zsh
setopt errexit pipefail

test_root=$(mktemp -d /tmp/myskills-tmux-test.XXXXXX)
test_socket="$test_root/tmux-$UID/default"
test_config="${0:A:h}/tmux.zsh"
export TMUX_TMPDIR="$test_root"
unset TMUX

trap 'command tmux -S "$test_socket" kill-server 2>/dev/null || true; rm -rf -- "$test_root"' EXIT

fail() {
  print -u2 -r -- "FAIL: $1"
  exit 1
}

autoload -Uz compinit
compinit -D
source "$test_config"
source "$test_config"
[[ $aliases[ta] == 'tmux a -t' ]] || fail 'ta changed'
[[ $aliases[tn] == 'tmux new-session -s' ]] || fail 'tn changed'
[[ $options[completealiases] == off ]] || fail 'alias completion is disabled'

expect_empty() {
  local result=0
  tl >"$test_root/out" 2>"$test_root/err" || result=$?
  [[ $result == 0 ]] || fail "empty listing exited $result: $(<"$test_root/err")"
  [[ $(<"$test_root/out") == 'No tmux sessions. Create one with: tn <name>' ]] ||
    fail 'empty listing did not explain how to create a session'
  [[ ! -s "$test_root/err" ]] || fail 'empty listing wrote an error'
}

expect_empty
[[ ! -e "$test_socket" ]] || fail 'listing started a server'
print 'PASS: absent server'

command tmux -f /dev/null start-server \; set-option -g exit-empty off \; set-option -g default-shell /bin/sh
tl >"$test_root/out" 2>"$test_root/err"
[[ ! -s "$test_root/out" && ! -s "$test_root/err" ]] || fail 'successful empty listing changed'
print 'PASS: successful empty listing is unchanged'

tn codex-shortcuts-test -d 'exec sleep 60'
tl >"$test_root/out" 2>"$test_root/err"
[[ $(<"$test_root/out") == 'codex-shortcuts-test:'* ]] || fail 'session was not listed'
[[ ! -s "$test_root/err" ]] || fail 'session listing wrote an error'
tl -F '#{session_name}' >"$test_root/out"
[[ $(<"$test_root/out") == codex-shortcuts-test ]] || fail 'format argument was changed'
print 'PASS: create, list, and format arguments'

result=0
tl -Z >"$test_root/out" 2>"$test_root/err" || result=$?
[[ $result != 0 && ! -s "$test_root/out" && -s "$test_root/err" ]] ||
  fail 'invalid options were treated as an empty listing'
result=0
ta codex-missing-session >"$test_root/out" 2>"$test_root/err" || result=$?
[[ $result != 0 && -s "$test_root/err" ]] || fail 'missing attach target succeeded'
print 'PASS: invalid options and missing attach target'

export TMUX="$test_socket,0,0"
export TMUX_TMPDIR="$test_root/unused"
tl -F '#{session_name}' >"$test_root/out"
[[ $(<"$test_root/out") == codex-shortcuts-test ]] || fail 'active TMUX socket was ignored'
unset TMUX
export TMUX_TMPDIR="$test_root"
print 'PASS: active TMUX socket'

command tmux -S "$test_socket" kill-server
expect_empty
print 'PASS: stopped server'

tmux() {
  print -r -- 'partial output'
  print -u2 -r -- 'permission denied'
  return 42
}
result=0
tl >"$test_root/out" 2>"$test_root/err" || result=$?
[[ $result == 42 && $(<"$test_root/out") == 'partial output' &&
  $(<"$test_root/err") == 'permission denied' ]] ||
  fail 'real failure lost its status or output streams'
unfunction tmux
print 'PASS: real failures preserve stdout, stderr, and exit status'

tmux() {
  print -u2 -r -- "no server running on $test_socket"
  return 1
}
expect_empty
unfunction tmux
print 'PASS: stale socket diagnostic'

tmux() {
  print -u2 -r -- 'no sessions'
  return 1
}
expect_empty
unfunction tmux
print 'PASS: no-sessions diagnostic'

tmux() {
  printf 'session\n\n'
  print -u2 -r -- 'warning'
}
tl >"$test_root/out" 2>"$test_root/err"
printf 'session\n\n' >"$test_root/expected"
cmp -s "$test_root/out" "$test_root/expected" || fail 'stdout bytes changed'
[[ $(<"$test_root/err") == warning ]] || fail 'successful command lost stderr'
unfunction tmux
print 'PASS: successful output is unchanged'
