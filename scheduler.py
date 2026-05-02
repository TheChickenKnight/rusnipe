import schedule
import time
import requests
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class UserCriteria:
    class_id: str
    class_name: str
    min_seats: int = 1
    notify_email: Optional[str] = None


def check_seat_availability(criteria: UserCriteria) -> dict:
    """
    Call your seat availability API/scraper here.
    Returns a dict with availability info.
    """
    # Replace with your actual API call or web scraping logic
    response = requests.get(
        f"https://your-registration-api.com/classes/{criteria.class_id}/seats",
        timeout=10
    )
    return response.json()  # e.g., {"available_seats": 3, "total_seats": 30}


def send_notification(criteria: UserCriteria, seats: int):
    """Send alert when seats become available."""
    message = (
        f"🎉 SEATS AVAILABLE: '{criteria.class_name}' "
        f"now has {seats} seat(s) open!"
    )
    print(f"[{datetime.now()}] ALERT: {message}")

    # Add your notification method here:
    # - Email via smtplib / SendGrid
    # - SMS via Twilio
    # - Push notification
    # - Slack/Discord webhook


def poll_class(criteria: UserCriteria):
    """Core polling logic — runs every 15 minutes."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Checking '{criteria.class_name}'...")

    try:
        data = check_seat_availability(criteria)
        available = data.get("available_seats", 0)

        if available >= criteria.min_seats:
            send_notification(criteria, available)
        else:
            print(f"  → No seats yet ({available} available, need {criteria.min_seats})")

    except requests.RequestException as e:
        print(f"  → Request failed: {e}")
    except Exception as e:
        print(f"  → Unexpected error: {e}")


def start_polling(watched_classes: list[UserCriteria], interval_minutes: int = 15):
    """Schedule polling jobs and run the loop."""
    for criteria in watched_classes:
        # Run immediately on start, then on schedule
        poll_class(criteria)
        schedule.every(interval_minutes).minutes.do(poll_class, criteria=criteria)

    print(f"\nPolling {len(watched_classes)} class(es) every {interval_minutes} minutes. Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30s for pending jobs


# --- Entry point ---
if __name__ == "__main__":
    watched = [
        UserCriteria(
            class_id="CS101-A",
            class_name="Intro to Computer Science",
            min_seats=1,
        ),
        UserCriteria(
            class_id="MATH301-B",
            class_name="Linear Algebra",
            min_seats=2,
        ),
    ]

    start_polling(watched, interval_minutes=15)