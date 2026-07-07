from datetime import datetime

from app import (
    app,
    db,
    BroadcastNotification,
    User,
    CandidateUser,
    send_notification
)

def check_notifications():

    with app.app_context():

        print("Checking notifications...")

        notifications = BroadcastNotification.query.filter(
            BroadcastNotification.status == "Scheduled",
            BroadcastNotification.schedule_time <= datetime.now()
        ).all()

        for n in notifications:

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