"""Run all quality checks (flake8, pylint, mypy, bandit) and print a color summary."""

import subprocess
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "exports" / "code_reports"
REPORTS.mkdir(parents=True, exist_ok=True)


def run_check(name: str, cmd: str) -> str:
    """Run a shell command and return its output."""
    print(f"\n🔍 Running {name} ...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT)
    if result.returncode == 0:
        print(f"✅ {name} passed")
    else:
        print(f"⚠️ {name} found issues")
    return f"# {name}\n```\n{result.stdout}{result.stderr}\n```\n"


def main():
    print("🚀 Leviathan Quality Check — running all tools...\n")

    sections = []
    sections.append(run_check("Flake8", "python -m flake8 leviathan"))
    sections.append(run_check("Pylint", "python -m pylint leviathan"))
    sections.append(run_check("Mypy", "python -m mypy leviathan"))
    sections.append(run_check("Bandit", "bandit -r leviathan"))

    # Save report
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    md_file = REPORTS / f"quality_report_{ts}.md"
    md_file.write_text("\n".join(sections), encoding="utf-8")

    print(f"\n📝 Report saved to: {md_file}")
    print("🏁 All checks complete!")


if __name__ == "__main__":
    main()

