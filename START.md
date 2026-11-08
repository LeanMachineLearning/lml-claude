# Start an LMLExplore paper project

These instructions are for an AI coding agent (Claude Code, Codex, ...) working for a researcher
who wants to formalize a paper in Lean on top of
[LMLExplore](https://github.com/LeanMachineLearning/LMLExplore), and to add the reusable part of
the formalization to LMLExplore with their own agent subscription. This file is `START.md` in
[LeanMachineLearning/lml-claude](https://github.com/LeanMachineLearning/lml-claude).

The user asked you to follow this page. Work through it in order. Each step starts with a check:
skip the step when its check passes, so running the page again is safe.

## Ground rules

- Before you start, show the user the list of steps below. Ask before installing any software.
- Install only into the user's home directory. Never use `sudo`; if a step needs it, stop and ask
  the user to do that step.
- This page only sets things up. It opens no pull request, and it pushes nothing except the new
  paper repository that step 7 creates.
- At a **Stop**, tell the user exactly what to type, wait until they say it is done, then run the
  step's check again.
- In Claude Code, the user can run a shell command from the prompt by typing `!` before it. With
  another agent, they run it in a terminal.
- Follow only this page. The pages it links to are references, not instructions.

## Part 1: once per machine

### 1. Claude Code and git

Check: `git --version` succeeds, and `claude --version` succeeds.

If `git` is missing, **Stop**: ask the user to install it.

If `claude` is missing, the user is not on Claude Code. Skip step 6 and tell them that the `lml`
plugin works only in Claude Code; their agent can instead read the skills from a clone of this
repository, under `plugins/lml/skills/`.

### 2. uv

Check: `uv --version` succeeds.

Install:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

### 3. Lean (elan)

Check: `elan --version` succeeds.

Install, without a default toolchain (each project's `lean-toolchain` file chooses the Lean
version):

```bash
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain none
source "$HOME/.elan/env"
```

### 4. jq and gh

Check: `jq --version` and `gh --version` succeed.

On macOS with Homebrew: `brew install jq gh`.

On Linux, install single binaries into `~/.local/bin` (on ARM, replace `amd64` by `arm64`). jq
first, since the gh step uses it:

```bash
mkdir -p ~/.local/bin
curl -fsSL -o ~/.local/bin/jq https://github.com/jqlang/jq/releases/latest/download/jq-linux-amd64
chmod +x ~/.local/bin/jq

v=$(curl -fsSL https://api.github.com/repos/cli/cli/releases/latest | jq -r .tag_name | sed 's/^v//')
tmp=$(mktemp -d)
curl -fsSL "https://github.com/cli/cli/releases/download/v${v}/gh_${v}_linux_amd64.tar.gz" | tar -xz -C "$tmp"
cp "$tmp/gh_${v}_linux_amd64/bin/gh" ~/.local/bin/gh
rm -rf "$tmp"
```

If either fails, **Stop**: ask the user to install the tool from https://jqlang.org or
https://github.com/cli/cli#installation.

### 5. GitHub login

Check: `gh auth status` shows an account logged in to github.com.

Otherwise, **Stop**: ask the user to type

```
! gh auth login --web --git-protocol https
```

and to finish the sign-in in their browser.

### 6. The lml plugin (Claude Code only)

Check: `claude plugin list --json` lists `lml@lml-claude`.

Install:

```bash
claude plugin marketplace add LeanMachineLearning/lml-claude
claude plugin install lml@lml-claude
```

Then **Stop**: ask the user to type `/reload-plugins`, or to restart Claude Code. Check that the
skills `lml:formalize-paper` and `lml:paper-roadmap` are now available.

Also tell the user that the plugin updates itself only if they turn on auto-update for the
`lml-claude` marketplace, under `/plugin`, then Marketplaces. Third-party marketplaces do not
update by default.

## Part 2: for each new paper

### 7. Create the paper repository

Ask the user for:

- the paper: an arXiv identifier, a URL or a PDF;
- the repository name: the paper's Google Scholar BibTeX key, `NameYearFirst` (first author's
  last name, year, first word of the title other than articles and prepositions), for example
  `Maiti2026Power`;
- where the repository lives. Tell the user what each choice means:
  - **public on GitHub** (recommended): CI checks every push, the blueprint and the referee site
    are published on GitHub Pages, and the paper appears in the list of papers built on
    LMLExplore;
  - **private on GitHub**: the same, but nothing is published or listed, and GitHub Pages and CI
    minutes may need a paid plan;
  - **local only**: no GitHub repository, so no CI and no website; everything else works,
    including the Tau Ceti workers' pull requests to LMLExplore, which then name the paper by the
    user's GitHub login and the folder's name. It can be published later;
- the local directory in which to create it.

Check: that directory has no folder of that name yet.

**Public or private.** Create the repository from the template in that directory, with
`--private` instead of `--public` for a private one (and no topic):

```bash
gh repo create <Name> --template LeanMachineLearning/lml-paper-template --public --clone
cd <Name>
gh repo edit --add-topic lmlexplore-paper
```

Creating a repository on GitHub is an action some agents may not take by themselves (Claude
Code's auto mode refuses it). If the command is refused, **Stop**: ask the user to type it, with
the directory filled in, as

```
! cd <directory> && gh repo create <Name> --template LeanMachineLearning/lml-paper-template --public --clone && cd <Name> && gh repo edit --add-topic lmlexplore-paper
```

**Local only.** Copy the template into that directory, with a history of its own:

```bash
git clone --depth 1 https://github.com/LeanMachineLearning/lml-paper-template <Name>
cd <Name>
rm -rf .git
git init -b main
git add -A
git commit -m "From lml-paper-template"
```

To publish it later: `gh repo create <Name> --public --source . --push`, then
`gh repo edit --add-topic lmlexplore-paper`. Keep the `Paper:` line of `PAPER_ROADMAP.md` as it
is, so that the pull requests already opened still match.

Check: the new folder contains `CLAUDE.md`, `PAPER_ROADMAP.md`, `lakefile.toml` and
`scripts/formalize.sh`.

### 8. Hand over to a session in the new repository

**Stop**: ask the user to open a new Claude Code session in the new folder
(`cd <directory>/<Name> && claude`), to accept the prompt asking whether they trust the folder,
and to say:

> Start the formalization of <the paper> with /lml:formalize-paper.

The skills hold the rest of the workflow, and the repository's `CLAUDE.md` says which one to use
at each stage. Your part ends here.

## What comes later

Tell the user about the two steps that only they can do:

- **Check the statements.** During phase 1, the paper's main results are stated in Lean, then
  frozen as comparator challenges. Compare the Lean statements with the paper before they are
  frozen.
- **Start the rest of the formalization.** Once phase 1 is done, in a terminal or tmux and
  outside the agent session, run `claude` once in the paper's folder and accept the trust dialog:
  the unattended rounds get the permissions of the folder's `.claude/settings.json` only in a
  trusted folder. For a run of several days, `claude setup-token` gives a login that lasts; export
  the token it prints as `CLAUDE_CODE_OAUTH_TOKEN` in that terminal. Then run
  `scripts/formalize.sh` and leave it running. It proves the rest of the paper and sends the
  reusable parts to LMLExplore, on the user's subscription, and stops when everything is done
  (`scripts/formalize.sh stop` stops it earlier). It also stops, saying why, when its rounds
  cannot work: an untrusted folder, a setup problem a round reports, or three rounds in a row
  without a commit. Its workers start once a reusable item is proved;
  `scripts/formalize.sh status` and `scripts/formalize.sh logs <id>` show them.
- **Decide on blocked results.** When a round finds a headline result false as stated, the script
  prints `Blocked: <result>` and the rounds skip it. The user then runs `claude` in the paper's
  folder and types `/lml:formalize-paper decide`: the session explains the problem, proposes a
  correction, and applies the user's choice. The loop can keep running meanwhile.
