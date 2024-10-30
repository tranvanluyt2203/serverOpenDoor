from app import app
from app.models import *
from flask import request
from app.utils.responses import error_response, success_response, list_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import model_humidity, model_rain, model_temp, scaler_humidity, scaler_rain, scaler_temp
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func
import random



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
    hours_ahead = data['hours_ahead']
    now = datetime.now()
    start_time = now - timedelta(hours=4)
    
    # weather_data = (
    #     db.session.query(
    #         func.strftime('%Y-%m-%d %H:00:00', Weather.created_at).label('hour'),
    #         func.avg(Weather.temp).label('avg_temperature'),
    #         func.avg(Weather.humidity).label('avg_humidity')
    #     )
    #     .filter(Weather.created_at >= start_time)
    #     .group_by(func.strftime('%Y-%m-%d %H:00:00', Weather.created_at))
    #     .order_by(func.strftime('%Y-%m-%d %H:00:00', Weather.created_at).asc())
    #     .all()
    # )
    weather_data = (
    db.session.query(
        func.strftime('%Y-%m-%d %H:00:00', Weather.created_at).label('hour'),
        func.avg(Weather.temp).label('avg_temperature'),
        func.avg(Weather.humidity).label('avg_humidity')
    )
    .group_by(func.strftime('%Y-%m-%d %H:00:00', Weather.created_at))
    .order_by(func.strftime('%Y-%m-%d %H:00:00', Weather.created_at).desc())
    .limit(4)  
    .all()
    )
    
    weather_list = [{
        'hour': w.hour,
        'avg_temperature': round(w.avg_temperature, 2),
        'avg_humidity': round(w.avg_humidity, 2)
    } for w in weather_data]
    temp_history = [w['avg_temperature'] for w in weather_list]
    humidity_history = [w['avg_humidity'] for w in weather_list]

    print(temp_history)
    print(humidity_history)

    if(len(temp_history) == 5):
        temp_history.pop(0)
        humidity_history.pop(0)


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
    latest_record = db.session.query(Weather).order_by(Weather.created_at.desc()).first()
    latest_temp = round(latest_record.temp, 2)
    latest_humidity = round(latest_record.humidity, 2)
    return success_response(data={
        'temp_forecast': [latest_temp] + [float(p[0]) for p in predictions],
        'humidity_forecast': [latest_humidity]+[float(p[1]) for p in predictions],
        'rain_prob': [random.choices([0.3,0.35,0.4],weights=[0.8,0.1,0.1],k=1)[0]]+[float(p[2]) for p in predictions]
    },message='Prediction successful',status_code=200)


@app.route('/weather', methods=['POST'])
def add_weather():
    data = request.json
    temp = data['temp']
    humidity = data['humidity']
    
    print("temp",temp)
    print("humidity",humidity)

    weather = Weather(temp=temp, humidity=humidity, created_at=datetime.now())
    db.session.add(weather)
    db.session.commit()

    return success_response(data=weather.to_dict(),message='Weather added successfully',status_code=201)

@app.route('/generate_bulk_weather', methods=['POST'])
def generate_bulk_weather():
    num_records = request.json.get('num_records', 100)  # Mặc định là 100 bản ghi
    hours_back = request.json.get('hours_back', 24)  # Mặc định là 24 giờ

    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours_back)

    generated_records = []

    for _ in range(num_records):
        temp = round(random.uniform(20, 35), 2)
        humidity = round(random.uniform(30, 80), 2)
        created_at = start_time + timedelta(seconds=random.randint(0, hours_back * 3600))

        weather = Weather(temp=temp, humidity=humidity, created_at=created_at)
        db.session.add(weather)
        generated_records.append(weather.to_dict())

    db.session.commit()
    return success_response(data=generated_records,message='Weather data generated successfully',status_code=201)

@app.route('/weather', methods=['GET'])
def get_weather():
    now = datetime.now()
    start_time = now - timedelta(hours=4)
    
    # Truy vấn và tổng hợp dữ liệu thời tiết trong 24 giờ qua
    weather_data = (
        db.session.query(
            func.strftime('%Y-%m-%d %H:00:00', Weather.created_at).label('hour'),
            func.avg(Weather.temp).label('avg_temperature'),
            func.avg(Weather.humidity).label('avg_humidity')
        )
        .filter(Weather.created_at >= start_time)
        .group_by(func.strftime('%Y-%m-%d %H:00:00', Weather.created_at))
        .order_by(func.strftime('%Y-%m-%d %H:00:00', Weather.created_at).asc())
        .all()
    )
    
    # Chuyển đổi dữ liệu thành list of dictionaries
    weather_list = [{
        'hour': w.hour,
        'avg_temperature': round(w.avg_temperature, 2),
        'avg_humidity': round(w.avg_humidity, 2)
    } for w in weather_data]
    return success_response( data=weather_list,message='Weather data retrieved successfully',status_code=200) 
#  get time now 
@app.route('/time', methods=['GET'])
def get_time():
    now = datetime.now()
    return success_response(data={'time': now},message='Time retrieved successfully',status_code=200)

@app.route('/data', methods=['POST'])
def receive_data():
    temperature = request.form.get('temperature')
    humidity = request.form.get('humidity')
    
    if temperature and humidity:
        print(f"Received Temperature: {temperature}°C, Humidity: {humidity}%")
        return "Data received successfully", 200
    else:
        return "Missing data", 400
