# From the template to the first push

For a new paper repository, made from
[lml-paper-template](https://github.com/LeanMachineLearning/lml-paper-template) by `START.md` of
lml-claude, or by

```
gh repo create <Name> --template LeanMachineLearning/lml-paper-template --public --clone
```

Do the steps in order; each ends with a check that must pass before moving on. The names are those
of `SKILL.md`: `<Name>` the repository (`Maiti2026Power`), `<Lib>` the Lean library (usually the
same), `<Paper>` the folder of the paper's own results (`MXJ2026`), `<KEY>` the paper's citation
key (`MXJ26`). `tools.md` says where each tool comes from.

1. **Install the tools that `START.md` does not.** Python 3 with `pip install leanblueprint`, and
   a TeX distribution with `xelatex` and `latexmk`, for the blueprint. For the user: VS Code with
   the Lean 4 extension. Check: `elan --version`, `leanblueprint --help`, `xelatex --version`.
2. **Fill in the template.** From a clean checkout of the new repository:
   ```
   scripts/init.sh <Lib> <Paper> <KEY>                 # e.g. Maiti2026Power MXJ2026 MXJ26
   lake update LMLExplore                              # LMLExplore's current main
   cp .lake/packages/LMLExplore/lean-toolchain .       # LMLExplore's toolchain
   scripts/build.sh                                    # prebuilt Mathlib and Tau Ceti, then lake build
   ```
   `init.sh` fills in the template's placeholders (the library, the paper's folder, the citation
   key, and the GitHub owner, repository and author it finds), renames the folders, drops the
   template's part of the README, and deletes itself. Check: the build succeeds;
   `lake exe mk_all --lib <Lib> --check` passes; and `scripts/check-pins.sh` reports that every
   package LMLExplore pins is at LMLExplore's revision. Commit. Every Lean file follows the
   template's `<Lib>/<Paper>/Basic.lean`: copyright header, `module`, `public import …`, a module
   docstring, `@[expose] public section`; delete that placeholder file with the first real one.
3. **Put the paper in `source/`** (the arXiv or camera-ready TeX sources) and write
   `notes/blueprint-outline.md` before any blueprint or Lean: the results, the lemmas they need,
   what LMLExplore, Tau Ceti, LML and Mathlib already provide, the modelling choices. This is the
   contract between the chapters written next; it also fixes the label names.
4. **Write the blueprint** in `blueprint/src/`: the template has `content.tex`, `print.tex`,
   `web.tex`, `plastex.cfg` and `macros/`. Make `content.tex` a list of `\input{chapters/…}`,
   one chapter file per part of the outline, Part I following the paper and Part II holding the
   library-shaped prerequisites. The site workflow needs a `trust-extract` release for the Lean of
   `lean-toolchain` (see `tools.md`). Check: `python3 scripts/check-blueprint.py`,
   `leanblueprint pdf`, `leanblueprint web`, `lake exe checkdecls blueprint/lean_decls` (empty at
   first), and `leanblueprint serve` to look at the site. On GitHub, set Pages to deploy from
   "GitHub Actions".
5. **Fill in `formalization.yaml`, `literature/bibliography.json` and the README.** In
   `formalization.yaml`: `project`, `sources`, and the `status` section listing every headline
   result with its intended Lean name and blueprint label; keep the schema comment in the header,
   so that the editor validates it. In `bibliography.json`: the paper's entry under `<KEY>`, with
   the `version` whose numbering the citations will use (LMLExplore's
   `scripts/literature/lookup.py propose` drafts it). `notes/paper-errata.md` starts with its
   header only.
6. **Set up the comparator side** once the headline statements exist and the user has checked
   them against the paper (end of phase 1). Write `comparator/targets.txt`, one headline
   declaration name per line (the name after the `<Lib>.` prefix), and list every
   `Challenge_<name>` in the `globs` of the `Comparator` library in `lakefile.toml`. Fill the
   imports of `comparator/Solution.lean` and the table of `comparator/README.md`. The template's
   `scripts/make-challenges.py` runs challenge-gen, which it clones and builds for the project's
   toolchain (see `tools.md`). Check: `python3 scripts/make-challenges.py`, `lake build
   Comparator`, then one `scripts/comparator-verify.sh --insecure <config>`.
7. **First push.** Commit and push, and check that the workflows go green: build, lint,
   `mk_all --check`, comparator build, referee site, literature links, blueprint deployment. From
   here on, follow the workflow in `SKILL.md`.
