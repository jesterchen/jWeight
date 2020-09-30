from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import DecimalField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Optional
from app.models import User
from datetime import date


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class MeasurementForm(FlaskForm):
    date = DateField('Messdatum', validators=[DataRequired()],
                     default=date.today)
    weight = DecimalField('Gewicht [kg]')
    bmi = DecimalField('BMI', validators=[Optional()])
    body_Fat = DecimalField('Koerperfett [%]', validators=[Optional()])
    muscle = DecimalField('Muskelmasse [%]', validators=[Optional()])
    rm_kcal = DecimalField('Grundumsatz [kcal]', validators=[Optional()])
    visceral_fat = DecimalField('Viszeralfett', validators=[Optional()])
    circumference = DecimalField('Bauchumfang [cm]', validators=[Optional()])
    submit = SubmitField('Speichern', validators=[Optional()])
