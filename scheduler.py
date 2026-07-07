import time

from app import app
from app import db

from app import BroadcastNotification

def check_notifications():

    with app.app_context():

        print("Scheduler Running...")

if __name__ == "__main__":

    print("Notification Scheduler Started")

    while True:

        try:

            check_notifications()

        except Exception as e:

            print("Scheduler Error:", e)

        time.sleep(60)