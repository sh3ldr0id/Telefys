from firebase_admin.credentials import Certificate
from firebase_admin import initialize_app, firestore

def initFirebase():
    creds = Certificate("config/firebase.json")
    initialize_app(creds, {
        'databaseURL': 'https://telefys-bot.firebaseio.com'
    })