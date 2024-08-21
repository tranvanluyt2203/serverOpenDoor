from firebase_admin import credentials, firestore, storage

import firebase_admin
from flask import Flask
from Utilies.Function import hash


# DOMAIN = "https://bfb-pbl7.xyz"
DOMAIN = "http://127.0.0.1:5000"

DATABASE_USER = "users"
DATABASE_PROFILE = "profiles"




API_USER = "/api/v1/users/"
API_PHOTO = "/api/v1/photos/"


valid_tokens = set()

app = Flask(__name__)

API_KEY = hash("I1O2T3")


cred = credentials.Certificate("./Firebase/opendoor-f2c07-firebase-adminsdk-aud3d-4117f59695.json")
firebase_admin.initialize_app(
    cred,{
        'storageBucket':'opendoor-f2c07.appspot.com'
    })
bucket = storage.bucket()
db_firestore = firestore.client()

valid_tokens = set()
