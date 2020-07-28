from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    measurements = db.relationship('Measurement', backref='user',
                                   lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Date, index=True)
    weight = db.Column(db.Float)
    bmi = db.Column(db.Float)
    body_fat = db.Column(db.Float)
    muscle = db.Column(db.Float)
    rm_kcal = db.Column(db.Float)
    visceral_fat = db.Column(db.Float)


'''
m.id
m.user_id
m.date

val.m_id
val.mt_id
val.value
'''

'''
weight
bmi
body_fat
muscle
rm_kcal
visceral_fat
'''
