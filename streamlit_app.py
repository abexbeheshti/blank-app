import json

import streamlit as st

from pipeline.config import load_config
from pipeline.runner import run_once
from pipeline.storage import Storage

st.set_page_config(page_title="Meeting-to-Code Pipeline", page_icon="🎈", layout="wide")
st.title("🎈 Meeting-to-Code Pipeline")
st.caption(
    "Transcript capture → requirements extraction → blueprint → human approval → "
    "tickets → generated code PRs."
)

config = load_config()
storage = Storage(config.data_dir)

with st.sidebar:
    st.header("Controls")
    if st.button("Run pipeline pass now", use_container_width=True):
        with st.spinner("Running a pipeline pass..."):
            try:
                summary = run_once(config)
                st.success(f"Done. New: {len(summary['new_transcripts'])}, "
                           f"advanced: {len(summary['advanced'])}, "
                           f"errors: {len(summary['errors'])}")
                if summary["errors"]:
                    st.json(summary["errors"])
            except Exception as exc:  # noqa: BLE001
                st.error(f"Run failed: {exc}")
    st.divider()
    st.caption(
        "Credentials are read from environment variables "
        "(see .env.example). Nothing is sent anywhere until the "
        "relevant API keys are configured."
    )

records = storage.all_records()

if not records:
    st.info(
        "No transcripts processed yet. Configure credentials and run a pass, "
        "or trigger scripts/run_pipeline.py --once."
    )
else:
    STAGE_ORDER = [
        "captured",
        "requirements_extracted",
        "blueprint_generated",
        "awaiting_approval",
        "approved",
        "issues_created",
        "code_generated",
        "failed",
    ]

    for transcript_id, record in sorted(
        records.items(), key=lambda kv: STAGE_ORDER.index(kv[1].get("status", "captured"))
        if kv[1].get("status") in STAGE_ORDER else 0,
        reverse=True,
    ):
        status = record.get("status", "unknown")
        meeting_name = record.get("meeting_name", transcript_id)
        icon = "🔴" if status == "failed" else ("✅" if status == "code_generated" else "🟡")

        with st.expander(f"{icon} {meeting_name} — *{status}*", expanded=False):
            st.write(f"**Transcript ID:** `{transcript_id}`")
            st.write(f"**Status:** `{status}`")

            if record.get("notion_page_url"):
                st.write(f"**Blueprint (Notion):** {record['notion_page_url']}")

            if record.get("github_issues"):
                st.write("**GitHub Issues:**")
                for issue in record["github_issues"]:
                    st.write(f"- [#{issue['number']}]({issue['url']}) {issue['title']}")

            if record.get("pull_requests"):
                st.write("**Generated PRs:**")
                for pr in record["pull_requests"]:
                    if pr.get("status") == "ok":
                        st.write(f"- [#{pr['pr']['number']}]({pr['pr']['url']}) (issue #{pr['issue_number']})")
                    else:
                        st.write(f"- ⚠️ issue #{pr.get('issue_number')} failed: {pr.get('error')}")

            if record.get("error"):
                st.error(record["error"])

            tabs = st.tabs(["Requirements", "Blueprint"])
            with tabs[0]:
                try:
                    st.json(storage.load_requirements(transcript_id))
                except FileNotFoundError:
                    st.caption("Not extracted yet.")
            with tabs[1]:
                try:
                    st.markdown(storage.load_blueprint(transcript_id))
                except FileNotFoundError:
                    st.caption("Not generated yet.")
