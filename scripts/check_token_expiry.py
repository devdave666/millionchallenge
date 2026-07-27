import os
import smtplib
from datetime import date, timedelta
from email.mime.text import MIMEText

ISSUED_FILE = "token_issued.txt"
TOKEN_LIFESPAN_DAYS = 60
WARNING_DAYS_REMAINING = 10
ASSUMED_ROTATION_WINDOW_DAYS = 7


def get_issued_date():
    with open(ISSUED_FILE) as f:
        return date.fromisoformat(f.read().strip())


def get_days_remaining(issued):
    elapsed = (date.today() - issued).days
    return TOKEN_LIFESPAN_DAYS - elapsed


def set_issued_date(new_date):
    with open(ISSUED_FILE, "w") as f:
        f.write(new_date.isoformat())


def send_email(days_remaining, next_check_in_date):
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
    notify_to = os.environ.get("NOTIFY_EMAIL", gmail_address)

    if not gmail_address or not gmail_app_password:
        print("GMAIL_ADDRESS / GMAIL_APP_PASSWORD secrets not set - skipping email, "
              f"but token expires in {days_remaining} day(s).")
        return False

    subject = f"Million Followers Challenge - Instagram token expires in {days_remaining} day(s)"

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

You do NOT need to manually reset any date file — this system assumes you'll rotate the
token within the next {ASSUMED_ROTATION_WINDOW_DAYS} days and has already scheduled the
next reminder for around {next_check_in_date.isoformat()} on its own.

No need to touch IG_BUSINESS_ACCOUNT_ID, it doesn't change.
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = gmail_address
    msg["To"] = notify_to

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_app_password)
        server.sendmail(gmail_address, [notify_to], msg.as_string())

    print(f"Reminder email sent - token expires in {days_remaining} day(s).")
    return True


def main():
    issued = get_issued_date()
    days_remaining = get_days_remaining(issued)
    print(f"Token issued: {issued.isoformat()}, days remaining: {days_remaining}")

    force_test = os.environ.get("FORCE_TEST_EMAIL", "").lower() == "true"

    should_warn = force_test or days_remaining == WARNING_DAYS_REMAINING

    if not should_warn:
        print("No reminder needed today.")
        return

    # Assume rotation happens within ASSUMED_ROTATION_WINDOW_DAYS of this email.
    # Advance the tracked issue date so the next 60-day cycle counts from that
    # assumed rotation point, instead of waiting for a manual reset.
    assumed_new_issue_date = date.today() + timedelta(days=ASSUMED_ROTATION_WINDOW_DAYS)
    next_check_in_date = assumed_new_issue_date + timedelta(days=TOKEN_LIFESPAN_DAYS - WARNING_DAYS_REMAINING)

    sent = send_email(max(days_remaining, 0), next_check_in_date)

    if sent and not force_test:
        set_issued_date(assumed_new_issue_date)
        print(f"Auto-advanced token_issued.txt to {assumed_new_issue_date.isoformat()} "
              f"(assumed rotation within {ASSUMED_ROTATION_WINDOW_DAYS} days).")


if __name__ == "__main__":
    main()
