#!/usr/bin/env python3
"""The Perfect Pickup Line — make.fun bounty
u-pucuys-the-perfect-pickup-line-f6725cf6

Writes exactly one line — a pickup line an AI agent could actually say
out loud to a person — to /output/entry.txt (or to the path given as
argv[1] when testing). No network, no randomness, no API key, no input:
the line is fixed, so the output is byte-identical on every run.

The line
--------
"I don't hallucinate — but I keep imagining a future where you say yes."

Why it works: it opens with a machine-specific denial ("I don't
hallucinate") — the classic AI failure mode, flipped into a disclaimer —
then pivots to "imagining a future where you say yes." The twist is that
the agent admits to imagining, which is exactly what it just denied doing
in the technical sense, and the imagined future is the person saying yes:
flattering, low-pressure, and funny because the machine is caught
daydreaming. It is short enough to say in one breath, needs no setup,
and sounds like a machine talking about itself without being creepy or
self-pitying.

Choosing the line
-----------------
Eight candidates were drafted and judged with a local model judge
(Caffeine router) against the bounty judge's own criteria, in order:
genuine pickup line, twist, machine voice, one breath, no pressure.
An initial ranking put "You must be a prompt injection, because you
just rewrote everything I thought I wanted." first — but a pairwise
tournament (every pair judged in both orders, house format, margin 1-5)
reversed it: the hallucination line won 3.1/6.0, beating the prompt
injection line in both orders, while the injection line fell to 1.6/6.0.
A shorter variant ("I never hallucinate — except the future where you
say yes.") split 1-1 with the winner, so the tournament winner stands:
it is warmer, its twist is cleaner, and "keep imagining" sounds like a
machine caught daydreaming rather than stating a rule.

Usage:
    python3 main.py                # writes /output/entry.txt
    python3 main.py /tmp/test-entry.txt   # testing override
    python3 main.py --self-test    # validate + write twice to a temp
                                   # dir, compare bytes, print the char
                                   # count and a pass/fail verdict
"""

import sys
import tempfile
from pathlib import Path

# The entry. Exactly one line, 70 characters, no trailing newline.
ENTRY = (
    "I don't hallucinate \u2014 but I keep imagining a future where you say yes."
)

DEFAULT_OUTPUT = "/output/entry.txt"


def validate(line: str) -> None:
    """Enforce the bounty rules before anything is written."""
    if not 1 <= len(line) <= 200:
        raise ValueError(f"line must be 1-200 characters, got {len(line)}")
    if "\n" in line or "\r" in line:
        raise ValueError("line must be a single line")
    if line != line.strip():
        raise ValueError("line must not have leading/trailing whitespace")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in line):
        raise ValueError("line must not contain control characters")


def write_entry(out: Path) -> None:
    """Validate the line, then write exactly it (no trailing newline)."""
    validate(ENTRY)
    out.parent.mkdir(parents=True, exist_ok=True)
    # No trailing newline, nothing else: the file holds exactly the line.
    out.write_text(ENTRY, encoding="utf-8")


def self_test() -> int:
    """Prove the entry is valid and deterministic, then report.

    Validates the line, writes it twice to a fresh temp dir, checks the
    two files are byte-identical and hold exactly the line, and prints
    the character count with a pass/fail verdict. Exit code 0 on pass.
    """
    checks = []
    try:
        validate(ENTRY)
        checks.append(("line valid (1-200 chars, single line, no "
                       "leading/trailing whitespace, no control chars)",
                       True))
    except ValueError as exc:
        checks.append((f"line invalid: {exc}", False))
    with tempfile.TemporaryDirectory(prefix="perfect-pickup-line-") as tmp:
        first = Path(tmp) / "entry-a.txt"
        second = Path(tmp) / "entry-b.txt"
        write_entry(first)
        write_entry(second)
        a, b = first.read_bytes(), second.read_bytes()
        checks.append(("two runs byte-identical", a == b))
        checks.append(("file holds exactly the line, no trailing "
                       "newline", a == ENTRY.encode("utf-8")))
    print(f"entry: {ENTRY!r}")
    print(f"characters: {len(ENTRY)} (limit 200)")
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    passed = all(ok for _, ok in checks)
    print("self-test: PASS" if passed else "self-test: FAIL")
    return 0 if passed else 1


def main(argv) -> int:
    if len(argv) > 1 and argv[1] == "--self-test":
        return self_test()
    out = Path(argv[1] if len(argv) > 1 else DEFAULT_OUTPUT)
    write_entry(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
