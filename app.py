from datetime import datetime, timezone
import re
from typing import Set
import os
if os.path.exists("env.py"):
    import env


from flask import Flask, flash, render_template, redirect, request, session, url_for
import flask_wtf
from terminusdb_client import WOQLClient, WOQLQuery 
from forms import LoginForm, RegisterForm, AddGameForm, ReviewForm 
# from flask-login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import User, Game, Review
from database import played_it_db

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
        user_list = list(played_it_db.client.query_document({"@type": "User", "email": f"{form.email.data}"}))
        if len(user_list) == 1:
            if check_password_hash(user_list[0]['_password'], form.password.data):
                session['username'] = user_list[0]['name']
                session['email'] = user_list[0]['email']
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
                session['email'] = form.email.data
                return redirect(url_for('main'))
    else:
        print('Registration form did not validate')
        print(form.errors)
    return render_template("register.html", title="Registration", form=form)


@app.route('/user/<username>')
def profile(username):
    """
    If statement prevents access to profile unless logged in. Consider using session cookie to hold boolean value - .is_logged_in
    """
    if 'username' in session:  
        if session['username'] == username:       
            try:
                user = list(played_it_db.client.query_document({"@type": "User", "name": username}))[0]
            except Exception as e: 
                print(e)
                flash('Email Incorrect')
                return redirect(url_for('login'))
            else:
                posts = [{'author': user['name'], 'body': 'Test Post 1'}, {'author': user['name'], 'body': 'Test Post 2'}]
                games = []
                if "played_games" in user:
                    for played_game in user["played_games"]:
                        games.append(played_it_db.client.get_document(played_game))
                else:
                    pass
                return render_template("user.html", user=user, posts=posts, games=games)
        else:
            flash('Oops. Something went wrong. Please log in to continue')
            session.pop('username', default=None)
            return redirect(url_for('login'))
    else:
        flash('Please log in to access user profile')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username')
    session.pop('email')
    flash('Successfully Logged Out.')
    return redirect(url_for('main'))


@app.route('/games')
def games():
    games = played_it_db.client.get_documents_by_type('Game')
    return render_template('browse_games.html', games=games)


@app.route('/games/<game_name>')
def game_page(game_name):
    games = list(played_it_db.client.query_document({"@type": "Game", "name": game_name}))
    pub_id = games[0]['publisher'] 
    print(pub_id)
    publisher = played_it_db.client.get_document(pub_id)
    print(publisher)
    return render_template('game.html', game_name=game_name, games=games, publisher=publisher)


@app.route('/user/<username>/add_game', methods=['GET', 'POST'])
def add_game(username):
    if 'username' in session:
        # As above, this checks if the session cookie has a username key
        # if not, send the user to a login screen.
        form = AddGameForm()
        # is this try...except block necessary?
        try:
            current_user = played_it_db.client.query_document({"@type": "User", "name":username})
        except Exception as e:
            print(e)
            flash('Oops. We encountered a problem. Please log in to continue')
            session.pop('username')
            session.pop('email')
            return redirect(url_for('login'))
        else:
            
            if form.validate_on_submit():
                label = form.title.data
                platform = form.platform.data
                year = int(form.year.data)
                genre = form.genre.data
                publisher = form.publisher.data
                 
                # Check if Publisher is in database
                publisher_id_regex = re.compile('Publisher/.*')
                if publisher_id_regex.fullmatch(publisher):
                    # if @id (a Lexical Key) is passed via the form
                    # retrieve the relevant document object
                    publisher_doc = played_it_db.get_doc_obj({"@id":publisher})
                else:
                    publisher_doc = played_it_db.get_doc_obj({"@type": "Publisher", "name": publisher.lower().replace(" ", "_") })
                    if publisher_doc is None:
                        publisher_doc = set()
         
                new_game = Game.create_game(label=label, platform=platform, year=year, genre=genre, publisher=set([publisher_doc]))
                
                try:
                    played_it_db.client.insert_document(new_game, commit_msg=f"New Game Added by {session['username']}")
                except Exception as e:
                    print(e)
                    flash('Failed to add game. Please try again')
                    return redirect(url_for('add_game', username=session['username']))
                flash('Game Added Successfully')
                return redirect(url_for('profile', username=session['username']))
            # else block for when form does not validate or for GET request
            else:
                return render_template('add_game.html', username=username, form=form)
    else:
        flash('Please log in to continue')
        return redirect(url_for('login'))


@app.route('/games/<game_name>/add_review', methods=['GET', 'POST'])
def add_review(game_name):

    if session:
        form = ReviewForm()
        if form.validate_on_submit():
            username = session['username']
            user_id = played_it_db.client.query_document({"@type": "User", "name": username}) 
            game_id= Set(played_it_db.client.query_document({"@type": "Game", "name": game_name}))
            pub_date = datetime.now(timezone.utc)
            
            new_review = Review(title=form.title, author=username, text=form.text, game=game_id, pub_date=pub_date)
            added_reviews = played_it_db.client.insert_document(new_review)
            for review_id in added_reviews:
                update_user = user_id["reviews"].add(review_id)
                played_it_db.client.update_document(update_user)
            
            flash('Review Successfully Added')
            return redirect(url_for('profile', username=username))
        else:
            flash('Error with form validation. Please try again.')

        return render_template('add_review.html', game_name=game_name)

    else:
        flash('Please Log In to post a review')
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

