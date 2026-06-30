# 🎈 Meeting-to-Code Pipeline

Converts Google Meet transcripts into requirements, a reviewable project
blueprint, GitHub tickets, and generated pull requests.

```
Google Meet (transcript)
  → Google Drive (auto-save)
    → Polling (pipeline/stages/stage1_capture.py)
      → Claude (extraction & blueprint generation)
        → Notion (blueprint doc, human approval gate)
          → GitHub (tickets, then generated code PRs)
```

A human approves the blueprint in Notion before tickets or code are
generated — nothing downstream of Stage 3 runs automatically.

## Two ways to run it

**1. One-click, interactive (easiest — recommended).** In Claude Code, just name
the meeting:

```
/meeting-to-code Q3 Planning
```

Claude finds the transcript, **confirms it with you**, then walks each stage —
extract → blueprint (written to Notion) → your approval → GitHub issues → code
PRs — pausing for your OK at every checkpoint. It uses your connected
**GitHub** and **Notion** logins, so there are no tokens to manage. The command
lives in `.claude/commands/meeting-to-code.md`.

**2. Automated background pipeline.** The Python package below runs the same
stages unattended on a schedule (polls Google Drive, advances each transcript
through a state machine). More setup, but fully hands-off. Details follow.

## Setup

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in credentials (Google service
   account, Anthropic auth, Notion token, GitHub token). See
   `.env.example` for what each one is used for.

### LLM backend (uses your Claude subscription by default)

By default (`LLM_BACKEND=claude_code`) the pipeline drives the **Claude Code
CLI**, which runs on your Claude **Pro/Max subscription** — no separate API
bill. One-time setup:

```
claude setup-token                 # prints a long-lived OAuth token
```

Put the token in `.env` as `CLAUDE_CODE_OAUTH_TOKEN=...` and leave
`ANTHROPIC_API_KEY` **unset** (if it's set, Claude Code uses it and bills as
API usage instead). That's it.

This draws on your subscription's rate limits (rolling multi-hour window +
weekly cap) rather than pay-as-you-go, so a heavy burst of meetings can
throttle.

Prefer pay-per-token instead? Set `LLM_BACKEND=api` and provide
`ANTHROPIC_API_KEY`.

## Running

**Dashboard** (view pipeline status, trigger a manual pass):

```
streamlit run streamlit_app.py
```

**One-shot pass** (for cron/systemd timers or testing):

```
python scripts/run_pipeline.py --once
```

**Continuous polling loop**:

```
python scripts/run_pipeline.py
```

**Cloud Function** (triggered by Cloud Scheduler — see
`scripts/poll_transcripts_function.py` for deploy commands).

## How it works

Each transcript moves through a state machine tracked in
`data/processed.json` (see `pipeline/runner.py`):

`captured → requirements_extracted → blueprint_generated → awaiting_approval → approved → issues_created → code_generated`

Every pass of `run_once()` re-checks every transcript and advances it one
step if it can — it's safe to run on a timer and safe to re-run after a
crash, since each stage is idempotent and keyed off the recorded status.

| Stage | Module | Model | Output |
|---|---|---|---|
| 1. Capture | `pipeline/stages/stage1_capture.py` | — | Transcript saved locally |
| 2. Extract requirements | `pipeline/stages/stage2_extract.py` | Haiku (cost) | Requirements JSON |
| 3. Blueprint + approval gate | `pipeline/stages/stage3_blueprint.py` | Sonnet (quality) | Notion page, awaits human approval |
| 4. Tickets | `pipeline/stages/stage4_tickets.py` | Haiku | GitHub issues |
| 5. Code generation | `pipeline/stages/stage5_codegen.py` | Opus (reasoning) | Draft PRs, never auto-merged |

## Tests

```
pytest
```

Tests cover storage, JSON-extraction parsing, and the requirements-extraction
stage with the Anthropic client mocked out — no live API calls or
credentials needed to run them.

## Security & privacy

- No data is sent anywhere until the relevant API keys are set.
- Local artifacts (`data/`) and credentials (`.env`, service account JSON)
  are gitignored.
- Generated code is always opened as a pull request for human review — the
  pipeline never merges automatically.
