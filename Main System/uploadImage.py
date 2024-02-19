import pyrebase

firebase_config = {
    "apiKey": "AIzaSyD7BJiwIa7J2llFnmYe-eHTtKJi11gnBxc",
    "authDomain": "heimdall-5aecb.firebaseapp.com",
    "databaseURL": "https://heimdall-5aecb-default-rtdb.firebaseio.com",
    "projectId": "heimdall-5aecb",
    "storageBucket": "heimdall-5aecb.appspot.com",
    "messagingSenderId": "162564554099",
    "appId": "1:162564554099:web:7d8d43779925e659d1d906",
    "measurementId": "G-YJY39SDG6Z",
    "serviceAccount": "heimdall.json",
}

firebase = pyrebase.initialize_app(firebase_config)

auth = firebase.auth()
storage = firebase.storage()

user = auth.sign_in_with_email_and_password(email="2748787417@heimdall.com", password="123123123")

storage.child("taked/takenImages.jpg").put("4.jpg")
url = storage.child("taked/takenImages.jpg").get_url(user['idToken'])
print("url", url)
