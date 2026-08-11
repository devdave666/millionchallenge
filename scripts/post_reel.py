import os
import subprocess
import sys
import time
import requests

REPO_RAW_BASE = "https://raw.githubusercontent.com/devdave666/millionchallenge/main"
MASTER_VIDEO = "reel.mp4"
COUNTER_FILE = "day_counter.txt"
GRAPH_API_VERSION = "v21.0"
GRAPH_API_HOST = "graph.instagram.com"  # Instagram Login token path (not graph.facebook.com)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

CAPTION_TEMPLATE = """A Million Followers Challenge \U0001F3AF

Day {day} of posting this same reel \u2014 every single day \u2014 until we hit 1 million followers.

No new content. No shortcuts. Just showing up, one day at a time.

If this reached you today, you're part of Day {day}. \U0001FAE1

#MillionFollowerChallenge #ShowUpDaily #Consistency #DisciplineOverMotivation #GrowthMindset #ThePowerOfShowingUp #TheHigherBeing #DailyReminder"""


def get_day_number():
    with open(COUNTER_FILE) as f:
        return int(f.read().strip())


def set_day_number(n):
    with open(COUNTER_FILE, "w") as f:
        f.write(str(n))


def render_day_video(day):
    output_path = f"reel_day_{day}.mp4"
    drawtext = (
        f"drawtext=fontfile={FONT_PATH}:text='DAY {day}':"
        f"fontcolor=white:fontsize=90:box=1:boxcolor=black@0.55:boxborderw=25:"
        f"x=(w-text_w)/2:y=160"
    )
    cmd = [
        "ffmpeg", "-y", "-i", MASTER_VIDEO,
        "-vf", drawtext,
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-crf", "20", "-preset", "medium",
        "-c:a", "copy",
        "-movflags", "+faststart",
        output_path,
    ]
    subprocess.run(cmd, check=True)
    return output_path


def git_commit_push(add_paths, remove_paths, message, max_retries=5):
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
    if remove_paths:
        subprocess.run(["git", "rm", "-f", *remove_paths], check=False)
    if add_paths:
        subprocess.run(["git", "add", *add_paths], check=True)
    diff = subprocess.run(["git", "diff", "--staged", "--quiet"])
    if diff.returncode == 0:
        return False

    subprocess.run(["git", "commit", "-m", message], check=True)

    # The remote can move between checkout and push (a rerun of this same
    # workflow, or another workflow committing to main), which makes a plain
    # `git push` fail with a non-fast-forward rejection. Rebase onto the
    # latest remote main and retry instead of letting that crash the run.
    for attempt in range(max_retries):
        push = subprocess.run(["git", "push"])
        if push.returncode == 0:
            return True
        print(f"git push rejected (attempt {attempt + 1}/{max_retries}), fetching and rebasing before retry")
        subprocess.run(["git", "fetch", "origin", "main"], check=True)
        subprocess.run(["git", "rebase", "origin/main"], check=True)

    raise RuntimeError(f"git push failed after {max_retries} rebase-and-retry attempts")


def main():
    access_token = os.environ.get("IG_ACCESS_TOKEN")
    ig_user_id = os.environ.get("IG_BUSINESS_ACCOUNT_ID")

    if not access_token or not ig_user_id:
        print("IG_ACCESS_TOKEN or IG_BUSINESS_ACCOUNT_ID secret not set yet - skipping post, counter left untouched.")
        sys.exit(0)

    day = get_day_number()
    caption = CAPTION_TEMPLATE.format(day=day)

    rendered_filename = render_day_video(day)
    video_url = f"{REPO_RAW_BASE}/{rendered_filename}"
    print(f"Rendered {rendered_filename}, publishing from {video_url}")

    git_commit_push([rendered_filename], [], f"Add rendered reel for Day {day}")

    # Give GitHub's raw CDN a moment to pick up the new file before Instagram fetches it.
    time.sleep(25)

    base = f"https://{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_user_id}"

    resp = requests.post(f"{base}/media", data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": access_token,
    })
    resp.raise_for_status()
    creation_id = resp.json()["id"]
    print(f"Created container {creation_id} for Day {day}")

    status_url = f"https://{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{creation_id}"
    for attempt in range(30):
        status_resp = requests.get(status_url, params={
            "fields": "status_code",
            "access_token": access_token,
        })
        status_resp.raise_for_status()
        status_code = status_resp.json().get("status_code")
        print(f"Status check {attempt + 1}: {status_code}")
        if status_code == "FINISHED":
            break
        if status_code == "ERROR":
            raise RuntimeError(f"Container processing failed: {status_resp.json()}")
        time.sleep(10)
    else:
        raise TimeoutError("Video container never finished processing in time")

    publish_resp = requests.post(f"{base}/media_publish", data={
        "creation_id": creation_id,
        "access_token": access_token,
    })
    publish_resp.raise_for_status()
    print(f"Published Day {day}: {publish_resp.json()}")

    set_day_number(day + 1)
    print(f"Counter incremented to {day + 1}")

    # Clean up the rendered file now that Instagram has already fetched and processed it,
    # to keep the repo lean.
    git_commit_push([COUNTER_FILE], [rendered_filename], f"Day {day} posted - bump counter, clean up rendered file")


if __name__ == "__main__":
    main()
