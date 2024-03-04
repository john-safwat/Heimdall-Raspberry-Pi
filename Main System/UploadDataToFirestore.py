import firebase_admin
from firebase_admin import credentials, firestore, messaging

firestore_credentials = credentials.Certificate("heimdall.json")
app = firebase_admin.initialize_app(firestore_credentials)
firebase_firestore = firestore.client()
log_collection_reference = firebase_firestore.collection('Log')
log_collection_reference.add({u'name': u'test', u'added': u'just now'})

topic = "n197o0uVQ1WLANpSG5yH1VnxSKn1"
try:
    message = messaging.Message(
        notification=messaging.Notification(
            title="Heimdall Lock",
            body="Check the code"
        ),
        topic=topic
    )
    messaging.send(message)
except Exception as e:
    print("exception")
