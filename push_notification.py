from firebase_admin import messaging

def send_push_notification(token, title, body):

    message = messaging.Message(

        notification=messaging.Notification(
            title=title,
            body=body
        ),

        data={
            "title": title,
            "body": body
        },

        android=messaging.AndroidConfig(
            priority="high"
        ),

        token=token
    )

    return messaging.send(message)