from flask import Flask, render_template, redirect, url_for, flash, \
    get_flashed_messages
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'

from flask_login import current_user, login_user, logout_user, login_required
from models import User, Measurement
from forms import LoginForm, MeasurementForm
from app import app


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/measurements/add', methods=['GET', 'POST'])
@login_required
def measurements_add():
    form = MeasurementForm()
    if form.validate_on_submit():
        user_id = get_current_user_id()
        measurement_id = add_measurement(user_id, form.date.data)
        if measurement_id is not None:
            weight = form.weight.data if form.weight.data != '' else None
            bmi = form.bmi.data if form.bmi.data != '' else None
            body_fat = form.body_Fat.data if form.body_Fat.data != '' else None
            muscle = form.muscle.data if form.muscle.data != '' else None
            rm_kcal = form.rm_kcal.data if form.rm_kcal.data != '' else None
            visceral_fat = form.visceral_fat.data if form.visceral_fat.data != '' else None
            add_values(measurement_id, weight=weight, bmi=bmi,
                       body_fat=body_fat, muscle=muscle, rm_kcal=rm_kcal,
                       visceral_fat=visceral_fat)
        flash('Messung gespeichert')
        return redirect(url_for('index'))
    return render_template('measurements.html', title='Messungen', form=form)


@app.route('/measurements')
@login_required
def measurements():
    user_id = get_current_user_id()
    measurement = Measurement.query.filter_by(user_id=user_id).order_by('date')
    return render_template('measurements.html', title='Messungen',
                           measurements=measurement)


'''
end of routes
'''


def add_measurement(user_id, date):
    m = Measurement.query.filter_by(user_id=user_id, date=date).scalar()
    if m is None:
        m = Measurement()
        m.date = date
        m.user_id = user_id
        db.session.add(m)
        db.session.flush()
        result = m.id
        db.session.commit()
        print(f'measurement inserted with id {result}')
        return result
    print(f'measurement exists with id {m.id}')
    return m.id


def add_values(measurement_id, weight=None, bmi=None, body_fat=None,
               muscle=None, rm_kcal=None, visceral_fat=None):
    pass

def get_current_user_id():
    u = User.query.filter_by(username=current_user.username).first()
    return u.id


if __name__ == '__main__':
    app.run()
