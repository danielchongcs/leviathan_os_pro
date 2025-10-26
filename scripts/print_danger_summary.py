# scripts/print_danger_summary.py
import json
from pathlib import Path

p = Path("exports/code_reports/danger_findings.json")
if not p.exists():
    print("No findings file yet. Run: python scripts/dangerous_pattern_scanner.py")
    raise SystemExit(1)

data = json.loads(p.read_text(encoding="utf-8"))
print(f"Total findings: {len(data)}")
print("Top 20:")
for i, f in enumerate(data[:20], 1):
    snippet = (f.get("snippet") or "").replace("\n", " ")[:200]
    print(f"{i}. {f['file']}:{f['line_no']} — {f['reason']}")
    print("   ->", snippet)
