# myskills-public

A personal collection of skills for coding agents such as Codex and Claude Code.
Each skill is a folder with a `SKILL.md` that tells the agent when and how to do
one kind of task: editing prose, writing a README, drawing a diagram, revising a
paper, or asking ChatGPT for a review.

## Skills

| Skill | What it does |
| --- | --- |
| [`chatgpt-ui-review`](chatgpt-ui-review/) | Asks ChatGPT in your signed-in browser to review text, UI screenshots, or both, and saves the reply. |
| [`diagram-craft`](diagram-craft/) | Creates or revises editable SVG diagrams of architecture, workflows, and methods, including README teaser figures. |
| [`external-collaboration`](external-collaboration/) | Turns a shared GitHub repository into a request inbox for a Coopa agent that runs scoped experiments and reports results. |
| [`humanizer`](humanizer/) | Rewrites AI-sounding text so it reads like the writer without changing what it says. |
| [`public-relations`](public-relations/) | Helps with earned media: journalist pitches, newsjacking, press requests, and podcast guest prep. |
| [`readme-craft`](readme-craft/) | Writes or improves a README with a clear reading path and real examples. |
| [`research-paper-writing`](research-paper-writing/) | Improves structure, paragraph flow, and claim-evidence alignment in ML/CV/NLP papers, section by section. |
| [`stop-slop`](stop-slop/) | Removes predictable AI writing patterns from prose. |
| [`wechat-article`](wechat-article/) | Researches a topic and drafts a WeChat Official Account article (in Chinese) with author, editor, and reader agents. |

## Example

After installing `research-paper-writing`, open your paper's repository and ask:

```text
Use the research-paper-writing skill to revise the introduction in
paper/intro.tex. Keep my technical claims, make each paragraph carry one
message, and list any claim that the experiments do not yet support.
```

The skill directs the agent to load only the Introduction guide and return an
outline, revised paragraphs, and a claim-evidence map. In Claude Code you can
also run it as `/research-paper-writing`.

## Install

Copy only the skills you want. Codex reads personal skills from
`~/.agents/skills/`, and Claude Code from `~/.claude/skills/`
([Codex docs](https://learn.chatgpt.com/docs/build-skills),
[Claude Code docs](https://code.claude.com/docs/en/skills)). For one
repository only, use `.agents/skills/` or `.claude/skills/` in that repository.

```sh
git clone https://github.com/ZhiningLiu1998/myskills-public.git
skill=readme-craft
dest="$HOME/.agents/skills"   # Claude Code: "$HOME/.claude/skills"
mkdir -p "$dest"
if [ -e "$dest/$skill" ]; then
  echo "$dest/$skill already exists; not copying."
else
  cp -R "myskills-public/$skill" "$dest/"
fi
```

Start a new agent session after copying so it picks up the skill.

## Runtime notes

Some skills need local tools for specific steps:

- **`chatgpt-ui-review`** runs on macOS with Google Chrome, where you are already
  signed in to ChatGPT. Its helper is compiled with `swiftc` (Xcode Command Line
  Tools) and controls Chrome through the macOS Accessibility API, so the app
  running your agent (for example, your terminal) needs Accessibility permission
  in System Settings > Privacy & Security.
- **`external-collaboration`** is built for Coopa: it expects a Coopa-managed
  agent session and the Coopa command it provides. Its inbox helper needs
  Python 3.10 or later on macOS or Linux and an authenticated
  [GitHub CLI](https://cli.github.com/) (`gh`).
- **`diagram-craft`** checks each SVG by rendering it, using a local SVG renderer
  or a headless browser.
- **`wechat-article`** uses `pdftoppm` (Poppler) and Python with Pillow when it
  crops figures from paper PDFs.

## Optional: global instructions and tmux shortcuts

[`global/AGENTS.example.md`](global/AGENTS.example.md) is a short set of
general working conventions for coding agents. Copy the parts you want into
your own `~/.codex/AGENTS.md` (Codex) or `~/.claude/CLAUDE.md` (Claude Code);
add to an existing file rather than replacing it.

[`global/tmux.zsh`](global/tmux.zsh) defines three zsh shortcuts: `ta <name>`
attaches to a tmux session, `tn <name>` creates one, and `tl` lists sessions.
The installer expects the file at `~/.codex/skills/global/tmux.zsh` and adds one
`source` line to your `~/.zshrc`:

```sh
mkdir -p ~/.codex/skills/global
cp -n myskills-public/global/tmux.zsh \
  myskills-public/global/install-tmux-shortcuts.sh \
  myskills-public/global/test-tmux-shortcuts.zsh ~/.codex/skills/global/
sh ~/.codex/skills/global/install-tmux-shortcuts.sh
```

`cp -n` leaves any existing file with the same name untouched. Running the
installer again does not add a duplicate line. To check the shortcuts, run
`zsh ~/.codex/skills/global/test-tmux-shortcuts.zsh`.

## Licenses

Some skills come from other projects and keep their own licenses; see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The rest of this
repository has no license file.
