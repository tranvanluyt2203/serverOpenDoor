from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    access_token = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(20), default='active')
    user = db.relationship('User', backref='account', uselist=False)
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'access_token': self.access_token
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }
    

