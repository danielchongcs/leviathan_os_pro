import os, json
from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from leviathan.utils import safe_read_json, to_df, hooks, expand_keywords
from leviathan.processors.trends import velocity, novelty
from leviathan.processors.cluster import cluster_phrases
from leviathan.ingestors.google_trends import fetch as fetch_trends
from leviathan.ingestors.youtube import search as yt_search
from leviathan.ingestors.reddit import pull as rd_pull

st.set_page_config(page_title="Leviathan OS — Pro", layout="wide")
st.title("🧠 Leviathan OS — Pro")
st.caption("Demo Mode works without keys. Add keys in .env for live data.")

# Read .env manually (simple)
env = {}
if Path('.env').exists():
    for line in Path('.env').read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.strip().startswith('#'):
            k,v = line.split('=',1); env[k.strip()] = v.strip()

yt_key = env.get("YOUTUBE_API_KEY","")
rd_id = env.get("REDDIT_CLIENT_ID","")
rd_secret = env.get("REDDIT_CLIENT_SECRET","")
rd_agent = env.get("REDDIT_USER_AGENT","")

# Start with demo signals
demo = json.loads(Path("data/demo_signals.json").read_text(encoding="utf-8"))
signals = demo["signals"][:]

with st.sidebar:
    st.subheader("Keyword Tools")
    kw_seed = st.text_input("Seed keyword for expansion", value="mini warehouse")
    if st.button("Expand"):
        st.session_state['expanded_keywords'] = expand_keywords(kw_seed)
    if 'expanded_keywords' in st.session_state:
        st.write("**Expanded:**")
        st.write("\n".join(f"- {k}" for k in st.session_state['expanded_keywords']))

    st.markdown("---")
    st.subheader("Data Sources")
    kw_text = st.text_area("Track keywords (comma-separated)", value="mini warehouse singapore, co living near NUS, ai agent lease management, ozone car odor, typeform alternative, virtual mailbox singapore", height=100)
    if st.button("Fetch Google Trends"):
        kws = [k.strip() for k in kw_text.split(",") if k.strip()]
        tr = fetch_trends(kws)
        for k, v in tr.items():
            series = v.get("series", [])
            vel = velocity(series)
            nov = novelty(k, [s["phrase"] for s in signals])
            signals.append({"phrase": k, "count": sum(series[-3:]), "velocity": vel, "novelty": nov, "domain": "trend", "examples": []})
        st.success("Google Trends fetched.")

    st.markdown("---")
    yt_q = st.text_input("YouTube query", value="singapore property rental")
    if st.button("Fetch YouTube"):
        vids = yt_search(yt_key, yt_q, 12)
        for v in vids:
            phrase = (v.get("title") or "")[:90]
            signals.append({"phrase": phrase, "count": 30, "velocity": 0.3, "novelty": 0.6, "domain": "youtube", "examples": [v.get("channel",""), v.get("published_at","")]})
        st.success("YouTube results added.")

    st.markdown("---")
    subs = st.text_input("Reddit subs", value="singapore, EntrepreneurRideAlong")
    if st.button("Fetch Reddit"):
        posts = rd_pull(rd_id, rd_secret, rd_agent, [s.strip() for s in subs.split(",") if s.strip()], 40)
        for p in posts:
            phrase = (p.get("title") or "")[:90]
            signals.append({"phrase": phrase, "count": p.get("score",0), "velocity": 0.25, "novelty": 0.6, "domain": p.get("subreddit","reddit"), "examples": [p.get("num_comments",0)]})
        st.success("Reddit posts added.")

df = to_df(signals)

st.subheader("Top Opportunities (Auto-Scored)")
st.dataframe(df.head(30), use_container_width=True)

# Charts: velocity bar + novelty heatmap (Top 10)
col1, col2 = st.columns(2)
top = df.head(10)

with col1:
    st.markdown("### Trend Velocity (Top 10)")
    fig, ax = plt.subplots()
    ax.bar(top["phrase"], top["velocity"])
    ax.set_xticklabels(top["phrase"], rotation=60, ha="right")
    ax.set_ylabel("Velocity"); ax.set_xlabel("Phrase")
    st.pyplot(fig)

with col2:
    st.markdown("### Novelty Heatmap (Top 10)")
    mat = top[["velocity","novelty"]].to_numpy()
    fig2, ax2 = plt.subplots()
    ax2.imshow(mat, aspect="auto")
    ax2.set_yticks(range(len(top))); ax2.set_yticklabels(range(1, len(top)+1))
    ax2.set_xticks([0,1]); ax2.set_xticklabels(["Velocity","Novelty"])
    ax2.set_title("Higher = Hotter")
    st.pyplot(fig2)

st.markdown("---")
st.subheader("Topic Clusters")
labels, top_terms = cluster_phrases(df["phrase"].tolist(), k=5 if len(df)>=5 else len(df))
if labels:
    dfc = df.copy(); dfc["cluster"] = labels
    for i in sorted(dfc["cluster"].unique()):
        sub = dfc[dfc["cluster"]==i].head(8)
        st.markdown(f"**Cluster {i}** — top terms: `{', '.join(top_terms[i])}`")
        st.table(sub[["phrase","score","velocity","novelty","domain"]])

st.subheader("Execution Playbook (Selected)")
idx = st.number_input("Row index", min_value=0, max_value=max(0,len(df)-1), value=0, step=1)
row = df.iloc[int(idx)]
h = hooks(row["phrase"])
st.code(f"""Ad: {h['ad']}
Short: {h['short']}
Landing H1: {h['h1']}""", language="markdown")

st.markdown("### Experiment Tracker")
log_path = Path("exports/experiments.csv")
if not log_path.exists():
    log_path.write_text("date,phrase,spend,clicks,leads,notes\n", encoding="utf-8")
with st.form("exp"):
    spend = st.text_input("Ad spend", value="0")
    clicks = st.text_input("Clicks", value="0")
    leads = st.text_input("Leads", value="0")
    notes = st.text_input("Notes", value="")
    if st.form_submit_button("Log Result"):
        from datetime import date
        line = f"{date.today().isoformat()},{row['phrase']},{spend},{clicks},{leads},{notes}\n"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)
        st.success("Logged. See exports/experiments.csv")

st.markdown("---")
st.markdown("### Save/Load Session")
if st.button("Save Top 50 → exports/session.json"):
    Path("exports/session.json").write_text(json.dumps({"signals": df.head(50).to_dict(orient="records")}, indent=2), encoding="utf-8")
    st.success("Saved.")
up = st.file_uploader("Load a session.json", type=["json"])
if up is not None:
    loaded = json.load(up)
    st.write("Loaded", len(loaded.get("signals", [])), "items. Preview:")
    st.dataframe(pd.DataFrame(loaded["signals"]).head(10), use_container_width=True)

if st.button("Export Weekly Blueprint"):
    import subprocess, sys
    code = subprocess.call([sys.executable, "scripts/export_blueprint.py"])
    if code == 0:
        st.success("Done. Check the exports/ folder.")
    else:
        st.error("Exporter failed.")

st.caption("Run `python scripts/export_blueprint.py` to generate Markdown + CSV without opening the UI.")
