#!python3

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, EqualTo, InputRequired, Email
from wtforms.fields.html5 import EmailField
from models import played_it_db


class LoginForm(FlaskForm):
    """
    Login form for App.
    Fields:
        username -> StringField
        password -> PasswordField
        remember_me -> BooleanField
        submit -> SubmitField
    username & password have DataRequired() validator
    """
    username = StringField('Username', validators=[DataRequired()], render_kw={"class": "input", "placeholder":"Username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"class": "input", "placeholder": "Password"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In', render_kw={"class": "button is-block is-info is-large is-fullwidth"})
    

class RegisterForm(FlaskForm):
    """
    Registration Form for App.
    Fields: 
            username -> StringField
            password -> PasswordField
            confirm -> PasswordField & EqualTo password
            email -> EmailField
            submit -> SubmitField
    """
    username = StringField('Username', validators=[DataRequired()], render_kw={"class": "input", "placeholder":"Enter a Username"})
    password = PasswordField('Password', validators=[InputRequired(), DataRequired()], render_kw={"class": "input", "placeholder": "Enter a Password"})
    confirm = PasswordField('ConfirmPassword', validators=[DataRequired(), EqualTo('password', message='Passwords must match')], render_kw={"class": "input", "placeholder": "Confirm Password"})
    email = StringField('Email', validators=[DataRequired(), Email(message='Invalid Email Address')], render_kw={"class":"input", "placeholder": "Enter Your Email"})
    submit = SubmitField('Register', render_kw={"class": "button is-block is-info is-large is-fullwidth"})

