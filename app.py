from flask import Flask, flash, render_template, redirect, request, session, url_for
import flask_wtf
from terminusdb_client import WOQLClient, WOQLQuery 
import os
if os.path.exists("env.py"):
    import env
# from models import User
from forms import LoginForm, RegisterForm
from config import Config
from models import played_it_db, User
# from flask-login import LoginManager
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Set


app = Flask(__name__)
app.config.from_object(Config)
played_it_db.db_connect()
# login_manager = LoginManager()


@app.route("/")
def main():
    """
    grabs documents from db and displays on main page
    """
    documents = played_it_db.client.get_document('Publisher/10tacle_studios')
    if 'username' in session:
        flash(f'Logged in as {session["username"]}')
    else:
        flash('You are not logged in.')
    return render_template("main.html", title="Main", documents=documents)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    TODO: Add server side validation (email etc.)
    """
    form = LoginForm()
    if form.validate_on_submit():
        user_id = str(form.username.data).replace('@','%40')
        user_list = list(played_it_db.client.query_document({"@type": "User", "@id": f"User/{user_id}"}))
        print(user_list)
       # user_list = list(played_it_db.client.query_document({"@type": "User", "name" : f"{form.username.data}"}))
        if len(user_list) == 1:
            if check_password_hash(user_list[0]['_password'], form.password.data):
                session['username'] = user_list[0]['name']
                flash(f"{user_list[0]['name']} has successfully logged in!")
                return redirect(url_for('main'))
            else:
                flash('Incorrect Password')
        else:
            flash('Username Incorrect')
    else:
        print(form.errors)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    """
    TODO: Add server-side validation.
    """
    form = RegisterForm()
    
    if form.validate_on_submit():

        user_email = played_it_db.client.query_document({"@type": "User", "email": f"{form.email.data}"})

        if len(list(user_email)) > 1:
            flash('User Account exists. Have you forgotten your password?')
            return render_template("register.html", title="Registration", form=form)
        else:

            user_pass = generate_password_hash(str(form.password.data), method='pbkdf2:sha256', salt_length=16)

            new_user = User(email=form.email.data, name=form.username.data, _password=user_pass, played_games=set(), reviews=set())

            try:
                played_it_db.client.insert_document(new_user)
            except Exception as e:
                print(f'Error loading new User to database. Please try again. Error: {e}.')
                return render_template("register.html", title="Registration", form=form)
            else:
                flash(f'New User: {form.username.data} has been successfully registered.')
                session['username'] = form.username.data 
                return redirect(url_for('main'))
    else:
        print('Registration form did not validate')
        print(form.errors)
    return render_template("register.html", title="Registration", form=form)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
  
