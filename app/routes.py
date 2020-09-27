from app import app, db
import io
import base64
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, redirect, url_for, flash, get_flashed_messages
from app.forms import LoginForm, MeasurementForm
from app.models import User, Measurement


@app.route('/')
@login_required
def index():
    images = []
    for i in ['weight', 'Gewicht'], ['bmi', 'BMI'], ['body_fat', 'Körperfett'], ['muscle', 'Muskelmasse'], \
             ['rm_kcal', 'Grundumsatz'], ['visceral_fat', 'Viszeralfett'], ['circumference', 'Bauchumfang']:
        images.append(create_image_from_user_data(i[0], i[1]))

    user_id = get_current_user_id()
    measurements = Measurement.query.filter_by(user_id=user_id).order_by(
        Measurement.date.desc())

    form = MeasurementForm()

    return render_template('index.html', images=images, open_accordion_at='Gewicht', measurements=measurements,
                           form=form)


def get_measurements_for_user():
    ms = Measurement.query.filter_by(user_id=get_current_user_id()).all()
    date = []
    weight = []
    bmi = []
    body_fat = []
    muscle = []
    rm_kcal = []
    visceral_fat = []
    circumference = []
    for m in ms:
        date.append(m.date)
        weight.append(m.weight)
        bmi.append(m.bmi)
        body_fat.append(m.body_fat)
        muscle.append(m.muscle)
        rm_kcal.append(m.rm_kcal)
        visceral_fat.append(m.visceral_fat)
        circumference.append(m.circumference)
    d = {'date': date, 'weight': weight, 'bmi': bmi, 'body_fat': body_fat,
         'muscle': muscle, 'rm_kcal': rm_kcal, 'visceral_fat': visceral_fat, 'circumference': circumference}
    return d


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
        data['visceral_fat'] = form.visceral_fat.data if form.visceral_fat.data != '' else None
        data['circumference'] = form.circumference.data if form.circumference.data != '' else None
        measurement_id = add_measurement(user_id, data)
        flash('Messung gespeichert')
        return redirect(url_for('index'))
    return render_template('measurement_add.html', title='Messungen', form=form)


@app.route('/measurements')
@login_required
def measurements():
    user_id = get_current_user_id()
    measurement = Measurement.query.filter_by(user_id=user_id).order_by(
        Measurement.date.desc())
    return render_template('measurements.html', title='Messungen',
                           measurements=measurement)


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
    m.circumference = data['circumference']
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


def create_image_from_user_data(column_to_show, description, sort_by='date'):
    img = io.BytesIO()
    sns.set_style("darkgrid")

    dataset = get_measurements_for_user()
    df = get_sorted_data_frame(dataset, sort_by)

    plt.plot(df[column_to_show])
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)

    image = base64.b64encode(img.getvalue()).decode('utf-8')
    image = f'data:image/png;base64, {image}'
    return {'image': image, 'description': description}


def get_sorted_data_frame(data, sort_by):
    df = pd.DataFrame(data=data)
    df.set_index(sort_by, inplace=True)
    return df.sort_index()
