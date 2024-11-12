from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import joblib


MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model_ai')
print(MODEL_DIR)

model_rain = joblib.load(os.path.join(MODEL_DIR, 'model_rain.joblib'))
model_temp = joblib.load(os.path.join(MODEL_DIR, 'model_temp.joblib'))
model_humidity = joblib.load(os.path.join(MODEL_DIR, 'model_humidity.joblib'))


scaler_rain = joblib.load(os.path.join(MODEL_DIR, 'scaler_rain.joblib'))
scaler_temp = joblib.load(os.path.join(MODEL_DIR, 'scaler_temp.joblib'))
scaler_humidity = joblib.load(os.path.join(MODEL_DIR, 'scaler_humidity.joblib'))


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

from app import routes, models
