#!python3

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from wtforms.fields.html5 import EmailField
from models import played_it_db


class LoginForm(FlaskForm):
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
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"class": "input", "placeholder": "Enter a Password"})
    confirm = PasswordField('ConfirmPassword', validators=[DataRequired(), EqualTo('password')], render_kw={"class": "input", "placeholder": "Confirm Password"})
    email = EmailField('Email', validators=[DataRequired()], render_kw={"class":"input", "placeholder": "Enter Your Email"})
    submit = SubmitField('Register', render_kw={"class": "button is-block is-info is-large is-fullwidth"})

    # def validate_username(self, username):
        # "Insert database query here for username"
        # user = [Database Query]
        # if user is not None:
            # raise ValidationError('Username Taken. Please use a different username')

    # def validate_email(self, email):
   #      """
        # Insert database query here.

        # """
        # # user = [Insert Database Query Here]
        # if user is not None:
            # raise ValidationError('Email Already Registered. Forgot your password? [Insert Link Here]')
