---
name: paper-roadmap
description: Write and refresh PAPER_ROADMAP.md in an LMLExplore paper project. It has one row per library-shaped prerequisite of the paper, tagged exists (LMLExplore has it), target (it advances an LMLRoadmaps target), refactor (it changes existing LMLExplore code), staged (library-shaped, with a proposed target) or paper, and its status, so that Tau Ceti workers port the right material to LMLExplore. Use at the end of phase 1 of /lml:formalize-paper, in its unattended rounds (tag, refresh), or when asked to tag or update the paper roadmap.
---

# The paper roadmap

`PAPER_ROADMAP.md`, at the root of a paper repository, says where each prerequisite of the paper
belongs: in LMLExplore already, in LMLExplore through a port, or in the paper repository. Three
readers depend on it:

- the paper loop of `scripts/formalize.sh`, which proves everything that is not `exists` and opens
  the `refactor` pull requests;
- the Tau Ceti authoring workers, which port the `target` items once they are `proved`;
- LMLExplore's maintainers, who collect the `staged` items of all papers to write new roadmap
  targets.

Scripts parse the file, so keep its format exactly.

## Format

```markdown
# Paper roadmap: On the Power of Adaptivity for ε-Best Arm Identification in Linear Bandits

Paper: alice/Maiti2026Power · LMLExplore 4cb54f2e8a1b · LMLRoadmaps 2ac39b4c0d7e · Refreshed 2026-11-08

## Items

| Id | Item | Tag | Link | Status | Files |
|---|---|---|---|---|---|
| R1 | Fixed-budget and fixed-design identification algorithms | exists | `LMLExplore.Identification.fixedBudget` | – | |
| R2 | Linear Gaussian bandit and (ε, δ)-PAC identification | target | Identification 9.1 | proved | `ForLMLExplore/Identification/LinearBandit.lean` |
| R3 | Gaussian width, Sudakov–Fernique and Borell–TIS inequalities | staged | S1 | todo | `ForLMLExplore/Probability/GaussianWidth.lean` |
| R4 | Design matrices and the width term w(𝒳) | paper | | todo | `MXJ2026/Width.lean` |

## Notes

- R2: Identification 9.1 asks for linear tasks as pullbacks of the unstructured tasks along the
  mean functional, with no separate definitions; the port takes that form.

## Proposed targets

### S1. Gaussian processes

The support function of a set and the Gaussian width of a set for a measure, …, with references.
```

- **Header line.** `Paper:` gives the `<owner>/<repo>` of the paper repository: the value that the
  paper's pull requests to LMLExplore carry in their `Paper:` line. Then the twelve-character
  commits of the LMLExplore pin and of the LMLRoadmaps `main` that the tags were checked against,
  and the date of that check.
- **Id.** `R1`, `R2`, …, never renumbered or reused. Pull requests name their item with a line
  `Item: <Id>`.
- **Item.** A short description of one unit that would make one pull request: a definition with
  its basic API, or a theorem with the lemmas only it needs. Not one row per lemma.
- **Tag and Link:**

  | Tag | Meaning | Link |
  |---|---|---|
  | `exists` | LMLExplore has it at the pinned commit, up to renaming, generalization and definitional unfolding | the LMLExplore declaration, in backquotes |
  | `target` | it advances an LMLRoadmaps target, or is a direct prerequisite of one | the target, `Area N.k`: roadmap directory, layer number, item number |
  | `refactor` | LMLExplore has a narrower version, or the definition without the API the paper needs | the LMLExplore declaration to change, in backquotes |
  | `staged` | library-shaped, but no target covers it | `S<n>`, its proposed target |
  | `paper` | specific to the paper | empty |

- **Status:** `todo`; `proved`, when its files are proved with no `sorry`; `PR #N`, while a pull
  request to LMLExplore is open; `merged #N`, once it is merged. `–` for `exists`.
- **Files:** the item's files in the paper repository, in backquotes, relative to `<Lib>/`.
- **Notes:** what a porter needs to know, by Id: the generality the target asks for, a convention
  to follow, the part of the item that LMLExplore already has.
- **Proposed targets:** for each `staged` item, a target written like an LMLRoadmaps item (what
  to build, at the generality of the literature, with references), ready for a maintainer to put
  in a roadmap.

## Tagging

Inputs: Part II of the blueprint and `notes/blueprint-outline.md`; `<Lib>/ForLMLExplore/`; the
pinned LMLExplore (`.lake/packages/LMLExplore`) and its dependencies; and a fresh checkout of
LMLRoadmaps, cloned or fetched into `.tauceti/LMLRoadmaps`.

For each prerequisite, in this order:

1. **In the pinned dependencies?** Search LMLExplore, Tau Ceti, LML and Mathlib, up to renaming,
   generalization and definitional unfolding. Found as the paper needs it: `exists`. Found in a
   narrower form, or without the API the paper needs: `refactor`. Only on LMLExplore's `main`, not
   at the pin: `exists` with the status `merged`, so that the final bump switches to it.
2. **On a roadmap?** Read the active roadmaps, `LMLRoadmaps/<Area>/README.md`. The item is a
   `target` when it advances a specific target, or when that target needs it on a real and
   proximate path. LMLExplore's scope reviewers apply exactly this test, and reject material that
   piles up around a target without bringing it closer; when in doubt, the item is `staged`. A
   `target` item must reach the generality its target states: write in Notes what that asks of
   the port.
3. **Library-shaped?** It names no object specific to the paper, and it would fit LMLExplore:
   `staged`, with a proposed target. State the proposed target at the strongest standard
   generality of the literature, not at the paper's: tasks on arbitrary models rather than
   vectors of means, exponential families rather than one distribution, conditional statements
   along a filtration rather than sums of i.i.d. variables, any algorithm–environment pair rather
   than one bandit type, suprema rather than attained maxima.
4. **Otherwise:** `paper`.

Fill in the header and commit the file.

## Refresh

Due when LMLRoadmaps `main`, or the set and states of the paper's pull requests to LMLExplore,
changed since the header.

1. **Roadmaps.** Fetch LMLRoadmaps. For each `staged` item, check whether a target now covers it;
   if one does, retag the item `target` and drop its proposed target. For each `target` item,
   check that its target still exists under the same number; if it moved, update the link, and if
   it is gone, retag the item `staged` with a proposed target.
2. **Pull requests.** List the paper's pull requests,
   ```bash
   gh pr list -R LeanMachineLearning/LMLExplore --state all \
     --search '"Paper: <owner>/<repo>" in:body' --json number,state,body
   ```
   and match each to its item by its `Item:` line. The status is `PR #N` while the pull request is
   open and `merged #N` once it is merged. A pull request closed without merging sets the item back
   to `proved`, with the reason in Notes when the pull request gives one.
3. Update the header and commit.
