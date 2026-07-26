# Million Challenge

Automated daily repost of one reel to `@the_higher_being`'s "Million Followers Challenge",
incrementing the day count each successful post until the account hits 1M followers.

## How it works
- `reel.mp4` — the fixed video, served via raw.githubusercontent.com as a stable public URL for the Graph API
- `day_counter.txt` — current day number, bumped only after a confirmed successful publish
- `scripts/post_reel.py` — creates the IG media container, polls until processed, publishes, updates the counter
- `.github/workflows/daily-reel.yml` — runs the script daily via GitHub Actions cron (also runnable manually via workflow_dispatch)

## Setup required
Add these as repo secrets (Settings → Secrets and variables → Actions):
- `IG_ACCESS_TOKEN` — long-lived Instagram Graph API access token for the target account
- `IG_BUSINESS_ACCOUNT_ID` — the Instagram Business Account ID to post from

Until both secrets are set, the workflow runs on schedule but exits early without posting or touching the counter.
