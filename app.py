from flask import Flask, render_template, redirect, url_for, flash, \
    get_flashed_messages
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

import io
import base64
import seaborn as sns
import matplotlib.pyplot as plt

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
        data = {}
        data['date'] = form.date.data
        data['weight'] = form.weight.data
        data['bmi'] = form.bmi.data if form.bmi.data != '' else None
        data[
            'body_fat'] = form.body_Fat.data if form.body_Fat.data != '' else None
        data['muscle'] = form.muscle.data if form.muscle.data != '' else None
        data['rm_kcal'] = form.rm_kcal.data if form.rm_kcal.data != '' else None
        data[
            'visceral_fat'] = form.visceral_fat.data if form.visceral_fat.data != '' else None
        measurement_id = add_measurement(user_id, data)
        flash('Messung gespeichert')
        return redirect(url_for('measurements'))
    return render_template('measurement_add.html', title='Messungen', form=form)


@app.route('/measurements')
@login_required
def measurements():
    user_id = get_current_user_id()
    measurement = Measurement.query.filter_by(user_id=user_id).order_by(
        Measurement.date.desc())
    return render_template('measurements.html', title='Messungen',
                           measurements=measurement)


@app.route('/test/')
def test():
    img = io.BytesIO()
    sns.set_style("dark")

    y = [1, 2, 3, 4, 5]
    x = [0, 2, 1, 3, 4]

    plt.plot(x, y)
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
    print(plot_url)
    return render_template('test.html', plot_url=plot_url)

'''
end of routes
'''


def add_measurement(user_id, data):
    m = Measurement.query.filter_by(user_id=user_id, date=data['date']).scalar()
    if m is None:
        m = Measurement()
    m.date = data['date']
    m.user_id = user_id
    m.weight = data['weight']
    m.bmi = data['bmi']
    m.body_fat = data['body_fat']
    m.muscle = data['muscle']
    m.rm_kcal = data['rm_kcal']
    m.visceral_fat = data['visceral_fat']
    db.session.add(m)
    db.session.flush()
    result = m.id
    db.session.commit()
    print(f'measurement inserted/updated with id {result}')
    return result


def add_values(measurement_id, weight=None, bmi=None, body_fat=None,
               muscle=None, rm_kcal=None, visceral_fat=None):
    pass


def get_current_user_id():
    u = User.query.filter_by(username=current_user.username).first()
    return u.id


if __name__ == '__main__':
    app.run()
