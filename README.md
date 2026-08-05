# Million Challenge

Automated daily repost of one reel to `@the_higher_being`'s "Million Followers Challenge",
incrementing the day count each successful post until the account hits 1M followers.

## How it works
- `reel.mp4` — the master video (never posted directly)
- `scripts/post_reel.py` — each run renders `reel_day_N.mp4` from the master with a "DAY N" text overlay burned in via ffmpeg (this also avoids Instagram's duplicate-content detection, which started rejecting the identical file after ~9 uploads), commits it, creates the IG media container from that file's raw GitHub URL, polls until processed, publishes, updates the counter, then deletes the rendered file to keep the repo lean
- `day_counter.txt` — current day number, bumped only after a confirmed successful publish
- `.github/workflows/daily-reel.yml` — runs the script daily via GitHub Actions cron (also runnable manually via workflow_dispatch)

## Setup required
Add these as repo secrets (Settings → Secrets and variables → Actions):
- `IG_ACCESS_TOKEN` — long-lived Instagram Graph API access token for the target account
- `IG_BUSINESS_ACCOUNT_ID` — the Instagram Business Account ID to post from

Until both secrets are set, the workflow runs on schedule but exits early without posting or touching the counter.

## Important: keep this repo public
Instagram's servers fetch the video from `raw.githubusercontent.com`, which only serves files
from **public** repos to anonymous requests. If this repo is ever switched to private, every
post will fail with a container processing error until it's switched back.
