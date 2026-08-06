# Million Challenge

> **New AI session or new device?** Read [`llms.txt`](./llms.txt) for full technical
> context, then [`HANDOFF.md`](./HANDOFF.md) for how to get access set up.

Automated daily repost of one reel to `@artificial_intellectual`'s "Million Followers Challenge",
incrementing the day count each successful post until the account hits 1M followers.

**This is a separate pipeline from `@the_higher_being` (which runs on Make.com) —
do not mix the two.**

## How it works
- `reel.mp4` — the master video (never posted directly)
- `scripts/post_reel.py` — each run renders `reel_day_N.mp4` from the master with a "DAY N" text overlay burned in via ffmpeg (this also avoids Instagram's duplicate-content detection, which started rejecting the identical file after ~9 uploads), commits it, creates the IG media container from that file's raw GitHub URL, polls until processed, publishes, updates the counter, then deletes the rendered file to keep the repo lean
- `day_counter.txt` — current day number, bumped only after a confirmed successful publish
- `.github/workflows/daily-reel.yml` — runs the script daily via GitHub Actions cron (also runnable manually via workflow_dispatch)
- `.github/workflows/token-expiry-check.yml` — emails a reminder when the Instagram token is ~10 days from expiring, then self-resets the countdown
- `scripts/notify_failure.py` + the "Email alert on failure" step — emails you automatically if a daily post run fails, with a link to the failed run

## Setup required
Add these as repo secrets (Settings → Secrets and variables → Actions):
- `IG_ACCESS_TOKEN` — long-lived Instagram Graph API access token for the target account
- `IG_BUSINESS_ACCOUNT_ID` — the Instagram Business Account ID to post from
- `GMAIL_ADDRESS` / `GMAIL_APP_PASSWORD` / `NOTIFY_EMAIL` (optional) — for token expiry and failure alert emails

Until the IG secrets are set, the workflow runs on schedule but exits early without posting or touching the counter.

## Important: keep this repo public
Instagram's servers fetch the video from `raw.githubusercontent.com`, which only serves files
from **public** repos to anonymous requests. If this repo is ever switched to private, every
post will fail with a container processing error until it's switched back.
