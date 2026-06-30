---
description: Turn a meeting transcript into requirements, a Notion blueprint, GitHub issues, and code PRs — interactively, confirming at each step.
argument-hint: [meeting name or keywords]
---

You are running the **Meeting-to-Code pipeline** interactively for the user.
The user names a meeting; you find its transcript, confirm it with them, then
walk through the stages below. **Pause at every CHECKPOINT and wait for the
user's confirmation before continuing — never run the whole thing unattended.**

Meeting the user asked for: **$ARGUMENTS**

---

## Step 1 — Find the transcript

1. If `$ARGUMENTS` is empty, ask: "Which meeting should I process?" and wait.
2. Find the transcript using whatever connector is available, in this order:
   - `notion-query-meeting-notes` (if they use Notion AI Meeting Notes), then
   - `notion-search` with the meeting name — this also indexes connected
     **Google Drive**, Slack, etc., so it usually surfaces a Google Meet
     transcript Doc.
3. Show the top 1–3 matches with **title, date, source, and a short snippet**
   so the user can tell them apart.
4. If nothing good comes back, ask the user to point you at it directly — paste
   the text, a Google Drive link, or a Notion page URL.

> **CHECKPOINT 1:** "Is this the right meeting?" Wait for a clear yes before
> continuing. If they pick a different one, re-confirm.

---

## Step 2 — Extract requirements

1. Pull the full transcript text (`notion-fetch` the page, or read the Doc/text
   the user pointed you to).
2. Extract, as a structured summary:
   - **Problem statement**
   - **Features** requested
   - **Decisions** made
   - **Open questions**
   - **Non-goals**
   - **Constraints** (budget, timeline, tech)
   - **Acceptance criteria**
   - **Stakeholders**
3. Show the user a concise version of this.

> **CHECKPOINT 2:** "Did I capture this correctly?" Let them correct anything
> before you build on it.

---

## Step 3 — Blueprint → Notion (approval gate)

1. Generate a project blueprint in Markdown with: PRD (problem, goals,
   non-goals, success criteria), an **architecture diagram as a `mermaid`
   block**, database schema, API contracts, and tech-stack rationale.
2. Ask where it should live in Notion if it isn't obvious (look for a
   "Blueprints" database with `notion-search`; otherwise ask). Create the page
   with `notion-create-pages`, titled `{meeting name} - Blueprint`, with a
   **Status** of `Awaiting Review`.
3. Give the user the Notion link.

> **CHECKPOINT 3 (human approval gate):** Ask the user to review the blueprint
> in Notion and approve it. **Do not generate tickets or code until they say
> it's approved.** This is the most important checkpoint.

---

## Step 4 — Tickets → GitHub issues

1. Break the approved blueprint into GitHub issues: epics, user stories, tasks.
   Each with a title, body, **acceptance-criteria checklist**, a story-point
   estimate, and dependencies.
2. Show the proposed issue list (titles + estimates) as a quick table.

> **CHECKPOINT 4:** "Create these issues?" On yes, create each with the GitHub
> connector (`issue_write`), applying labels (`epic`/`story`/`task`,
> `estimate-N`).

---

## Step 5 — Code → pull requests

1. Ask which issues to implement now (default: the concrete `task` issues, not
   epics).
2. For each chosen issue:
   - Create a feature branch `feature/{issue-number}-{slug}`.
   - Generate clean, **tested** code (include unit tests).
   - Commit the files to the branch (`push_files` / `create_or_update_file`).
   - Open a **pull request** referencing the issue (`Closes #N`).
   - **Never auto-merge** — leave every PR for human review.
3. Summarize the PRs you opened with their links.

---

## Rules

- Pause at every **CHECKPOINT**; the user stays in control.
- Never merge a PR automatically.
- If a connector isn't available or a step fails, say so plainly and ask how to
  proceed — don't silently skip a stage.
- Keep each summary short and skimmable; the user is steering, not reading
  walls of text.
