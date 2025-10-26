import os
import re
from pathlib import Path

# ✅ Where your real code lives
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "leviathan"

def add_docstrings_to_file(path: Path):
    """Read a .py file and insert simple docstrings into empty functions or classes."""
    text = path.read_text(encoding="utf-8")

    # Adds a one-line docstring to functions without one
    def replacer(match):
        name = match.group(1)
        return f"def {name}(\g<2>):\n    \"\"\"{name} function.\"\"\""

    # Adds docstrings for classes
    def class_replacer(match):
        name = match.group(1)
        return f"class {name}:\n    \"\"\"{name} class.\"\"\""

    new_text = re.sub(r"def\s+(\w+)\s*(\(.*?\))\s*:", replacer, text)
    new_text = re.sub(r"class\s+(\w+)\s*:", class_replacer, new_text)

    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        print(f"✅ Added docstrings to {path.name}")
    else:
        print(f"ℹ️ No changes needed in {path.name}")

def main():
    for py_file in SRC.rglob("*.py"):
        if "auto_add_docstrings" in str(py_file):
            continue
        add_docstrings_to_file(py_file)
    print("🎉 Done! Docstrings inserted automatically.")

if __name__ == "__main__":
    main()
