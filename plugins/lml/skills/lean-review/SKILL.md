---
name: lean-review
description: Review Lean 4 code (Mathlib-style libraries, LML/LMLPapers material, paper formalizations) to raise its quality, following the Mathlib review guidelines and the TauCeti review rubrics (correctness, reuse, scope, attribution, API design, generality, placement, naming, documentation, proof quality), then a second phase scrutinizing each file and important result for the right generality (which hypotheses can be weakened with the current proof or with an alternative one), then apply and verify the fixes. Use when asked to review Lean files, a PR or a library, make Lean code more Mathlib-like, or prepare material for upstreaming.
---

# Reviewing Lean code for quality

This skill combines two sources:
- Mathlib's contributor documentation (PR review guide, values, style, naming, documentation);
- the TauCeti review rubrics, adversarial per-angle review prompts for an AI-written Lean library
  downstream of Mathlib.

The originals are in `references/`, with their provenance in `references/SOURCES.md`; consult
them for detail. This file is the working procedure.

Companion scripts (run with `python3 ~/.claude/skills/lean-review/scripts/<name>`):

- `decl_headers.py FILE_OR_DIR...`: every declaration's statement, without proofs. This is the
  fastest way to review an API surface.
- `lean_smells.py [--all] FILE_OR_DIR...`: heuristic candidates that no linter reports:
  - conjunctions in conclusions or hypotheses;
  - conclusion-only implicit arguments;
  - `change`/`erw` without a comment;
  - silenced linters;
  - long uncommented proofs;
  - missing `## Main …` sections.

  Every hit is a candidate to confirm by reading the code, never a finding by itself.

## Principles

- **Assume an adversarial author.** The code was probably written by an AI, possibly one with
  your own blind spots. Do not defer to fluent docstrings or plausible names: read the actual
  definitions, check the mathematics, try to break each statement.
- **Verify before asserting.** Every finding gives a location, the problem, a concrete fix, and
  evidence: the grep hit, the line, or the counterexample. Never claim that a lemma exists, or
  doesn't, without having searched (`grep -rn` under `.lake/packages/mathlib`, the other
  `.lake/packages/*`, and the project).
- **Materiality.** Report user-visible risks: wrong mathematics, duplicated API, a misleading
  interface, misplaced material, a fragile proof, missing credit. Skip taste preferences. When
  unsure whether a point clears the bar, omit it.
- **All instances.** Once you find a defect, find every other instance of it in scope.
- **No compatibility layer inside a project.** A rename or move updates every use and deletes
  the old surface: no aliases, wrappers, forwarding modules or `deprecated` shims. Mathlib PRs
  are the exception: they follow Mathlib's deprecation policy (`references/mathlib/style.md`,
  "Deprecation").
- **Mathlib values.** General definitions, weak hypotheses, strong conclusions, classical
  reasoning, maintainability ("zero `sorry`s is a starting point, not an end point").
- **Never do the linters' work.** Whatever a linter enforces is not reviewed by hand, not
  scanned for, and not reported: make the linters run and pass, then review what they cannot see.
  - The Mathlib standard set (`weak.linter.mathlibStandardSet = true` in the lakefile) covers:
    - non-terminal / flexible `simp` (`flexible`);
    - `show` that changes the goal;
    - `set_option maxHeartbeats` without a comment (with one it is still forbidden, see below);
    - `λ` / `$` syntax, `cdot`, `multiGoal`, `refine'`, old `obtain`, whitespace;
    - long lines and files;
    - copyright header and module docstring;
    - unused `Fintype` / `Decidable` instances.
  - `lake exe runLinter` covers docBlame, unusedArguments, simpNF, dupNamespace, and more.
  - Lean's own warnings cover `sorry` and unused variables and section variables.
  
  If a project does not enable these, enabling them is the finding.
- **No `set_option`, no silenced linters, no evasion.** The code must pass the linters as they
  are. Each of these is a finding, never an acceptable fix:
  - `set_option` (`maxHeartbeats`, `synthInstance.*`, `linter.* false`, …), with or without `in`;
  - `@[nolint …]`;
  - an unused variable or hypothesis silenced by renaming it `_h` / `_x`.
  
  Fix the cause instead:
  - remove the unused argument, and update the callers;
  - speed up or split the slow proof;
  - restate the lemma so the linter's concern goes away.
  
  If the unused argument is in a frozen statement, tell the user. Dropping it gives a strictly
  stronger statement, but it still changes the frozen statement, so it needs their approval.

## Workflow

### 0. Scope

- Decide what is under review. For a library that grew since a commit:
  `git diff --name-status <base> -- <lib dirs>`. Separate new files from additions to existing
  ones.
- Identify what is **frozen**:
  - headline statements and the definitions in their closure (comparator challenges);
  - definitions shared with other repositories;
  - anything the user said not to touch.
  
  Fixes must not change frozen statements. If a frozen statement is wrong, stop and ask.
- Choose the mode: review only (report findings) or review and fix (the default when the user
  says "review … and make changes" / "make it more Mathlib-like").
- For more than a few thousand lines, consider parallel subagents per file group or per angle.
  Ask the user first, and launch them with `model: "opus"`.

### 1. Mechanical layer

Make the linters run and pass before judging semantics. First check that the lakefile enables
`weak.linter.mathlibStandardSet = true` and has `lintDriver = "batteries/runLinter"`; enable them
if missing. Then run, and fix everything reported:

```
lake build <Lib> --wfail                  # all linter warnings are errors
lake exe runLinter <Lib>                  # Mathlib linters (docBlame, unusedArguments, simpNF…)
lake exe mk_all --lib <Lib> --check       # root import file up to date
grep -rn "sorry" <Lib>                    # none in finished material
```

Then run `#print axioms` on the main results, in a scratch file with `import <Lib>`. Expect only
`propext`, `Classical.choice` and `Quot.sound`.

### 2. Survey

- Run `decl_headers.py` and `lean_smells.py` on the files in scope.
- Read every module docstring.
- Write a map: topic → files → definitions → their characterizing lemmas.
- Note for each new file which existing file of the same topic it could join.

### 3. Angle passes

Do the passes in this order. The first four are integrity angles: a failure there can sink the
material, so check them first. The details per angle are below.

1. correctness
2. reuse
3. scope
4. attribution
5. API design
6. generality
7. placement
8. naming
9. documentation
10. proof quality

Angle 6 here is the surface checklist: unused or implied hypotheses and the typeclass ladder.
The systematic scrutiny of generality is a separate phase, step 6 below, run on the cleaned code.

### 4. Findings

List the findings grouped by angle, each with this shape:

```
file:line — issue — fix — evidence
```

Rate each one *blocking* (wrong or vacuous statement, outright duplicate, missing credit),
*should fix*, or *minor*. In review-only mode, report the list. Use the `ReportFindings` tool when
the session's review instructions ask for it, otherwise give concise Markdown. Then stop.

### 5. Fix (review-and-fix mode)

Apply fixes in this order, building after each batch:

1. file organization (merges, moves, renames of files);
2. API (statements, hypotheses, namespaces);
3. names;
4. documentation;
5. proofs.

Mechanics are in "Applying fixes" below.

### 6. Generality phase

A second pass, on the code as it stands after step 5, asking of every file and every important
result: **is this done in the right generality, and which hypotheses could be weakened, with the
current proof or with another one?** Angle 6 of step 3 only catches what is syntactically unused
or obviously implied; this pass is where most generality defects are found. It needs the clean
code and the API map from step 2, and it is never skipped, in either mode.

Important results are: every definition, everything listed under `## Main definitions` and
`## Main statements`, every public theorem, and every lemma on the dependency path of a main
statement. For a file under about 200 lines, that is every declaration. Private helpers matter
only when weakening them would weaken a public result.

For each file, then each result, in writing:

1. **Inventory the hypotheses**: explicit hypotheses, instance arguments, the ambient `variable`
   instances, and the type of each object (`ℝ`, `ℕ`-indexing, `EuclideanSpace`, `Measure` vs
   `Kernel`, `Fintype`). For each one, find the proof step that needs it: grep the proof for the
   lemma that requires it, or remove it and read the error. A hypothesis whose only use is a
   consequence available under a weaker assumption is a finding: `measure_univ` used as
   `μ univ ≠ ∞`, `IsMarkovKernel` used as `κ x univ ≤ 1`, `Measurable f` used only through
   `AEMeasurable`, `∀ x` used under `∀ᵐ x`, `0 < φ A` used as `φ A ≠ 0`.
2. **Compare with the literature and with Mathlib.** State the result the way the strongest
   standard reference does (σ-finite rather than finite, sub-Markov rather than Markov, s-finite
   kernels, `Finite` rather than `Fintype`), and the way Mathlib states its neighbours: read the
   hypotheses of the Mathlib lemmas the result extends or feeds into, and of the lemmas it uses.
3. **Try the weakening.** Edit the statement in place, with the hypothesis dropped or the
   typeclass replaced by the next rung of the ladder (Generality checklist below), and build.
   - It builds: keep it. Then recheck the callers, which may drop hypotheses of their own, and
     check whether the lemma now subsumes another one (reuse).
   - It fails at one step: find the alternative argument for that step in the weaker setting.
     The catalogue of standard tricks is in the Generality checklist; search Mathlib for the
     weaker-hypothesis version of the lemma that failed. "Free" is not the bar: a **small**
     change (a few lines, a case split, an instance derived from a bound already in the proof, a
     different Mathlib lemma) is applied now, even when the first attempt did not build. Only a
     **large** change is reported instead of done: one that needs a development that does not
     exist yet ("this could be generalized, but it needs 2000 lines on the theory of X"). The
     report names the failing step, the missing theory and its rough size.
   - Never silence a linter, add an unused argument, or weaken the conclusion to make a
     generalization go through.
4. **Right objects, not only right hypotheses.** Ask whether the statement should be about a
   more general object: a `Kernel` instead of a `Measure`, a filter instead of `ℕ → _`, an
   arbitrary set instead of a measurable one, a predicate (`IsSmallSet κ C n ν`) instead of an
   existential, `κ ^ n` instead of one fixed `n`, a `Prop` on all `x` instead of an `∀ᵐ` when
   the proof gives it. Also the converse: do not introduce a parameter, typeclass or index type
   that nothing in scope or in Mathlib instantiates differently. The bar is the natural
   generality in which the proof works, not the maximal one.
5. **Frozen statements** are not changed; a possible weakening of a frozen hypothesis is
   reported to the user with the evidence from point 3.

Record the outcome per file as a short table: result, hypotheses dropped or weakened,
hypotheses kept and the step that needs each one, generalizations left open (large changes only,
each with its missing theory). In review-only mode
this table is the report of the pass. In review-and-fix mode, apply the weakenings that build
(statements first, then callers), rebuild, and report the rest.

A grep listing the strongest assumptions in scope is a good starting point:

```
grep -rnoE "\[(IsProbabilityMeasure|IsMarkovKernel|IsFiniteMeasure|IsFiniteKernel|Fintype|DecidableEq|Nonempty|Nontrivial|CompleteSpace|FiniteDimensional|StandardBorelSpace|CountablyGenerated|SecondCountableTopology)[^]]*\]" <Lib>
```

### 7. Verify

- Rerun step 1, plus `#print axioms` on the main results.
- If statements are frozen by comparator challenges, regenerate them and diff against the last
  commit: only imports, `open` lines, docstrings and namespace stubs may change.
- Blueprint:
  - update the `\lean{}` names of renamed declarations;
  - rebuild (`leanblueprint pdf && leanblueprint web`);
  - run `lake exe checkdecls blueprint/lean_decls`;
  - keep `\leanok` coverage complete.

### 8. Record

- Update the project notes (`notes/upstreaming-candidates.md`, README, `formalization.yaml` status)
  and memory.
- Summarize the changes for the user: what moved where, the API changes, the hypotheses
  weakened in step 6, and what was left open and why, including the generalizations not done.
- Do not commit unless asked.

## Angle checklists

### Correctness and faithfulness (can block)

Try to break every definition and statement; approve only after failing.

- Quantifiers, the direction of implications, the objects, and edge cases: empty types,
  `T = 0`, a single action (`m = 1`), dimension `0`, degenerate parameters.
- **Junk values make statements vacuous or false.** In Lean:
  - `x / 0 = 0` and `Real.log 0 = 0`;
  - `Real.sqrt` of a negative number is `0`;
  - `ENNReal.toReal ∞ = 0`;
  - the inverse of a singular matrix is `0`;
  - `⨅`/`sInf` over an empty set is `0` in `ℝ`.
  
  A hypothesis such as `⟪x, S⁻¹ x⟫ ≤ c` holds trivially for a singular `S`. A bound `C / gapMin`
  with `gapMin = 0` claims `≤ 0`.
- Content moved into hypotheses. An assumption that makes the statement trivial. A predicate or
  structure with neither a consuming theorem nor a nontrivial witness: require one.
- Placeholders: `True`, or a trivial stand-in, in a signature or structure field.
- Over-strong typeclass assumptions that silently narrow the claim.
- When a statement looks false, build a counterexample: a small instance with exact arithmetic,
  or a simulation script for quantitative bounds. Report it with the evidence. Never weaken or
  "fix" a frozen statement without the user's approval.

### Reuse and duplication (can block on an outright duplicate)

- For each new declaration, search for an existing one up to renaming, unfolding, symmetry or
  specialization:
  - grep distinctive identifiers in `.lake/packages/mathlib/Mathlib`, LML, and sibling
    libraries (e.g. LMLPapers);
  - try `exact?` / `apply?` in a scratch file that imports Mathlib.
- Standard plumbing almost always has a named lemma. Examples met in practice:
  - `Integrable.of_bound` instead of a hand-rolled boundedness lemma;
  - `HasCondDistrib.lintegral_prodMk` instead of a private copy;
  - `Real.rpow_add_le_add_rpow`;
  - `rpow_one_add_le_one_add_mul_self`.
- Within the project, look for:
  - near-clones in different files;
  - private lemmas restating public ones;
  - special cases proved separately from a general lemma that is also present (delete the
    special case, use the general one with `(by norm_num)` arguments);
  - thin wrappers, i.e. one-line lemmas that only reorder or weaken another lemma's interface;
    worst of all is a wrapper that takes a hypothesis it never uses;
  - `∧`-bundles of existing lemmas.
- Every finding names the existing declaration and shows how to use it.

### Scope (can block)

- One topic per file and per change. An opportunistic refactor bundled with new material gets
  split.
- Material with no consumer and no clear library value is a candidate for deletion. Grep for
  uses before keeping a helper public.

### Attribution (can block on clearly missing credit)

- The module docstring cites the paper or book a development follows (`## References`, Mathlib
  `references.bib` style when upstreaming). Bold the names of named theorems
  (**Ville's inequality**).
- Material copied or adapted from another library (Mathlib PR, LMLPapers) says so.

### API design

- **Minimal surface.** `private` is only for helpers specific to the surrounding proof. General
  infrastructure is relocated and exported, never hidden.
- **Characteristic API for each definition:**
  - `_def` / `_apply` / `mem_*_iff` restatements, and the interaction with the operations in
    scope;
  - measurability and continuity (`@[fun_prop]`);
  - `@[simp]` normal forms, plus `@[gcongr]` / `@[grind]` where they help.
  
  Try to use the definition without unfolding it.
- **Standard predicates in hypotheses**, matching the name: `IsMaxOn f s a`, not a spelled-out
  `∀ q ∈ s, f q ≤ f a` in a lemma named `…_of_isMaxOn`. The same goes for `Monotone`, `HasLaw`,
  `IsProbabilityMeasure` and `Integrable`.
- **No conjunctions in conclusions or hypotheses** (Mathlib style): prove separate lemmas, and
  take separate hypotheses. An `↔` with a conjunction on the right is fine. A case-analysis lemma
  (`A ∨ B` of conjunctions) is acceptable when it is the natural tool.
- **Definitions instead of existentials** when the witness is canonical and reused: a `def`
  plus lemmas characterizing it.
- **Explicit vs implicit.** An argument determined only by the conclusion of a non-rewrite lemma
  (an inequality) should be explicit; `have := foo h` cannot infer it. Rewrite lemmas (`=`, `↔`)
  conventionally keep such arguments implicit.
- **Dot notation.** A lemma whose main hypothesis is `h : IsAlgEnvSeq …` / `h : IsPSNE …` goes in
  that namespace (`lemma _root_.Learning.IsAlgEnvSeq.foo`), so that `h.foo` works.
- **No structures bundling a function with its measurability:** plain functions plus `hf`
  hypotheses (user preference). No free data in structures: if `@[ext]` cannot hold on the data
  the laws use, drop the extra data.
- **`theorem` vs `lemma`.** Some projects reserve `theorem` for headline results; follow the
  project.

### Generality

Surface checklist for angle 6 of step 3; the systematic pass is step 6 of the workflow.

- **Unused hypotheses.** Remove them. The linter catches syntactically unused ones; also look for
  hypotheses implied by others (e.g. `u ∈ [-1, 1]` when `u` is the mean of rewards in
  `[-1, 1]`). Never silence the linter or rename the argument to `_h`. In a frozen statement,
  ask the user to drop the hypothesis (see Principles).
- **Weakest natural hypotheses.** The ladders below go from strongest to weakest; try the next
  rung, and go down as far as the proof allows:
  - measures: `IsProbabilityMeasure` → `IsFiniteMeasure` → `SigmaFinite` → `SFinite` → none;
  - kernels: `IsMarkovKernel` → `IsZeroOrMarkovKernel` / sub-Markov (`κ x univ ≤ 1`) →
    `IsFiniteKernel` → `IsSFiniteKernel` → none;
  - finiteness: `Fintype` → `Finite` → `Countable`, with `MeasurableSingletonClass` or
    `DiscreteMeasurableSpace` rather than a measurable-space instance on a discrete type;
  - measurability: `Measurable` → `AEMeasurable` / `AEStronglyMeasurable`; `MeasurableSet` →
    `NullMeasurableSet`; `∀ x` → `∀ᵐ x`; `s ⊆ t` → `s ≤ᵐ[μ] t`; `f = g` → `f =ᵐ[μ] g`;
  - spaces: `EuclideanSpace ℝ (Fin n)` → inner product space → normed space;
    `FiniteDimensional` → `CompleteSpace` → none; `StandardBorelSpace` → `CountablyGenerated` →
    none; `ℝ` → an ordered field, or `ℝ≥0∞` when the quantities are nonnegative;
  - indexing: `ℕ`-sequences and `atTop` → a filter on a preorder, when only monotonicity or
    eventual behaviour is used; `Finset.sum` over `univ` → `finsum` / `tsum`;
  - scalars and masses: `0 < c` → `c ≠ 0` (same on `ℝ≥0∞`, weaker on `ℝ`); normalizing by
    `IsProbabilityMeasure` → carrying `μ univ` through the statement (`μ univ • π`).
- **Standard tricks for an alternative proof** in the weaker setting:
  - finite → σ-finite or s-finite: exhaust by `spanningSets`, restrict to `sigmaFiniteSetWRT` or
    `sigmaFiniteSet` (a null-set argument then often removes a finiteness assumption entirely,
    as in `exists_null_restrict_compl_absolutelyContinuous`), or decompose with `sfiniteSeq` and
    `Measure.sum`;
  - probability → finite: carry the mass instead of normalizing, and handle `μ = 0` separately;
  - Markov → sub-Markov: the killed chain `κ.restrict hs` is the model case; replace
    `measure_univ` by `prob_le_one`-style bounds and `measure_ne_top`;
  - `Measurable` → `AEMeasurable`: work with `AEMeasurable.mk` and transport along `ae_eq`;
  - `Fintype` → `Finite`: `Fintype.ofFinite` locally, classically;
  - a hypothesis used in only one direction of an `↔`, or in one branch of a case split: split
    the lemma, so that each half carries only what it needs;
  - a hypothesis used only to exclude a degenerate case (`μ = 0`, `n = 0`, `s = ∅`): check
    whether the statement is true, often trivially, in that case, and drop the hypothesis.
- Prove the general result and derive special cases in one line. Do not generalize
  speculatively (parameters that never specialize to anything used).

### Placement and imports

- Each declaration lives next to the definition or theory it elaborates:
  - API of a definition goes in the definition's file;
  - generic real analysis or measure theory goes in the Mathlib-mirror directory (`<Lib>/Mathlib/…`
    with Mathlib's path), even when only one project file uses it.
- **Files by topic**:
  - merge small files on one subject (`Foo.lean` + `FooIntegral.lean`; a theorem file + its
    "Optimism" sibling);
  - dissolve grab-bag files into the topic files of their parts;
  - split files whose sections are only loosely related (raw length is the `longFile` linter's
    job);
  - sibling files sharing a CamelCase prefix that names their subject become a directory.
- Imports are minimal and specific (never `import Mathlib` in a library file). A suspicious new
  import often means the material belongs elsewhere.

### Naming

Full rules: `references/mathlib/naming.md`.

- **Case.** Theorem names are snake_case. `Prop`s and `Type`s are UpperCamelCase. Functions and
  other terms are lowerCamelCase, named after what they return. An UpperCamelCase name becomes
  lowerCamelCase inside a snake_case name. American spelling.
- **Describe the conclusion**, read outward, in Mathlib vocabulary:
  - `pos`/`nonneg`/`nonpos`/`neg`, `le`/`lt`, `ne_zero`;
  - `mem`, `sum`, `prod`, `smul`, `inner`, `norm`, `comp`;
  - `inj` / `injective`, `mono`.
  
  Hypotheses follow `_of_`, in order. Use `exp`, not `rexp`, for `Real.exp` (`cexp` for the
  complex one).
- **Do not overstate.** `_iff` only for `↔`; `_eq` only for `=`; `_le` for `≤`. `_def` restates a
  definition; `_apply` evaluates at an argument.
- **Consistency.** Match adjacent declarations and the existing namespace. Predicates are
  prefixes (`isClosed_Icc`), except `_injective` / `_monotone`-style suffixes.
- Introduce notation sparingly, and `scoped`.

### Documentation

Format: `references/mathlib/doc.md`.

- **Module docstring layout:**
  - a `#` title and a summary;
  - then `## Main definitions`, `## Main statements`, `## Notation`, `## Implementation notes`,
    `## References`, `## Tags`, in that order.
  
  The lists must match the current names after any rename or move.
- **Docstrings** on every definition and every main or nontrivial theorem. They describe the
  object or result, not the proof, and not the project process (phases, packages, agents,
  roadmap status).
- **No overclaiming.** A docstring must not promise more than the statement gives. Watch for
  stale text after moves.
- **Sectioning** with `/-! ### … -/`. Long proofs (more than 50 lines) carry comments sketching
  the argument. Cross-reference related declarations.

### Proof quality

Style-level proof issues (non-terminal `simp`, `show` changing the goal, multiple goals, `λ`)
are the linters'. This angle is about what they cannot judge.

- **Robust automation.** Prefer `simp`, `grind`, `omega`, `positivity`, `gcongr`, `fun_prop`,
  `linarith`, `nlinarith`, `field_simp`, `ring` over long chains of named rewrites. A squeezed
  terminal `simp only` that lists many lemmas is fragile; prefer the unsqueezed call.
- **Defeq hygiene.**
  - `change` / `erw` need a comment saying why; prefer a lemma.
  - Do not rely on accidental definitional equality across wrappers or coercions.
  - Prefer `(rfl)` to `rfl` for lemmas that should not leak defeq.
- Factor repeated or substantial reasoning into lemmas. Split proofs over 50 lines, or comment
  their structure.
- **No `set_option` or silenced linters.** A `set_option maxHeartbeats` means the proof is too
  slow: find the expensive step (`set_option trace.profiler` locally, never committed) and fix it.
  The same goes for `@[nolint …]`, `set_option linter.… false` and `_`-renamed unused
  arguments (see Principles).

## Applying fixes: Lean 4 mechanics

- **Move code with scripts, not by hand.** Python with exact-string `assert s.count(a) == 1`
  replacements. `git mv` for file renames. Then `lake exe mk_all --lib <Lib>`, and grep every
  importer of a moved module.
- **Section variables.** A lemma moved into a file with other `variable` blocks may pick up
  unused instance arguments (linter warnings) or duplicate instances. Fixes:
  - wrap it in a `section`;
  - use `omit [...] in` for one declaration;
  - use `omit [...]` as a command for the rest of a section;
  - drop duplicated `variable` lines.
- **Renaming into `_root_.Foo.bar`.** Inside the proof, bare identifiers now resolve in
  namespace `Foo` first, so a call to a same-named lemma elsewhere may hit the lemma itself.
  Qualify it (`Learning.foo`).
- **Spelled-out hypothesis → `IsMaxOn`/predicate.** Callers still typecheck by defeq. Inside
  proofs, `h hx` now has membership form: use `show … from h hx`, or a type ascription, before
  `linarith`/`nlinarith`.
- **Elaboration order.** `have := lemma (by norm_num) …` fails when the arguments solved by
  `norm_num` depend on an implicit fixed only later. Name it: `lemma (a := 1 / 2) (by norm_num) …`.
- **Moving `Real` lemmas** into `namespace Real` changes their full names. Qualify call sites
  (`Real.foo`), or the files must `open Real`.
- **Ports to a second library** (e.g. LMLPapers):
  - map the paths;
  - copy new files;
  - merge additions into existing files, keeping the target's own definitions, and adapt proofs
    that depended on the source's variants;
  - leave other people's uncommitted work alone;
  - build everything, lint the touched modules, and check name collisions
    (`scripts/upstream_collisions.sh` in LMLPapers).
- Rebuild after every batch; one batch at a time keeps error messages local.
