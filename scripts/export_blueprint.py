import json, datetime as dt
from pathlib import Path
from leviathan.utils import to_df as to_dataframe, hooks

def main():
    demo = json.loads(Path("data/demo_signals.json").read_text(encoding="utf-8"))
    df = to_dataframe(demo["signals"]).head(10)
    ts = dt.date.today().isoformat()
    out = Path("exports"); out.mkdir(exist_ok=True)

    df.to_csv(out / f"top10_{ts}.csv", index=False, encoding="utf-8")

    lines = [f"# Leviathan Weekly Blueprint — {ts}", ""]
    for i, row in df.iterrows():
        h = hooks(row['phrase'])
        lines += [
            f"## {i+1}. {row['phrase']} (score {row['score']})",
            f"- Domain: {row['domain']}",
            f"- Velocity: {row['velocity']} • Novelty: {row['novelty']} • Volume: {row['count']}",
            f"- **Ad**: {h['ad']}",
            f"- **Short Hook**: {h['short']}",
            f"- **Landing H1**: {h['h1']}",
            ""
        ]
    (out / f"blueprint_{ts}.md").write_text("\n".join(lines), encoding="utf-8")
    print("Saved in", out)

if __name__ == "__main__":
    main()
