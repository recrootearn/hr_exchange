import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("firebase-adminsdk.json")

try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)


def send_push_notification(token, title, body):

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token,
    )

    response = messaging.send(message)

    return response