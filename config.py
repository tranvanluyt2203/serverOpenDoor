import os
basedir = os.path.abspath(os.path.dirname(__file__))
database_dir = os.path.join(basedir, 'database')
class Config(object):
    
#    SECRET_KEY = os.environ.get('SECRET_KEY') or 'do-or-do-not-there-is-no-try'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(database_dir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = '55a4711cce9e240b588b1724496556eea217d7e29b1e115c10cb167b4881bcbf'
    JWT_ACCESS_TOKEN_EXPIRES = 36000
    # Cấu hình API
    DOMAIN = "https://yourdomain.com"
    API_USER = "/api/v1/users/"
    API_PHOTO = "/api/v1/photos/"

    # Cấu hình API chi tiết
    API_LOGIN = API_USER + "login"
    API_LOGOUT = API_USER + "logout"
    API_CREATE = API_USER + "create"

    API_PUSH_IMAGE = API_PHOTO + "push_image"
    API_GET_IMAGE = API_PHOTO + "get_image"
