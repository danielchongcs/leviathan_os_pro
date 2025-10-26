# scripts/summarize_fuzz.py
import json
import sys
from collections import Counter
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python scripts/summarize_fuzz.py exports/fuzz_logs/results.json")
    sys.exit(1)

p = Path(sys.argv[1])
if not p.exists():
    print("File not found:", p)
    sys.exit(1)

data = json.loads(p.read_text(encoding="utf-8"))
total = len(data)
errors = []
nonzero = []
rcs = Counter()
stderrs = Counter()

for entry in data:
    if entry.get("error"):
        errors.append(entry["error"])
    rc = entry.get("rc")
    if rc not in (0, None):
        nonzero.append(entry)
    if "stderr" in entry and entry["stderr"]:
        stderrs.update([entry["stderr"].strip()[:300]])

    if rc is not None:
        rcs.update([rc])

summary = {
    "total_runs": total,
    "num_errors_field": len(errors),
    "num_nonzero_rc": len(nonzero),
    "return_code_counts": dict(rcs),
    "top_10_stderr_samples": stderrs.most_common(10),
}

outp = p.parent / "summary_results.json"
outp.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("Saved summary →", outp)
print(" - total runs:", total)
print(" - entries with 'error' field:", len(errors))
print(" - entries with non-zero return code:", len(nonzero))
print(" - summary file:", outp)
