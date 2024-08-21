import cv2
from flask import request, jsonify

from APIs.SettingApi import *
from APIs.ListUrlApi import *
from Utilies.Function import *


@app.route("/", methods=["GET"])
def home():
    return (
        jsonify(
            {
                "success": True,
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
        "password_hash": hash(password),
    }
    profile_data = {
        "username": username,
        "full_name": "",
    }
    user_doc = db_firestore.collection(DATABASE_USER).document(userId)
    if user_doc.get().to_dict():
        return (
            jsonify(
                {
                    "success": False,
                    "status": 401,
                    "message": "Account is exists",
                }
            ),
            401,
        )
    else:
        user_doc.set(user_data)
        db_firestore.collection(DATABASE_PROFILE).document(userId).set(profile_data)
        return (
            jsonify(
                {
                    "success": True,
                    "status": 201,
                    "message": "Create account success",
                }
            ),
            201,
        )


@app.route(API_LOGIN, methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    userId = hash(username + password)

    user_doc = db_firestore.collection(DATABASE_USER).document(userId)
    if user_doc.get().to_dict():
        data_user = user_doc.get().to_dict()
        data_profile = (
            db_firestore.collection(DATABASE_PROFILE).document(userId).get().to_dict()
        )
        valid_tokens.add(data_user.get("access_token"))
        print(valid_tokens)
        return (
            jsonify(
                {
                    "success": True,
                    "status": 201,
                    "message": "Login success",
                    "body": {"data_user": data_user, "data_profile": data_profile},
                }
            ),
            201,
        )
    else:
        return (
            jsonify(
                {
                    "success": False,
                    "status": 401,
                    "message": "Username or password is wrong",
                }
            ),
            401,
        )

@app.route(API_PUSH_IMAGE,methods=["POST"])
def push_image_to_storage():
    local_image_path = "images/captured_image.jpg"
    
    storage_path = "images/avt/captured_image.jpg"
    cap = cv2.VideoCapture(0)  
    if not cap.isOpened():
        print("Không thể mở camera")
        return

    ret, frame = cap.read()
    if ret:
        cv2.imwrite(local_image_path, frame) 
        print(f"Đã chụp ảnh và lưu tại {local_image_path}")
    else:
        print("Không thể chụp ảnh")

    cap.release()
    cv2.destroyAllWindows()



    bucket = storage.bucket()
    blob = bucket.blob(storage_path)
    blob.upload_from_filename(local_image_path)
    print(f"File uploaded successfully to {storage_path}!")
    return (
        jsonify(
            {
                "success": True,
                "status": 201,
                "message": "pushSuccess",
            }
        ),
        201,
    )
@app.route(API_GET_IMAGE,methods=["GET"])
def get_image_from_storage():
    storage_path = "images/avt/captured_image.jpg"
    # Đường dẫn lưu trữ ảnh cục bộ sau khi tải về
    local_image_path = "images/downloaded_image.jpg"
    bucket = storage.bucket()
    blob = bucket.blob(storage_path)
    
    # Tải file từ Firebase Storage về máy cục bộ
    blob.download_to_filename(local_image_path)
    print(f"File downloaded successfully to {local_image_path}!")
    return (
        jsonify(
            {
                "success": True,
                "status": 201,
                "message": "get_image_success",
            }
        ),
        201,
    )



if __name__ == "__main__":    
    app.run(debug=True)
