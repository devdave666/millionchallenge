import os
import sys
import smtplib
from datetime import date
from email.mime.text import MIMEText

ISSUED_FILE = "token_issued.txt"
TOKEN_LIFESPAN_DAYS = 60
WARNING_THRESHOLDS = [10, 5, 1]  # days remaining that trigger an email


def get_days_remaining():
    with open(ISSUED_FILE) as f:
        issued_str = f.read().strip()
    issued = date.fromisoformat(issued_str)
    elapsed = (date.today() - issued).days
    return TOKEN_LIFESPAN_DAYS - elapsed


def send_email(days_remaining):
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
    notify_to = os.environ.get("NOTIFY_EMAIL", gmail_address)

    if not gmail_address or not gmail_app_password:
        print("GMAIL_ADDRESS / GMAIL_APP_PASSWORD secrets not set - skipping email, "
              f"but token expires in {days_remaining} day(s).")
        return

    urgency = "URGENT: " if days_remaining <= 1 else ""
    subject = f"{urgency}Million Followers Challenge - Instagram token expires in {days_remaining} day(s)"

    body = f"""Heads up — the Instagram access token for the Million Followers Challenge
(@artificial_intellectual) expires in approximately {days_remaining} day(s).

If it expires before you refresh it, the daily reel post will silently fail.

WHAT TO DO:

1. Go to the Meta developer dashboard for the app:
   https://developers.facebook.com/apps/1510843857376746/dashboard/

2. Go to: Use cases > Manage messaging & content on Instagram > API setup with Instagram login

3. Under "Generate access tokens", confirm @artificial_intellectual is still listed as a
   tester. If the invite lapsed, re-send it from the dashboard and accept it again from
   the Instagram app (Settings > Apps and websites > Tester invites).

4. Click "Generate token" next to the account to get a fresh long-lived token.

5. Update the repo secret with the new token:
   https://github.com/devdave666/millionchallenge/settings/secrets/actions
   (edit IG_ACCESS_TOKEN)

6. Reset the issue-date tracker so this reminder cycle restarts:
   Edit token_issued.txt in the repo to today's date (YYYY-MM-DD) and commit.
   https://github.com/devdave666/millionchallenge/edit/main/token_issued.txt

That's it — no need to touch IG_BUSINESS_ACCOUNT_ID, it doesn't change.
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = gmail_address
    msg["To"] = notify_to

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_app_password)
        server.sendmail(gmail_address, [notify_to], msg.as_string())

    print(f"Reminder email sent - token expires in {days_remaining} day(s).")


def main():
    days_remaining = get_days_remaining()
    print(f"Days remaining on token: {days_remaining}")

    if days_remaining in WARNING_THRESHOLDS or days_remaining <= 0:
        send_email(max(days_remaining, 0))
    else:
        print("No reminder needed today.")


if __name__ == "__main__":
    main()
