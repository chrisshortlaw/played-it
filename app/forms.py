#!python3

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo, InputRequired, Email, Length
from wtforms.fields.html5 import EmailField
from bson.objectid import ObjectId

# TODO: INSERT DATABASE IMPORT HERE
from app.database_mongo import mongo


# CUSTOM VALIDATORS
def check_username(form, field):
    message = f"Username in use. Please choose a different."
    user = mongo.db.users.find_one({ 'name' : field.data })
    if user is not None: 
        raise ValidationError(message)

def check_email(form, field):
    message = "Email already registered. Please log in to continue."
    user = mongo.db.users.find_one({ 'email': field.data })

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
    email = EmailField('Email', 
            validators=[DataRequired()], 
            render_kw={"class": "input", 
                "placeholder":"Your Email"})
    password = PasswordField('Password', 
            validators=[DataRequired()], 
            render_kw={"class": "input", 
                "placeholder": "Your Password"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In', 
            render_kw={"class": "button is-block is-info is-large is-fullwidth"})
    

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
    username = StringField('Username', 
            validators=[DataRequired(), check_username],
            render_kw={"class": "input", 
                "placeholder":"Enter a Username"}
            )
    password = PasswordField('Password',
            validators=[InputRequired(), DataRequired()], 
            render_kw={"class": "input", 
                "placeholder": "Enter a Password"}
            )
    confirm = PasswordField('ConfirmPassword', 
            validators=[DataRequired(), 
                EqualTo('password', 
                    message='Passwords must match')], 
            render_kw={"class": "input", 
                "placeholder": "Confirm Password"}
            )
    email = StringField('Email', 
            validators=[DataRequired(), 
                Email(message='Invalid Email Address'), check_email], 
            render_kw={"class":"input", 
                "placeholder": "Enter Your Email"}
            )
    submit = SubmitField('Register', 
            render_kw={"class": "button is-block is-info is-large is-fullwidth"})


publisher_docs = mongo.db.publisher.find({})
choices = [(publisher["_id"], publisher["label"]) for publisher in publisher_docs ]

class AddGameForm(FlaskForm):
    title = StringField('title', 
            validators=[DataRequired()], 
            render_kw={"class": "input", 
                "placeholder": "Enter the title of the Game"}
            )
    platform = StringField('Platform', 
            validators=[DataRequired()], 
            render_kw={"class": "input", 
                "placeholder": "Enter the Platform the Game is on"})
    year = StringField('Year', 
            validators=[DataRequired()], 
            default="0000", 
            render_kw={"class": "input", 
                "placeholder": "Release Year"}
            )
    genre = StringField('Genre', 
            validators=[DataRequired()], 
            default="unknownGenre", 
            render_kw={"class": "input", 
                "placeholder": "Enter Genre"})
    publisher = SelectField('Publisher', 
            validators=[DataRequired()], 
            choices=choices, 
            render_kw={"class": "input"}
            )
    submit = SubmitField('Add Game', 
            render_kw={"class": "button is-block is-info is-large is-fullwidth"})


class ReviewForm(FlaskForm):
    """
    fields:
        title, review_text, game, submit
    Game is extracted from database and attached to player.
    """
    title = StringField('title', 
            validators=[DataRequired()], 
            render_kw={"class": "input", 
                "placeholder": "Title"}
            )
    review_text = TextAreaField('text', 
            validators=[InputRequired()], 
            render_kw={"class": "input", 
                "placeholder": "Your Review Here", 
                "minlength": "2", 
                "maxlength":"2000", 
                "rows":"4", 
                "cols":"70"}
            )
    submit = SubmitField('Add Review', 
            render_kw={"class": "button is-block is-info is-large is-fullwidth"})


games = mongo.db.games.find({})
game_choices = [(game.get('_id'), game.get('label')) for game in games]


class UserReviewForm(FlaskForm):
    title = StringField('title', 
            validators=[DataRequired()], 
            render_kw={"class": "input", 
                "placeholder": "Title"}
            )
    review_text = TextAreaField('text', 
            validators=[InputRequired()], 
            render_kw={"class": "input", 
                "placeholder": "Your Review Here", 
                "minlength": "2", 
                "maxlength":"2000", 
                "rows":"4", 
                "cols":"70"}
            )
    game = SelectField('game', validators=[DataRequired()], choices=game_choices, render_kw={"class": "input"})
    submit = SubmitField('Add Review', 
            render_kw={"class": "button is-block is-info is-large is-fullwidth"})
    

class EditProfileForm(FlaskForm):
    username = StringField('username', 
            validators=[DataRequired()], 
            render_kw={"class": "input"})
    bio = TextAreaField('Bio', 
            validators=[Length(min=0, 
                max=500, 
                message='Review cannot be longer than 500 characters')], 
            render_kw={"class": "input", 
                "alt": ""})
    email = EmailField('Email',
            validators=[DataRequired()],
            render_kw={"class": "input"})
    submit = SubmitField('Edit Profile', 
            render_kw={"class": "button is-block is-info is-large is-fullwidth"})

    def __init__(self, current_username, current_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_username = current_username
        self.current_email = current_email

    def validate_user(self, username):
        if username.data != self.current_username:
            user = mongo.db.users.find_one({"name": username.data})
            if user is not None:
                raise ValidationError('Please choose a different username')

    def validate_email(self, email):
        if email.data != self.current_email:
            user = mongo.db.users.find_one({"email": email.data})
            if user is not None:
                raise ValidationError('Email is in use. Please choose a different email or login.')


class EditReviewForm(FlaskForm):
    title = StringField('title', 
            validators=[DataRequired()], 
            render_kw={"class":"input"})
    review_text = TextAreaField('text', 
            validators=[DataRequired()], 
            render_kw={"class": "input"})
    submit = SubmitField('Edit Review', 
            render_kw={"class": "button is-block is-info is-large is-fullwidth"})
 
class AddGameRef(FlaskForm):
    submit = SubmitField('Add This Game', render_kw={ "class": "button is-medium is-primary" })


class DeleteGame(FlaskForm):
    submit = SubmitField('Delete This Game', render_kw={"class": "button is-medium is-danger" })


class DeleteReview(FlaskForm):
    submit = SubmitField('Delete This Review', render_kw={"class": "button is-medium is-danger"})
