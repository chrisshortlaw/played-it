#!python3

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, TextAreaField
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


class AddGameForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()], render_kw={"class": "input", "placeholder": "Enter the title of the Game"})
    platform = StringField('Platform', validators=[DataRequired()], render_kw={"class": "input", "placeholder": "Enter the Platform the Game is on"})
    year = DateField('Year', validators=[DataRequired()], default="0000", render_kw={"class": "input", "placeholder": "Release Year"})
    genre = StringField('Genre', validators=[DataRequired()], default="unknownGenre", render_kw={"class": "input", "placeholder": "Enter Genre"})
    publisher = StringField('Publisher', validators=[DataRequired()], default="unknownPub", render_kw={"class": "input", "placeholder": "Enter Genre"})
    submit = SubmitField('Add Game', render_kw={"class": "button is-block is-info is-large is-fullwidth"})


class ReviewForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()], render_kw={"class": "input", "placeholder": "Title"})
    review_text = TextAreaField('text', validators=[InputRequired()], render_kw={"class": "input", "placeholder": "Your Review Here", "minlength": "2", "maxlength":"280", "rows":"4", "cols":"70"} )
    submit = SubmitField('Add Review', render_kw={"class": "button is-block is-info is-large is-fullwidth"})

