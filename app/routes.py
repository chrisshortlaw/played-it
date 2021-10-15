from app import app
from flask import Flask, flash, render_template, redirect, request, session, url_for
import flask_wtf
from datetime import datetime, timezone
import re
from typing import Set
import os
import dataclasses

from werkzeug.security import check_password_hash, generate_password_hash

from bson.objectid import ObjectId
from bson.son import SON
from dacite import from_dict

from app.database_mongo import mongo
from app.models import User, Game, Review, ReviewList, GameList
from app.forms import LoginForm, RegisterForm, ReviewForm, AddGameForm 

@app.route("/")
def main():
    """
    grabs documents from db and displays on main page
    """
    documents = mongo.db.publisher.find({})
    if 'username' in session:
        flash(f'Logged in as {session["username"]}')
    else:
        flash('You are not logged in.')
    return render_template("main.html", title="Main", documents=documents)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        user_doc = mongo.db.users.find_one({"email": f"{ form.email.data }"})
        if user_doc.get("email") is not None:
            if check_password_hash(user_doc['_password'], form.password.data):
                session['username'] = user_doc['name']
                session['email'] = user_doc['email']
                session['_id'] = user_doc['_id']
                flash(f"{user_doc['name']} has successfully logged in!")
                return redirect(url_for('main'))
        else:
            flash('Username Incorrect')
            redirect(url_for('login'))
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

        user_email = mongo.db.users.find_one({"email": f"{form.email.data}"}) 

        if user_email is not None:
            flash('User Account exists. Have you forgotten your password?')
            return render_template("register.html", title="Registration", form=form)
        else:
            # dataclass used to check type and ensure encapsulation of data
            try:
                new_user = User.create_user(password=form.password.data, email=form.email.data, name=form.username.data)
            except Exception as e:
                print(f"failed to create user: {e}")
            else:
                try:
                    mongo.db.user.insert_one(dataclasses.asdict(new_user))
                except Exception as e:
                    print(f'Error loading new User to database. Please try again. Error: {e}.')
                    return render_template("register.html", title="Registration", form=form)
                else:
                    flash(f'New User: {form.username.data} has been successfully registered.')
                    session['username'] = new_user.name 
                    session['email'] = new_user.email
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
    if session.get(username) is not None:      
        try:
            user = mongo.db.users.find_one({"name": username})                
            if user.get("reviews") is not None:
                user_reviews = mongo.db.reviews.find([{"_id": ObjectId(review)} for review in user.get("reviews")])               
            else:
                # TODO: Insert a placeholder id/reference here.
                user_reviews = []
            if user.get("games") is not None:
                user_games = mongo.db.games.find([{"_id": ObjectId(game)} for game in user.get("game_list")])
            else:
                user_games = []

        except Exception as e: 
            print(f"profile func: {e}")
            flash('Error. Please log in to continue')
            return redirect(url_for('login'))
        else:
            return render_template("user.html", user=user, user_reviews=user_reviews, games=user_games)
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
    """
    Returns a list of documents in the games collection.
    Second query grabs a list of publishers.
    """
    games = mongo.db.games.find({})
    games_with_embedded_publishers = []
    for game in games:
        publisher = mongo.db.publisher.find_one({"_id": ObjectId(game.get("publisher"))})
        game["pub_doc"] = publisher
        games_with_embedded_publishers.append(game)

    print(games_with_embedded_publishers[0])
    return render_template('browse_games.html', games=games_with_embedded_publishers)


@app.route('/games/<game_name>')
def game_page(game_name):
    game = mongo.db.games.find_one({"name": game_name})
    if game.get('publisher') is not None:
        pub_id = game.get('publisher') 
        print(f"game_page func: {pub_id}")
        publisher = mongo.db.publisher.find_one({"_id": ObjectId(pub_id)})
    return render_template('game.html', game_name=game_name, game=game, publisher=publisher)


@app.route('/user/<username>/add_game', methods=['GET', 'POST'])
def add_game(username):
    if 'username' in session:
        # As above, this checks if the session cookie has a username key
        # if not, send the user to a login screen.
        form = AddGameForm()
        # is this try...except block necessary?
        
        current_user = mongo.db.user.find_one({"name": username})
        if current_user is None:
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
                publisher = form.publisher.value
                # ensure publisher is selectfield with id as values 
                new_game_name = label.replace(" ", "_").lower() 
                new_game = Game(label=label, name=new_game_name, platform=platform, year=year, genre=genre, publisher=publisher)


                try:
                    added_game = mongo.db.games.insert_one(dataclasses.asdict(new_game))
                except Exception as e:
                    print(e)
                    flash('Failed to add game. Please try again')
                    return redirect(url_for('add_game', username=session['username']))
                else:
                    flash('Game Added Successfully')
                    # write from_dict function to instantiate User from dict in mongodb
                    # Add new game to Users list of games
                    current_user_games = current_user['game_list']
                    # check if this return value is correct
                    current_user_games.append(added_game.inserted_id)

                    current_user['game_list'] = current_user_games

                    mongo.db.users.update_one({ "$addToSet" : {"game_list": ObjectId(added_game.inserted_id)}})
                    

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
            user = mongo.db.users.find_one({"name": username})
            pub_date = str(datetime.now(timezone.utc))
            game = mongo.db.game.find_one({"_id": form.game.data})
            #game = played_it_db.get_doc_obj({"@id": form.game.data})
            
            new_review = Review(title=form.title.data, author=username, _author=user['@id'], text=form.review_text.data, game=game['label'], _game_id=form.game.data, pub_date=pub_date)

            try:
                mongo.db.reviews.insert_one(dataclasses.asdict(new_review))
            except Exception as e:
                print(f"add_review Exception: {e}")
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

