from datetime import datetime, timezone
import re
from typing import Set
import os
if os.path.exists("env.py"):
    import env

from flask import Flask, flash, render_template, redirect, request, session, url_for
import flask_wtf
from terminusdb_client import WOQLClient, WOQLQuery 
from terminusdb_client.woqlschema import WOQLSchema
from forms import LoginForm, RegisterForm, AddGameForm, ReviewForm 
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
#from models import User, Game, Review, ReviewList, GameList
from database import played_it_db

app = Flask(__name__)
app.config.from_object(Config)
played_it_db.db_connect()


data_schema = WOQLSchema()
data_schema.from_db(played_it_db.client)


User = data_schema.object.get('User')
Game = data_schema.object.get('Game')
Review = data_schema.object.get("Review")


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
                session['@id'] = user_list[0]['@id']
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


            # Instantiate User with two dummy forwardrefs. 
            fake_review_raw = played_it_db.client.get_document("Review/0afa3d1539a937854953a4644fbdd00412b44a6be852369f96f2cdcd84d6da43")
            fake_game_raw = played_it_db.client.get_document("Game/fake_game_Wii")
            # Import Objects must be passed a list or iterable.
            fake_game = data_schema.import_objects([fake_game_raw])
            fake_review = data_schema.import_objects([fake_review_raw])


            new_user = User(email=form.email.data, name=form.username.data, _password=user_pass, games=set(fake_game), reviews = set(fake_review))

            try:
                played_it_db.client.update_document(new_user)
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
                # TODO: Model One to Many relationship with ForwardRef
                user = list(played_it_db.client.query_document({"@type": "User", "name": username}))[0]
                user_reviews = played_it_db.client.get_document(user.get("reviews"))
                user_games = played_it_db.client.get_document(user.get("games", "wrong key games"))
                print(user.get("reviews"))
                print(user)

            except Exception as e: 
                print(f"profile func: {e}")
                flash('Error. Please log in to proceed.')
                return redirect(url_for('login'))
            else:
                return render_template("user.html", user=user, user_reviews=[user_reviews], games=[user_games])
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
    pub_id = games[0]['publisher'][0] 
    print(f"game_page func: {pub_id}")
    publisher = played_it_db.client.get_document(pub_id)
    return render_template('game.html', game_name=game_name, games=games, publisher=publisher)


@app.route('/user/<username>/add_game', methods=['GET', 'POST'])
def add_game(username):
    if 'username' in session:
        # As above, this checks if the session cookie has a username key
        # if not, send the user to a login screen.
        form = AddGameForm()
        # is this try...except block necessary?
        try:
            current_user = played_it_db.get_doc_obj({"@type": "User", "name":username})
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
                    # get_doc_obj takes a dict as argument
                    print(f"Add_game: if block fired")
                    publisher_raw = played_it_db.client.get_document(publisher)
                    publisher_doc = data_schema.import_objects([publisher_raw])
                else:
                    print(f"Add_game: else block fired")
                    publisher_raw = played_it_db.client.query_document({"@type": "Publisher", "name": publisher.lower().replace(" ", "_") })
                    publisher_doc = data_schema.import_objects(publisher_raw)
                # a snake_case name for new_game for easy querying
                new_game_name = label.replace(" ", "_").lower() 
                new_game = Game(label=label, name=new_game_name, platform=platform, year=year, genre=genre, publisher=set(publisher_doc))


                try:
                    played_it_db.client.update_document([new_game], commit_msg=f"New Game Added by {session['username']}")
                except Exception as e:
                    print(e)
                    flash('Failed to add game. Please try again')
                    return redirect(url_for('add_game', username=session['username']))
                flash('Game Added Successfully')

                # Add new game to Users list of games
                new_user_game_raw = played_it_db.client.query_document({"@type": "Game", "label": label})
                new_user_game = data_schema.import_objects([new_user_game_raw])
                current_user_games = current_user['games']

                print(f"AddGame - current_user_games: {current_user_games}")

                current_user_games.append(new_user_game_raw["@id"])
                current_user["games"] = current_user_games
                current_user_doc = data_schema.import_objects(current_user)

                played_it_db.client.update_document(current_user_doc)
                
                return redirect(url_for('profile', username=session['username']))
            # else block for when form does not validate or for GET request
            else:
                return render_template('add_game.html', username=username, form=form)
    else:
        flash('Please log in to continue')
        return redirect(url_for('login'))


@app.route('/user/<username>/add_review', methods=['GET', 'POST'])
def add_review(username):

    if session:
        form = ReviewForm()
        if form.validate_on_submit():
            username = session['username']
            user = played_it_db.get_doc_obj({"@type": "User", "name": username})
            print(user)
            print(user.name)
            pub_date = str(datetime.now(timezone.utc))
            game = played_it_db.client.get_document(form.game.data)
            #game = played_it_db.get_doc_obj({"@id": form.game.data})
            
            new_review = Review(title=form.title.data, author=username, _author=session['@id'], text=form.review_text.data, game=game['label'], _game_id=form.game.data, pub_date=pub_date)

            try:
                played_it_db.client.insert_document([new_review])
            except Exception:
                print(Exception)
                flash("Review not posted. Could not connect to database.")
                redirect(url_for('profile', username=username))
            else:            
                flash('Review Successfully Added')
                return redirect(url_for('profile', username=username))
        else:
            flash('Error with form validation. Please try again.')

        return render_template('add_review.html', username=username, form=form)

    else:
        flash('Please Log In to post a review')
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

