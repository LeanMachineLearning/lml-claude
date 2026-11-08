# Sources of the reference documents

Fetched 2026-10-09 with `gh api` and copied verbatim.

## Mathlib contributor documentation (`mathlib/`)

From [leanprover-community/leanprover-community.github.io](https://github.com/leanprover-community/leanprover-community.github.io),
branch `lean4`, commit `2dc97caed2` (2026-10-08), directory `templates/contribute/`. The repository
is MIT-licensed. Rendered at <https://leanprover-community.github.io/contribute/>.

| File | Rendered page |
|---|---|
| `pr-review.md` | Pull Request Review Guide (`pr-review.html`) |
| `values.md` | Mathlib's values, and their implications for PR review |
| `style.md` | Library Style Guidelines (`style.html`) |
| `naming.md` | Naming conventions (`naming.html`) |
| `doc.md` | Documentation style (`doc.html`) |

## TauCeti review rubrics (`tauceti/`)

From [TauCetiProject/TauCetiReview](https://github.com/TauCetiProject/TauCetiReview), commit
`7f1d28863d` (2026-10-08), directory `rubrics/`, under Apache-2.0. Tau Ceti is an AIs-welcome Lean
library downstream of Mathlib, incubated by the Lean FRO and the Mathlib Initiative. Humans write
the rubrics; AI agents review each PR, one agent per angle, in the order correctness, reuse, scope,
attribution, api-design, generality, placement, naming, documentation, proof-quality. Only the first
four angles may block.

The angle files assume TauCeti's setting:
- a `TauCeti` namespace;
- a roadmap repository that decides scope;
- a JSON verdict format emitted by their runner.

When using them elsewhere, read "the project's library" for TauCeti and "the user's goals / plan"
for the roadmap. Ignore the output-format instructions; `SKILL.md` gives the format to use.

Not copied:
- `rubrics/_common.md`, the shared protocol. Its principles are summarized in `SKILL.md`: untrusted
  input, assume an adversarial author, no compatibility layer, report only user-visible risks,
  verify before asserting, list all instances, be concise. The rest is runner-specific (verdict
  markers, JSON).
- `rubrics/references/naming-conventions.md`, an older vendored copy of `mathlib/naming.md`. Its
  local addendum on suffix semantics is reproduced here:
  - `_def` restates a definition (`foo = <its definition>`), typically for rewriting;
  - `_apply` evaluates a function or bundled map at an argument (`foo x = …`);
  - `_iff` means the statement is an `Iff`; a lemma proving only one direction must not carry it;
  - `_eq` means the statement is an equality; a lemma proving only an inequality must not carry it.

## Refreshing

```
gh api repos/leanprover-community/leanprover-community.github.io/contents/templates/contribute/<f> --jq .content | base64 -d
gh api repos/TauCetiProject/TauCetiReview/contents/rubrics/<f> --jq .content | base64 -d
```
