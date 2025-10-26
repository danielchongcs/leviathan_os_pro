# scripts/dangerous_pattern_scanner.py
import re
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "leviathan"

PATTERNS = {
    r"\beval\s*\(": "use of eval() - dangerous, prefer ast.literal_eval or explicit parsing",
    r"\bexec\s*\(": "use of exec() - dangerous, avoid",
    r"os\.system\(": "os.system call - use subprocess with list args instead",
    r"subprocess\.Popen\(": "subprocess.Popen - ensure shell=False and pass list args",
    r"subprocess\.run\([^\)]*shell\s*=\s*True": "subprocess.run(..., shell=True) - avoid shell=True",
    r"open\([^\)]*(\"w\"|'w'|\"wb\"|'wb')": "writing to files - ensure safe paths and use tempfile for untrusted input",
    r"[A-Za-z0-9\-_]{40,}": "possible API key / long token (40+ chars) - check if secret",
    r"password\s*[:=]": "possible hardcoded password",
    r"SECRET_|API_KEY|AWS_SECRET|TOKEN": "likely secret-ish variable name",
}

def scan_file(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    findings = []
    for pat, reason in PATTERNS.items():
        for m in re.finditer(pat, text):
            start = max(0, m.start()-40)
            snippet = text[start:m.end()+40].replace("\n", " ")
            findings.append({
                "pattern": pat,
                "reason": reason,
                "file": str(path.relative_to(ROOT)),
                "line_no": text.count("\n", 0, m.start()) + 1,
                "snippet": snippet[:300],
            })
    return findings

def main():
    out = []
    for py in SRC.rglob("*.py"):
        if "venv" in str(py).lower() or "site-packages" in str(py).lower():
            continue
        out += scan_file(py)

    report = ROOT / "exports" / "code_reports" / "danger_findings.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Scanned {len(list(SRC.rglob('*.py')))} python files")
    print(f"Findings saved -> {report}")
    for f in out:
        print(f"{f['file']}:{f['line_no']}  - {f['reason']}\n  → {f['snippet']}\n")

if __name__ == "__main__":
    main()
