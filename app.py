from flask import Flask, flash, render_template, redirect, request, session, url_for
import flask_wtf
from terminusdb_client import WOQLClient, WOQLQuery 
import os
if os.path.exists("env.py"):
    import env
#from models import User
from forms import LoginForm, RegisterForm
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

user = 'chris'
team = 'team_of_me'
endpoint = f"https://cloud.terminusdb.com/{team}/"
client = WOQLClient(endpoint)


client.connect(user=user, team=team, db="new_test_db", use_token=True)


@app.route("/")
def main():
    documents = client.get_document('Publisher/10tacle_studios')
    print(documents)
    return render_template("main.html", title="Main", documents=documents)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
    #    username = request.form.get('username')
    #   NOTE: Remove this Print Statement
        print("Login Form Post Succesful")
    return render_template("login.html", title="Sign In", form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        pass

    return render_template("register.html", title="Registration", form=form)
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
    
