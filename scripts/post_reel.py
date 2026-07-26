import os
import sys
import time
import requests

REPO_RAW_VIDEO_URL = "https://raw.githubusercontent.com/devdave666/millionchallenge/main/reel.mp4"
COUNTER_FILE = "day_counter.txt"
GRAPH_API_VERSION = "v21.0"

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


def main():
    access_token = os.environ.get("IG_ACCESS_TOKEN")
    ig_user_id = os.environ.get("IG_BUSINESS_ACCOUNT_ID")

    if not access_token or not ig_user_id:
        print("IG_ACCESS_TOKEN or IG_BUSINESS_ACCOUNT_ID secret not set yet - skipping post, counter left untouched.")
        sys.exit(0)

    day = get_day_number()
    caption = CAPTION_TEMPLATE.format(day=day)
    base = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{ig_user_id}"

    resp = requests.post(f"{base}/media", data={
        "media_type": "REELS",
        "video_url": REPO_RAW_VIDEO_URL,
        "caption": caption,
        "access_token": access_token,
    })
    resp.raise_for_status()
    creation_id = resp.json()["id"]
    print(f"Created container {creation_id} for Day {day}")

    status_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{creation_id}"
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


if __name__ == "__main__":
    main()
