import os
import sys
import smtplib
from email.mime.text import MIMEText


def main():
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
    notify_to = os.environ.get("NOTIFY_EMAIL", gmail_address)
    run_url = os.environ.get("RUN_URL", "")
    reason = os.environ.get("FAILURE_REASON", "unknown step failed")

    if not gmail_address or not gmail_app_password:
        print("GMAIL_ADDRESS / GMAIL_APP_PASSWORD secrets not set - cannot send failure alert.")
        sys.exit(0)

    subject = "Million Followers Challenge - daily post FAILED"
    body = f"""The daily reel post for the Million Followers Challenge (@artificial_intellectual)
failed to run today.

Reason: {reason}

Check the run here:
{run_url}

The day counter was NOT incremented, so nothing was skipped - just re-run the workflow
manually once fixed (Actions tab -> Daily Million Follower Challenge Post -> Run workflow).
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = gmail_address
    msg["To"] = notify_to

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_app_password)
        server.sendmail(gmail_address, [notify_to], msg.as_string())

    print("Failure alert email sent.")


if __name__ == "__main__":
    main()
