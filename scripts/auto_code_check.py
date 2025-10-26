import subprocess, time, os, sys
from pathlib import Path

WATCH_PATH = Path(__file__).resolve().parent.parent  # root folder
INTERVAL = 10  # seconds between checks

def run_cmd(cmd):
    """Run shell command and capture output"""
    print(f"\n🔍 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

def check_all():
    """Run multiple quality and error checks"""
    print("\n🧠 Auto Code Doctor — full project scan")
    run_cmd(["python", "-m", "py_compile", "app.py"])
    run_cmd(["flake8", str(WATCH_PATH / "leviathan"), "--max-line-length=100"])
    run_cmd(["pylint", str(WATCH_PATH / "leviathan")])
    run_cmd(["bandit", "-r", str(WATCH_PATH / "leviathan")])
    run_cmd(["mypy", str(WATCH_PATH / "leviathan")])

if __name__ == "__main__":
    print("🚀 Auto-checker started — watching for changes...")
    seen = {}
    while True:
        changed = False
        for pyfile in WATCH_PATH.rglob("*.py"):
            mtime = pyfile.stat().st_mtime
            if pyfile not in seen or seen[pyfile] != mtime:
                changed = True
                seen[pyfile] = mtime
        if changed:
            check_all()
        time.sleep(INTERVAL)
