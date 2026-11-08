#!/usr/bin/env python3
"""Heuristic scan of Lean 4 files for review candidates that no linter reports.

Usage: lean_smells.py [--all] FILE_OR_DIR...

Everything the Mathlib linters already enforce is deliberately left out: the standard set
(`weak.linter.mathlibStandardSet = true`: flexible/non-terminal `simp`, `show` changing the goal,
`maxHeartbeats` without comment, `λ`/`$` syntax, long lines and files, header and module docstring,
…), `lake exe runLinter` (docBlame, unusedArguments, simpNF, …) and Lean's own warnings (`sorry`,
unused variables and section variables). Make sure the project enables them instead.

Every hit is a *candidate*: open the code and confirm before reporting or changing anything.
Checks (tag in brackets):
  [doc]      module docstring without `## Main ...` section (files over 80 lines)
  [size]     proof over 50 lines without any comment (sketch the argument or split it)
  [concl∧]   conclusion with a top-level `∧` (Mathlib: prove separate lemmas)
  [concl∃]   conclusion starting with `∃` (consider a definition + characterizing lemmas)
  [hyp∧]     hypothesis binder that is a conjunction
  [implicit] implicit `{x}` binder used only in the conclusion of a non-rewrite lemma (cannot be
             inferred from the hypotheses by `have := foo h`; consider making it explicit)
  [theorem]  `theorem` keyword (some projects reserve it for headline results)
  [nolint]   `@[nolint ...]` and any `set_option` (never acceptable: fix the cause instead)
  [evade]    explicit `(_x : …)` binder or `_h…` hypothesis name in a declaration header or
             `variable`: an unused argument renamed to dodge the linter (remove the argument).
             Implicit structure binders such as `{_mΩ : MeasurableSpace Ω}` are not flagged.
  [defeq]    `erw` or `change` without a comment (undocumented defeq)
  [private]  private declarations (check: genuinely file-specific, or general and misplaced?)
  [aux]      public declaration named `*_aux` / `aux_*`
By default [theorem], [private], [concl∃] are omitted; pass --all to include them.
"""
import pathlib
import re
import sys

DECL = re.compile(r"^(@\[[^\]]*\]\s*)?((private|protected|noncomputable|nonrec|partial|unsafe)\s+)*"
                  r"(lemma|theorem|def|abbrev|structure|class|instance|inductive|opaque)\b(\s+([^\s(\[{:]+))?")
OPEN = "([{⟨⦃"
CLOSE = ")]}⟩⦄"


def depth_split(s, sep):
    """Split s on `sep` occurring at bracket depth 0."""
    out, cur, d, i = [], "", 0, 0
    while i < len(s):
        c = s[i]
        if c in OPEN:
            d += 1
        elif c in CLOSE:
            d -= 1
        if d == 0 and s.startswith(sep, i):
            out.append(cur)
            cur = ""
            i += len(sep)
            continue
        cur += c
        i += 1
    out.append(cur)
    return out


def binders_and_conclusion(header):
    """Return (binders, conclusion) of a declaration header (text before `:=`)."""
    # drop the keyword and name
    m = DECL.match(header)
    rest = header[m.end():] if m else header
    # binders: leading bracket groups
    binders, i, s = [], 0, rest
    while True:
        s2 = s.lstrip()
        if not s2 or s2[0] not in OPEN:
            break
        d, j = 0, 0
        for j, c in enumerate(s2):
            if c in OPEN:
                d += 1
            elif c in CLOSE:
                d -= 1
                if d == 0:
                    break
        binders.append(s2[:j + 1])
        s = s2[j + 1:]
    s = s.strip()
    concl = s[1:].strip() if s.startswith(":") else ""
    return binders, concl


def scan(f, show_all):
    text = f.read_text()
    lines = text.split("\n")
    hits = []

    def hit(tag, line, msg):
        if not show_all and tag in ("theorem", "private", "concl∃"):
            return
        hits.append((line, tag, msg))

    # file-level
    if "/-!" in text:
        md = text[text.index("/-!"):text.index("-/", text.index("/-!"))]
        if "## Main" not in md and len(lines) > 80:
            hit("doc", 1, "module docstring has no `## Main definitions/statements` section")

    # declarations
    decl_starts = [i for i, l in enumerate(lines) if DECL.match(l)]
    header_lines = set()
    for k, i in enumerate(decl_starts):
        end_decl = decl_starts[k + 1] if k + 1 < len(decl_starts) else len(lines)
        hdr, j = [lines[i]], i
        while ":=" not in lines[j] and not lines[j].rstrip().endswith(" where") and j + 1 < end_decl:
            j += 1
            hdr.append(lines[j])
        header = " ".join(l.strip() for l in hdr).split(":=")[0]
        header_lines.update(range(i, j + 1))
        m = DECL.match(lines[i])
        kind, name = m.group(4), (m.group(6) or "")
        if kind == "theorem":
            hit("theorem", i + 1, f"`theorem {name}`")
        if lines[i].lstrip().startswith("private") or " private " in lines[i][:20]:
            hit("private", i + 1, f"private `{name}`")
        short = name.split(".")[-1]
        if (short.endswith("_aux") or short.startswith("aux_")) and "private" not in lines[i]:
            hit("aux", i + 1, f"public auxiliary `{name}`")
        if kind in ("lemma", "theorem"):
            binders, concl = binders_and_conclusion(header)
            c0 = re.sub(r"\bif\b.*?\bthen\b", "if _ then", concl)
            is_rel = len(depth_split(c0, "↔")) > 1 or len(depth_split(c0, " = ")) > 1
            if (len(depth_split(c0, "∧")) > 1 and len(depth_split(c0, "↔")) == 1
                    and not c0.lstrip().startswith(("∃", "∀"))):
                hit("concl∧", i + 1, f"`{name}`: conclusion is a conjunction")
            if concl.lstrip().startswith("∃"):
                hit("concl∃", i + 1, f"`{name}`: existential conclusion")
            for b in binders:
                inner = b[1:-1]
                if ":" in inner and b[0] == "(":
                    typ = inner.split(":", 1)[1]
                    if len(depth_split(typ, "∧")) > 1:
                        hit("hyp∧", i + 1, f"`{name}`: conjunction hypothesis `{b[:60]}`")
            for bi, b in enumerate(binders):
                if is_rel or b[0] != "{" or ":" not in b:
                    continue
                names = b[1:-1].split(":", 1)[0].split()
                others = " ".join(x for bj, x in enumerate(binders) if bj != bi)
                for nm in names:
                    pat = re.compile(r"(?<![\w.'₀-₉])" + re.escape(nm) + r"(?![\w'₀-₉])")
                    if pat.search(concl) and not pat.search(others):
                        hit("implicit", i + 1, f"`{name}`: `{{{nm}}}` appears only in the conclusion")
        # proof body checks
        body = lines[j + 1:end_decl] if j + 1 <= end_decl else []
        body_text = "\n".join(body)
        n_body = sum(1 for l in body if l.strip() and not l.strip().startswith("--"))
        if n_body > 50 and "--" not in body_text and "/-" not in body_text:
            hit("size", i + 1, f"`{name}`: {n_body}-line proof without comments")
        for off, l in enumerate(body):
            ln = j + 2 + off
            s = l.strip()
            if re.search(r"(^|[\s;(])erw\b", s) and "--" not in l:
                hit("defeq", ln, "`erw` without comment")
            if re.match(r"(·\s*)?change\b", s) and "--" not in l:
                hit("defeq", ln, "`change` without comment")
    for n, l in enumerate(lines, 1):
        if re.search(r"@\[nolint|^\s*set_option\b|\bset_option\b.*\bin\b", l) and not l.lstrip().startswith("--"):
            hit("nolint", n, l.strip()[:90])
        if (DECL.match(l) or l.startswith("variable") or (l.startswith("    ") and n - 1 in header_lines)) \
                and re.search(r"\(\s*_[A-Za-z]\w*|[{⦃]\s*_h\w*", l):
            hit("evade", n, l.strip()[:90])
    return sorted(hits)


def main():
    args = [a for a in sys.argv[1:] if a != "--all"]
    show_all = "--all" in sys.argv[1:]
    total = 0
    for a in args:
        p = pathlib.Path(a)
        fs = sorted(p.rglob("*.lean")) if p.is_dir() else [p]
        for f in fs:
            h = scan(f, show_all)
            total += len(h)
            for line, tag, msg in h:
                print(f"{f}:{line}: [{tag}] {msg}")
    print(f"-- {total} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
