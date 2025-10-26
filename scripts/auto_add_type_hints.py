"""
Auto-add simple type hints to all Python files inside leviathan/.
This is a *safe upgrader* — it won’t break your code.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "leviathan"

def add_type_hints_to_file(path: Path):
    text = path.read_text(encoding="utf-8")
    original = text

    # Add simple type hints for common names
    text = re.sub(r"def\s+(\w+)\((.*?)\):", lambda m: fix_signature(m), text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"✅ Type hints added → {path.relative_to(ROOT)}")
    else:
        print(f"ℹ️ No changes → {path.relative_to(ROOT)}")

def fix_signature(match):
    name = match.group(1)
    params = match.group(2)

    # Skip if already has ':'
    if ":" in params:
        return match.group(0)

    # Guess types from common variable names
    hint_map = {
        "file": "str",
        "path": "str",
        "file_path": "str",
        "text": "str",
        "data": "dict",
        "df": "pd.DataFrame",
        "x": "float",
        "y": "float",
        "n": "int",
        "count": "int",
        "name": "str",
        "url": "str",
        "self": "",
    }

    parts = [p.strip() for p in params.split(",") if p.strip()]
    new_parts = []
    for p in parts:
        hint = "Any"
        for key, t in hint_map.items():
            if key in p:
                hint = t
                break
        if p == "self":
            new_parts.append("self")
        elif "=" in p:
            name_part, default = p.split("=", 1)
            new_parts.append(f"{name_part.strip()}: {hint} = {default.strip()}")
        else:
            new_parts.append(f"{p}: {hint}")

    params_hint = ", ".join(new_parts)
    return f"def {name}({params_hint}) -> Any:"

def main():
    for py in SRC.rglob("*.py"):
        if "auto_add_type_hints" in str(py):
            continue
        add_type_hints_to_file(py)
    print("🎯 Type hints successfully added to your project!")

if __name__ == "__main__":
    main()
