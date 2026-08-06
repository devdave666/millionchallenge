# Starting a new AI session on this project? Read this.

This repo runs a fully automated daily Instagram Reel posting pipeline for the
**Million Followers Challenge** (`@artificial_intellectual`). If you're picking this
up in a new chat, on a different device, or with a different AI model, here's
exactly what to hand over.

---

## 1. Give the new AI this repo

Just share the URL:

```
https://github.com/devdave666/millionchallenge
```

Tell it to read **`llms.txt`** at the repo root first — that file has the full
technical context (what the pipeline does, known gotchas, why certain design
choices were made). Then point it at this file for the access/setup steps below.

**Good opening message to a new AI session:**

> I have an existing automation in github.com/devdave666/millionchallenge for an
> Instagram "Million Followers Challenge" posting the same reel daily with an
> incrementing day counter. Read llms.txt and HANDOFF.md in that repo first, then
> help me with [whatever you need].

---

## 2. Giving the AI actual access (to push code, fix bugs, trigger runs)

The AI needs a **GitHub Fine-Grained Personal Access Token**, scoped to this repo
only. Generate one at:

`github.com/settings/personal-access-tokens/new`

- Repository access: **Only select repositories** → `devdave666/millionchallenge`
- Permissions needed:
  - **Contents: Read and write** (to push code/rendered files)
  - **Actions: Read and write** (to trigger/check workflow runs)
  - **Secrets: Read and write** (only if you want the AI to set repo secrets
    directly — otherwise you can add secrets yourself and skip this one)

Paste the generated token into the chat. The AI can use it to clone, push, and
manage the repo directly.

**Security note:** these tokens are sensitive. It's fine to paste one into a chat
with a trusted AI to get work done, but regenerate/revoke it afterward from
`github.com/settings/tokens` if you're done with that session, especially if
you're not planning to reuse the same token later.

---

## 3. What's already running (no action needed unless something's broken)

- **Daily reel post** — 9am ET every day, fully automatic
- **Token expiry reminder** — emails you when the Instagram token needs rotating,
  with exact steps, and self-resets the countdown
- **Failure alerts** — emails you automatically if a daily post fails, with a
  link to the failed run

You should only need to open a new AI chat about this repo when:
- You get a failure or expiry email and want help acting on it
- You want to change something about the pipeline (cadence, caption, hashtags,
  which account it posts to, etc.)
- Something's genuinely broken and the automated alert didn't fire

---

## 4. Quick status check for a new AI to run immediately

Once it has a token, a good first move for any new AI session is to check recent
run history to see current state before touching anything:

```
GET https://api.github.com/repos/devdave666/millionchallenge/actions/workflows/daily-reel.yml/runs?per_page=5
```

and read `day_counter.txt` in the repo to confirm what day the challenge is
currently on.
