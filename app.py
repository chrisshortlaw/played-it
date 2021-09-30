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


app = Flask(__name__)
app.config.from_object(Config)
played_it_db.db_connect()
# login_manager = LoginManager()

# user = 'chris'
# team = 'team_of_me'
# endpoint = f"https://cloud.terminusdb.com/{team}/"
# client = WOQLClient(endpoint)


# client.connect(user=user, team=team, db="new_test_db", use_token=True)


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
    form = LoginForm()
    if form.validate_on_submit():
        user_list = list(played_it_db.client.query_document({"@type": "User", "name" : f"{form.username.data}"}))
        if len(user_list) == 1:
            if user_list[0]['password'] == f"{form.password.data}":
                session['username'] = user_list[0]['name']
                flash(f"{user_list[0]['name']} has successfully logged in!")
                return redirect(url_for('main'))
            else:
                flash('Incorrect Password')
        else:
            flash('Username Incorrect')
    return render_template("login.html", title="Sign In", form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit:
        user_email = form.email.data
        existing_email_check = played_it_db.client.get_document(user_email)
        if existing_email_check:
            flash('User Account exists. Have you forgot your password?')
            return render_template("register.html", title="Registration", form=form)
        else:
            user_name = form.username.data

            user_pass = generate_password_hash(str(form.password.data), method='pbkdf2:sha256', salt_length=16)

            new_user = User(email=user_email, name=user_name, _password=user_pass, played_games=[], reviews=[])

            try:
                played_it_db.client.insertDocument(new_user)
            except Exception as e:
                print(f'Error loading new User to database. Please try again. Error: {e}.')
                return render_template("register.html", title="Registration", form=form)
            else:
                flash(f'New User: {user_name} has been successfully registered.')
                session['username'] = user_name
                return redirect(url_for('main'))
    return render_template("register.html", title="Registration", form=form)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
  
