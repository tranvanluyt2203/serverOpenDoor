from flask import Flask, request, jsonify, g, redirect, url_for
import jwt
import datetime
from firebase_admin import credentials, auth, firestore, db
import firebase_admin
from firebase_admin import firestore
import json

from APIs.SettingApi import *
from APIs.ListUrlApi import *
from Utilies.Function import *


@app.route("/", methods=["GET"])
def home():
    return (
        jsonify(
            {
                "success":True,
                "status": 201,
                "message": "THIS IS HOME API",
            }
        ),
        201,
    )


@app.route(API_CREATE, methods=["POST"])
def create_account():
    username = request.json.get("username")
    password = request.json.get("password")
    
    userId = hash(username + password)

    user_data = {
        "access_token": API_KEY + userId + "IOT",
        "username": username,
        "password_hash": hash(password)
    }
    profile_data = {
        "username": username,
        "full_name":"",
    }
    user_doc = db_firestore.collection(DATABASE_USER).document(userId)
    if (user_doc.get().to_dict()):
        return (
            jsonify(
                {
                    "success":False,
                    "status": 401,
                    "message": "Account is exists",
                }
            ),
            401,
        )
    else :
        user_doc.set(user_data)
        db_firestore.collection(DATABASE_PROFILE).document(userId).set(profile_data)
        return (
            jsonify(
                {
                    "success":True,
                    "status": 201,
                    "message": "Create account success",
                }
            ),
            201,
        )
        
    


@app.route(API_LOGIN,methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    
    userId = hash(username+password)
    
    user_doc = db_firestore.collection(DATABASE_USER).document(userId)
    if (user_doc.get().to_dict()):
        data_user = user_doc.get().to_dict()
        data_profile = db_firestore.collection(DATABASE_PROFILE).document(userId).get().to_dict()
        valid_tokens.add(data_user.get("access_token"))
        print(valid_tokens)
        return(
            jsonify(
                {
                    "success":True,
                    "status": 201,
                    "message":"Login success",
                    "body":{
                        "data_user":data_user,
                        "data_profile":data_profile
                    }
                }
            ),
            201
        )
    else :
        return (
            jsonify(
                {
                    "success":False,
                    "status": 401,
                    "message": "Username or password is wrong",
                }
            ),
            401,
        )


if __name__ == "__main__":
    app.run(debug=True)
