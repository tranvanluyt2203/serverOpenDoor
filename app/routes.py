from app import app
from app.models import *
from flask import request
from app.utils.responses import error_response, success_response, list_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import model_humidity, model_rain, model_temp, scaler_humidity, scaler_rain, scaler_temp
import numpy as np
import pandas as pd


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

@app.route('/predict', methods=['POST'])
def predict_weather():
    hours_past = 4
    data = request.json
    temp_history = data['temp_history']
    humidity_history = data['humidity_history']
    hours_ahead = data['hours_ahead']

    if len(temp_history) != hours_past or len(humidity_history) != hours_past:
        return error_response(message=f"Cần cung cấp {hours_past} giá trị nhiệt độ và độ ẩm gần nhất",status_code=400)

    predictions = []

    for _ in range(hours_ahead):
        input_data = np.array(temp_history + humidity_history + [0, 0]).reshape(1, -1)
        
        feature_names = [f'Temp_-{h}h' for h in range(1, hours_past + 1)] + \
                        [f'Humidity_-{h}h' for h in range(1, hours_past + 1)] + \
                        ['Hour', 'DayOfWeek']

        input_data_df = pd.DataFrame(input_data, columns=feature_names)

        input_data_scaled_rain = scaler_rain.transform(input_data_df)
        input_data_scaled_temp = scaler_temp.transform(input_data_df)
        input_data_scaled_humidity = scaler_humidity.transform(input_data_df)

        rain_prob = model_rain.predict_proba(input_data_scaled_rain)[0][1]
        temp_forecast = model_temp.predict(input_data_scaled_temp)[0]
        humidity_forecast = model_humidity.predict(input_data_scaled_humidity)[0]

        predictions.append((temp_forecast, humidity_forecast, rain_prob))

        temp_history.append(temp_forecast)
        humidity_history.append(humidity_forecast)
        temp_history.pop(0)
        humidity_history.pop(0)

    return success_response(data={
        'temp_forecast': [float(p[0]) for p in predictions],
        'humidity_forecast': [float(p[1]) for p in predictions],
        'rain_prob': [float(p[2]) for p in predictions]
    },message='Prediction successful',status_code=200)