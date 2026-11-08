#!/usr/bin/env python3
"""Print the header (statement up to `:=` / `where`) of every declaration in Lean files.

Usage: decl_headers.py FILE_OR_DIR...   (directories are searched recursively for *.lean)

Reviewing the API surface this way (statements only, no proofs) is the fastest first pass:
names vs conclusions, hypotheses, generality, conjunctions in conclusions, namespaces.
"""
import pathlib
import re
import sys

DECL = re.compile(r"^(@\[[^\]]*\]\s*)?((private|protected|noncomputable|nonrec|partial|unsafe)\s+)*"
                  r"(lemma|theorem|def|abbrev|structure|class|instance|inductive|opaque|axiom)\b")


def files(args):
    for a in args:
        p = pathlib.Path(a)
        if p.is_dir():
            yield from sorted(p.rglob("*.lean"))
        else:
            yield p


def main():
    for f in files(sys.argv[1:]):
        lines = f.read_text().split("\n")
        print(f"\n######## {f}")
        i = 0
        while i < len(lines):
            if DECL.match(lines[i]):
                hdr = [lines[i]]
                j = i
                while (":=" not in lines[j] and not lines[j].rstrip().endswith(" where")
                       and j + 1 < len(lines) and j - i < 40):
                    j += 1
                    hdr.append(lines[j])
                print(f"{i + 1}: " + "\n".join(hdr).split(":=")[0].rstrip())
                i = j + 1
            else:
                i += 1


if __name__ == "__main__":
    main()
