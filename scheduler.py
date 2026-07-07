import time
from zoneinfo import ZoneInfo
from datetime import datetime

from app import (
    app,
    db,
    BroadcastNotification,
    User,
    CandidateUser,
    send_notification
)

IST = ZoneInfo("Asia/Kolkata")


def check_notifications():

    with app.app_context():

        print("Checking notifications...")
        print("Current IST time:", datetime.now(IST))

        notifications = BroadcastNotification.query.filter(
            BroadcastNotification.status == "Scheduled"
        ).all()

        for n in notifications:
            print(
                "Notification:",
                n.id,
                n.schedule_time,
                n.status
            )

        notifications = BroadcastNotification.query.filter(
            BroadcastNotification.status == "Scheduled",
            BroadcastNotification.schedule_time <= datetime.now(IST)
        ).all()

        for n in notifications:

            print(f"Sending notification {n.id}")

            full_message = f"{n.title}\n\n{n.message}"

            if n.send_to == "hr":

                for user in User.query.all():

                    send_notification(
                        user_id=user.id,
                        user_type="hr",
                        message=full_message,
                        type="admin_broadcast"
                    )

            elif n.send_to == "candidate":

                for user in CandidateUser.query.all():

                    send_notification(
                        user_id=user.id,
                        user_type="candidate",
                        message=full_message,
                        type="admin_broadcast"
                    )

            elif n.send_to == "both":

                for user in User.query.all():

                    send_notification(
                        user_id=user.id,
                        user_type="hr",
                        message=full_message,
                        type="admin_broadcast"
                    )

                for user in CandidateUser.query.all():

                    send_notification(
                        user_id=user.id,
                        user_type="candidate",
                        message=full_message,
                        type="admin_broadcast"
                    )

            n.status = "Sent"

        db.session.commit()


if __name__ == "__main__":

    print("Notification Scheduler Started")

    while True:

        try:
            check_notifications()

        except Exception as e:
            print("Scheduler Error:", e)

        time.sleep(60)