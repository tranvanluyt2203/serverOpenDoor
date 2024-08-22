from app import app
from app.models import *
from flask import request
from app.utils.responses import error_response, success_response, list_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


@app.route("/", methods=["GET"])
def home():
    return success_response(message='THIS IS HOME API',status_code=201)


@app.route(app.config['API_CREATE'], methods=["POST"])
def create_account():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')

    if not all([username, password, first_name, last_name, email]):
        return  error_response(message='Missing required fields',status_code=400)

    # Check if username or email already exists
    if Account.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return error_response(message='Username or email already exists',status_code=400)
   
    account = Account(username=username, password=password, access_token=create_access_token(identity=username))
    account.set_password(password)
    db.session.add(account)
    db.session.commit()
    
    user = User(first_name=first_name, last_name=last_name, email=email, account_id=account.id)
    db.session.add(user)
    db.session.commit()

    return success_response(data={'account': account.to_dict(), 'user': user.to_dict()},message='Account created successfully',status_code=201)


@app.route(app.config['API_LOGIN'], methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    if not all([username, password]):
        return error_response(message='Missing required fields',status_code=400)
    
    account = Account.query.filter_by(username=username).first()
    if account is None or not account.check_password(password):
        return error_response(message='Invalid username or password',status_code=401)
    
    user = User.query.filter_by(account_id=account.id).first()
    return success_response(data={'access_token': account.access_token, 'user': user.to_dict()},message='Login successful',status_code=200)

# @app.route(API_PUSH_IMAGE,methods=["POST"])
# def push_image_to_storage():
#     local_image_path = "images/captured_image.jpg"
    
#     storage_path = "images/avt/captured_image.jpg"
#     cap = cv2.VideoCapture(0)  
#     if not cap.isOpened():
#         print("Không thể mở camera")
#         return

#     ret, frame = cap.read()
#     if ret:
#         cv2.imwrite(local_image_path, frame) 
#         print(f"Đã chụp ảnh và lưu tại {local_image_path}")
#     else:
#         print("Không thể chụp ảnh")

#     cap.release()
#     cv2.destroyAllWindows()



#     bucket = storage.bucket()
#     blob = bucket.blob(storage_path)
#     blob.upload_from_filename(local_image_path)
#     print(f"File uploaded successfully to {storage_path}!")
#     return (
#         jsonify(
#             {
#                 "success": True,
#                 "status": 201,
#                 "message": "pushSuccess",
#             }
#         ),
#         201,
#     )
# @app.route(API_GET_IMAGE,methods=["GET"])
# def get_image_from_storage():
#     storage_path = "images/avt/captured_image.jpg"
#     # Đường dẫn lưu trữ ảnh cục bộ sau khi tải về
#     local_image_path = "images/downloaded_image.jpg"
#     bucket = storage.bucket()
#     blob = bucket.blob(storage_path)
    
#     # Tải file từ Firebase Storage về máy cục bộ
#     blob.download_to_filename(local_image_path)
#     print(f"File downloaded successfully to {local_image_path}!")
#     return (
#         jsonify(
#             {
#                 "success": True,
#                 "status": 201,
#                 "message": "get_image_success",
#             }
#         ),
#         201,
#     )



# if __name__ == "__main__":    
#     app.run(debug=True)
