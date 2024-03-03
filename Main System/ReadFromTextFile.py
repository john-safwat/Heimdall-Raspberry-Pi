import pyrebase

token: str = ""
lock_id: str = ""

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

# initialize pyrebase
pyrebase_firebase = pyrebase.initialize_app(firebase_config)
# initialize pyrebase auth
pyrebase_auth = pyrebase_firebase.auth()

print("Login")
with open('auth_data.txt', 'r') as file:
    email_and_password = file.read().split("\n")
    print(email_and_password)
    email = email_and_password[0]
    lock_password = email_and_password[1]
    login_user = pyrebase_auth.sign_in_with_email_and_password(email, lock_password)
    print("Successfully logged in!")
    lock_id = login_user['localId']
    token = login_user["idToken"]
    print(lock_id)
