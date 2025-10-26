# scripts/auto_fix_backslash_errors.py
"""
Automatically fix corrupted regex or stray backslash sequences
(e.g., "\g<1>", "\g<2>", "\x", etc.) that cause SyntaxError.

Run:
    python scripts/auto_fix_backslash_errors.py
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET_DIR = ROOT / "leviathan"

# patterns that break syntax
BAD_PATTERNS = [
    re.compile(r"\\g<\d+>"),
    re.compile(r"\\x[0-9A-Fa-f]{0,2}"),
    re.compile(r"\\$"),
]

fixed = 0

for py_file in TARGET_DIR.rglob("*.py"):
    text = py_file.read_text(encoding="utf-8")
    new_text = text
    for pat in BAD_PATTERNS:
        new_text = pat.sub("", new_text)
    if new_text != text:
        py_file.write_text(new_text, encoding="utf-8")
        fixed += 1
        print(f"🩹 Fixed syntax pattern in: {py_file}")

print(f"\n✅ Cleanup complete — {fixed} file(s) modified.")
print("Now re-run: python scripts/auto_code_check_pro.py")
