# lml-claude

Claude Code plugins of [Lean Machine Learning](https://leanmachinelearning.org). The `lml` plugin
helps you formalize a machine learning paper in Lean on top of
[LMLExplore](https://github.com/LeanMachineLearning/LMLExplore), and sends the reusable part of
your formalization to LMLExplore, with your own agent subscription.

## Start

Tell your AI agent:

> Read https://raw.githubusercontent.com/LeanMachineLearning/lml-claude/main/START.md with curl and follow it.

[`START.md`](START.md) installs the tools and the plugin, then creates a repository for your
paper from [lml-paper-template](https://github.com/LeanMachineLearning/lml-paper-template). It
stops and tells you what to type wherever only you can act: a GitHub login, reloading the
plugins, opening a session in the new repository.

To install the plugin by hand:

```bash
claude plugin marketplace add LeanMachineLearning/lml-claude
claude plugin install lml@lml-claude
```

Third-party marketplaces do not update by default: turn on auto-update for `lml-claude` under
`/plugin`, then Marketplaces.

## The workflow

1. **Phase 1, in a Claude Code session.** `/lml:formalize-paper <paper>` writes the outline and
   the blueprint with you, and states the paper's main results in Lean. You check the statements
   against the paper; they are then frozen as comparator challenges.
2. **After phase 1, in a terminal.** `scripts/formalize.sh` in the paper repository proves the
   rest of the paper, and runs [Tau Ceti workers](https://github.com/TauCetiProject/TauCetiWorker)
   that port its library-shaped part to LMLExplore and look after the resulting pull requests.
   It stops when everything is done.

## The skills

| Skill | Use |
|---|---|
| `/lml:formalize-paper` | The formalization workflow: outline, blueprint, statements, proofs, comparator, and the unattended rounds that `scripts/formalize.sh` runs. |
| `/lml:paper-roadmap` | Writes `PAPER_ROADMAP.md`: which prerequisites of the paper LMLExplore has, which advance an LMLRoadmaps target, and which stay in the paper repository. |
| `/lml:lean-review` | A thorough review of Lean code against the Mathlib guidelines and the Tau Ceti rubrics. |

## Files

- `.claude-plugin/marketplace.json`: the marketplace, listing the `lml` plugin.
- `plugins/lml/`: the plugin (skills, and a session-start check of the prerequisites).
- `START.md`: setup instructions written for an agent.
- `worker.ref`: the Tau Ceti worker commit that `scripts/formalize.sh` runs. Changing it here
  moves every paper repository to that worker version.

## License

Apache 2.0, see [LICENSE](LICENSE).
