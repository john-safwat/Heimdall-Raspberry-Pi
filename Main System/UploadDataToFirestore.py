import firebase_admin
from firebase_admin import credentials, messaging

firebase_cred = credentials.Certificate("heimdall.json")
firebase_app = firebase_admin.initialize_app(firebase_cred)

message = messaging.Message(
    notification=messaging.Notification(
        title="New Notification",
        body="Alert to view"
    ),
    topic="TestData",
    data={
        "MyNotification": "nardin"
    }
)

response = messaging.send(message)
print(response)
print("done")
