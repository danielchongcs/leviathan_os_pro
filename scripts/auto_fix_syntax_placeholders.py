# scripts/auto_fix_syntax_placeholders.py
"""
Repairs bad placeholders like '\g<2>' that slipped into code and broke def lines.
Also patches empty parameter names like 'def f(: Any)' -> 'def f(x: Any)'.
Runs a syntax check on each edited file so you can see what's still broken.
"""

from __future__ import annotations
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "leviathan"

# --- regex helpers
BACKREF = re.compile(r"\\g<\d+>")  # e.g. \g<1>, \g<2>
EMPTY_PARAM = re.compile(r"(def\s+[A-Za-z_]\w*\(\s*):\s*Any(\s*[,\)])")  # def f(: Any) -> def f(x: Any)
LONE_COLON = re.compile(r"(def\s+[A-Za-z_]\w*\([^)]*),\s*:\s*Any")        # def f(a: int, : Any) -> insert name
OPEN_PAREN_COLON = re.compile(r"(def\s+[A-Za-z_]\w*\(\s*):(\s*)")         # def f(:  -> def f(x:
ANY_USED = re.compile(r"\bAny\b")

def ensure_import_any(text: str) -> str:
    """Add 'from typing import Any' if Any is used and not imported yet."""
    if "from typing import Any" in text:
        return text
    if ANY_USED.search(text):
        # put import after the first future- or std import if possible
        lines = text.splitlines()
        insert_at = 0
        for i, line in enumerate(lines[:20]):
            if line.startswith(("from __future__", "import", "from ")):
                insert_at = i + 1
        lines.insert(insert_at, "from typing import Any")
        return "\n".join(lines)
    return text

def fix_text(text: str) -> str:
    # 1) Replace bad backrefs with a safe name
    fixed = BACKREF.sub("param", text)

    # 2) Fix 'def f(: Any' -> 'def f(x: Any'
    fixed = EMPTY_PARAM.sub(r"\1x: Any\2", fixed)

    # 3) Fix 'def f(a, : Any' -> 'def f(a, x: Any'
    fixed = LONE_COLON.sub(r"\1, x: Any", fixed)

    # 4) Fix 'def f(:' (no type) -> 'def f(x:'
    fixed = OPEN_PAREN_COLON.sub(r"\1x:\2", fixed)

    # 5) If Any appears but not imported, add it
    fixed = ensure_import_any(fixed)

    return fixed

def py_ok(path: Path) -> bool:
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile", str(path)],
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0

def main() -> None:
    changed = 0
    failed = []

    for f in sorted(TARGET.rglob("*.py")):
        original = f.read_text(encoding="utf-8")
        patched = fix_text(original)
        if patched != original:
            f.write_text(patched, encoding="utf-8")
            if py_ok(f):
                print(f"🩹 Fixed & OK  → {f.relative_to(ROOT)}")
                changed += 1
            else:
                print(f"⚠️  Fixed but still syntax errors → {f.relative_to(ROOT)}")
                failed.append(f)

    print("\n========== Summary ==========")
    print(f"Edited files: {changed}")
    if failed:
        print("Still failing:")
        for f in failed:
            print(" -", f.relative_to(ROOT))
    else:
        print("All edited files compile ✅")

if __name__ == "__main__":
    main()
