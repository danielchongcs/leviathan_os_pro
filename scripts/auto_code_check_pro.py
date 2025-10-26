# scripts/auto_code_check_pro.py
# ✅ Hardened & Upgraded: safe subprocess, scoreboard, auto-open HTML, danger scan

import subprocess
import time
import os
import datetime
import difflib
import pathlib
import shutil
import sys
from typing import Dict, Tuple

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "exports" / "code_reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

LEVIATHAN_DIR = ROOT / "leviathan"

# --- Helpers -----------------------------------------------------------------

def _tool(name: str) -> str:
    """Return the full path to a tool if available, else just the name (it may still work)."""
    return shutil.which(name) or name

def run_cmd(args: list[str], timeout: int = 180) -> str:
    """
    Run a command safely (no shell=True), capture output, return stdout+stderr.
    Sanitizes env to avoid leaking secrets to child processes.
    """
    print(f"🔍 Running: {' '.join(args)}")
    try:
        # minimal env – only what we really need
        safe_env = {"PYTHONIOENCODING": "utf-8"}
        # preserve PATH and VIRTUAL_ENV so venv tools work
        for k in ("PATH", "VIRTUAL_ENV", "SYSTEMROOT", "WINDIR"):
            if k in os.environ:
                safe_env[k] = os.environ[k]

        proc = subprocess.run(
            args,
            cwd=ROOT,
            env=safe_env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        return f"[TIMEOUT] {' '.join(args)} exceeded {timeout}s"
    except Exception as e:
        return f"[ERROR] {' '.join(args)} failed: {e}"

def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def write_report(markdown_body: str) -> Tuple[pathlib.Path, pathlib.Path]:
    """Write markdown + html versions with timestamp and return their paths."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    md_path = REPORT_DIR / f"report_{ts}.md"
    html_path = REPORT_DIR / f"report_{ts}.html"

    md_path.write_text(markdown_body, encoding="utf-8")

    html_body = (
        "<html><head><meta charset='utf-8'><title>Auto Code Report</title>"
        "<style>"
        "body{font-family:Consolas,monospace;background:#111;color:#eee;padding:2em}"
        "pre{white-space:pre-wrap;word-wrap:break-word}"
        ".score{font-size:18px;margin-bottom:16px;padding:12px;border-radius:8px;background:#1b1b1b}"
        ".pill{display:inline-block;margin-right:10px;padding:6px 10px;border-radius:999px;background:#222}"
        ".ok{color:#87d37c}.warn{color:#f9ca24}.bad{color:#ff6b6b}"
        "</style></head><body><pre>"
        + html_escape(markdown_body)
        + "</pre></body></html>"
    )
    html_path.write_text(html_body, encoding="utf-8")
    print(f"✅ Saved report → {md_path.name} / {html_path.name}")
    return md_path, html_path

# --- Parsing / Scoreboard ----------------------------------------------------

def parse_flake8(out: str) -> int:
    """
    Count flake8 issues by non-empty lines that look like 'path:line:col: CODE ...'.
    If flake8 isn't installed or directory missing, count = 0 and the raw output will explain.
    """
    count = 0
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        # crude heuristic: Windows paths often start with drive letters or absolute paths
        if ":" in line and " " in line:
            # e.g. C:\...\file.py:12:8: E501 message
            parts = line.split(" ", 1)
            if parts and ":" in parts[0]:
                count += 1
    return count

def parse_pylint_score(out: str) -> float:
    """
    Look for: 'Your code has been rated at X.XX/10'
    If not found, return 0.0 (tool may be missing or crashed).
    """
    for line in out.splitlines():
        if "Your code has been rated at" in line and "/10" in line:
            try:
                left = line.split("at", 1)[1].strip()
                score_str = left.split("/10", 1)[0].strip()
                return float(score_str)
            except Exception:
                pass
    return 0.0

def parse_bandit_counts(out: str) -> Tuple[int, int, int]:
    """
    Parse Bandit 'Total issues (by severity): High/Medium/Low'.
    Return (high, medium, low).
    """
    high = med = low = 0
    for line in out.splitlines():
        ls = line.strip().lower()
        if ls.startswith("total issues (by severity):"):
            # the next few lines should contain the counts
            continue
        if ls.startswith("high:"):
            try: high = int(ls.split(":")[1].strip())
            except: pass
        if ls.startswith("medium:"):
            try: med = int(ls.split(":")[1].strip())
            except: pass
        if ls.startswith("low:"):
            try: low = int(ls.split(":")[1].strip())
            except: pass
    return high, med, low

def parse_mypy_errors(out: str) -> int:
    """
    Count lines that look like mypy error lines: 'path:line: error: ...'
    """
    count = 0
    for line in out.splitlines():
        if ": error:" in line:
            count += 1
    return count

def build_scoreboard(pylint_out: str, flake8_out: str, bandit_out: str, mypy_out: str) -> str:
    pylint_score = parse_pylint_score(pylint_out)
    flake_issues = parse_flake8(flake8_out)
    b_high, b_med, b_low = parse_bandit_counts(bandit_out)
    mypy_errs = parse_mypy_errors(mypy_out)

    def pill(label: str, value: str, cls: str) -> str:
        return f"{label}: {value}"

    # Simple color classes in HTML replaced later; keep plain in MD
    board_lines = [
        "📊 CODE SUMMARY",
        "──────────────────────────────",
        f"✅ Pylint Score: {pylint_score:.2f}/10",
        f"⚠️ Flake8 Issues: {flake_issues}",
        f"🔒 Bandit Findings: {b_high} High, {b_med} Medium, {b_low} Low",
        f"🔍 Mypy Errors: {mypy_errs}",
        "",
    ]
    return "\n".join(board_lines)

# --- Main --------------------------------------------------------------------

def main():
    print("🚀 Auto-Code-Check PRO (Hardened) …")

    # 0) Quick security scan for dangerous patterns (non-fatal)
    danger_scan = run_cmd([_tool("python"), "scripts/dangerous_pattern_scanner.py"])

    # 1) Syntax check (app.py may be missing; that's fine, we report it)
    syntax_out = run_cmd([_tool("python"), "-m", "py_compile", "app.py"])

    # 2) Flake8 style
    flake8_out = run_cmd([_tool("flake8"), str(LEVIATHAN_DIR), "--max-line-length=100"])

    # 3) Pylint
    pylint_out = run_cmd([_tool("pylint"), str(LEVIATHAN_DIR)])

    # 4) Bandit (security)
    bandit_out = run_cmd([_tool("bandit"), "-r", str(LEVIATHAN_DIR)])

    # 5) Mypy (typing)
    mypy_out = run_cmd([_tool("mypy"), str(LEVIATHAN_DIR)])

    # Build scoreboard (top)
    scoreboard = build_scoreboard(pylint_out, flake8_out, bandit_out, mypy_out)

    # Combine to markdown sections
    sections: Dict[str, str] = {
        "Security Pre-Scan (dangerous patterns)": danger_scan,
        "Syntax Check": syntax_out,
        "Flake8 Style": flake8_out,
        "Pylint Logic": pylint_out,
        "Bandit Security": bandit_out,
        "Mypy Typing": mypy_out,
    }

    md = "📊 CODE SUMMARY\n──────────────────────────────\n" + scoreboard + "\n"
    md += f"# 🧠 Leviathan Auto Code Report ({datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')})\n\n"

    for name, out in sections.items():
        md += f"### 🔹 {name}\n\n{out.strip() or '(no output)'}\n\n\n"

    # Compare with previous report if any (ignore the one we are writing now)
    prev_files = sorted(REPORT_DIR.glob("report_*.md"))
    prev_text = ""
    if len(prev_files) >= 1:
        # Last completed report is the last one in this list
        prev_text = prev_files[-1].read_text(encoding="utf-8") if prev_files else ""

    if prev_text:
        diff = difflib.unified_diff(prev_text.splitlines(), md.splitlines(), n=3)
        diff_text = "\n".join(diff)
        if diff_text.strip():
            md += "### 🔹 Changes Since Last Report\n\n" + diff_text + "\n\n"
        else:
            md += "### 🔹 Changes Since Last Report\n\nNo changes detected.\n\n"
    else:
        md += "### 🔹 Changes Since Last Report\n\n(n/a – first run or no prior report found)\n\n"

    md_path, html_path = write_report(md)

    # Auto-open HTML report on Windows
    try:
        if os.name == "nt":
            os.startfile(html_path)  # type: ignore[attr-defined]
    except Exception as e:
        print("ℹ️ Could not auto-open HTML:", e)

    # Optional sound notification (Windows)
    try:
        import winsound  # only on Windows
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception:
        pass

    print("🏁 Analysis complete — reports saved in /exports/code_reports")

if __name__ == "__main__":
    main()
