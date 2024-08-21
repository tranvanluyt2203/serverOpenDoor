from firebase_admin import credentials, firestore

from firebase_admin import firestore
import firebase_admin
from flask import Flask
from Utilies.Function import hash


# DOMAIN = "https://bfb-pbl7.xyz"
DOMAIN = "http://127.0.0.1:5000"

DATABASE_USER = "users"
DATABASE_PROFILE = "profiles"




API_USER = "/api/v1/users/"


valid_tokens = set()

app = Flask(__name__)

API_KEY = hash("I1O2T3")


cred = credentials.Certificate("./Firebase/opendoor-f2c07-firebase-adminsdk-aud3d-4117f59695.json")
firebase_admin.initialize_app(cred)
db_firestore = firestore.client()

valid_tokens = set()
