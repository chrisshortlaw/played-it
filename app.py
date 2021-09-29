from flask import Flask, flash, render_template, redirect, request, session, url_for
import flask_wtf
from terminusdb_client import WOQLClient, WOQLQuery 
import os
if os.path.exists("env.py"):
    import env
#from models import User
from forms import LoginForm, RegisterForm
from config import Config
from models import played_it_db


app = Flask(__name__)
app.config.from_object(Config)
played_it_db.db_connect()

# user = 'chris'
# team = 'team_of_me'
# endpoint = f"https://cloud.terminusdb.com/{team}/"
# client = WOQLClient(endpoint)


# client.connect(user=user, team=team, db="new_test_db", use_token=True)


@app.route("/")
def main():
    documents = played_it_db.client.get_document('Publisher/10tacle_studios')
    print(documents)
    return render_template("main.html", title="Main", documents=documents)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_list = list(played_it_db.client.query_document({"@type": "User", "name" : f"{form.username.data}"}))
        print(user_list)
        if len(user_list) == 1:
            if user_list[0]['password'] == f"{form.password.data}":
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
    if request.method == 'POST':
        pass

    return render_template("register.html", title="Registration", form=form)
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
    
