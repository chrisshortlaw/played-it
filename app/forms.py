#!python3

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo, InputRequired, Email
from wtforms.fields.html5 import EmailField
from bson.objectid import ObjectId

# TODO: INSERT DATABASE IMPORT HERE
from app.database_mongo import mongo


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
    email = EmailField('Email', validators=[DataRequired()], render_kw={"class": "input", "placeholder":"Your Email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"class": "input", "placeholder": "Your Password"})
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

publisher_docs = mongo.db.publisher.find({})
choices = [(publisher["_id"], publisher["label"]) for publisher in publisher_docs ]

class AddGameForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()], render_kw={"class": "input", "placeholder": "Enter the title of the Game"})
    platform = StringField('Platform', validators=[DataRequired()], render_kw={"class": "input", "placeholder": "Enter the Platform the Game is on"})
    year = StringField('Year', validators=[DataRequired()], default="0000", render_kw={"class": "input", "placeholder": "Release Year"})
    genre = StringField('Genre', validators=[DataRequired()], default="unknownGenre", render_kw={"class": "input", "placeholder": "Enter Genre"})
    publisher = SelectField('Publisher', validators=[DataRequired()], choices=choices, render_kw={"class": "input"})
    submit = SubmitField('Add Game', render_kw={"class": "button is-block is-info is-large is-fullwidth"})

game_docs = mongo.db.games.find({})
game_choices = [(game["_id"], game['label']) for game in game_docs]

class ReviewForm(FlaskForm):
    """
    fields:
        title, review_text, game, submit
    Game is extracted from database and attached to player.
    """
    title = StringField('title', validators=[DataRequired()], render_kw={"class": "input", "placeholder": "Title"})
    review_text = TextAreaField('text', validators=[InputRequired()], render_kw={"class": "input", "placeholder": "Your Review Here", "minlength": "2", "maxlength":"2000", "rows":"4", "cols":"70"} )
    game = SelectField('Game', validators=[DataRequired(), InputRequired()], description='Select Game to be reviewed', render_kw={"class": "input"}, choices = game_choices)
    submit = SubmitField('Add Review', render_kw={"class": "button is-block is-info is-large is-fullwidth"})

