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
from flask_pymongo import PyMongo

from app.database_mongo import mongo
from app.models import User, Game, Review, ReviewList, GameList
from app.forms import LoginForm, RegisterForm, ReviewForm, AddGameForm, EditProfileForm, EditReviewForm 

@app.route("/")
def main():
    """
    grabs documents from db and displays on main page
    """
    if 'username' in session:
        flash(f'Logged in as {session["username"]}')
    else:
        flash('You are not logged in.')
    return render_template("main.html", title="Main")


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        user_doc = mongo.db.users.find_one({"email": f"{ form.email.data }"})
        if user_doc.get("email") is not None:
            if check_password_hash(user_doc.get('_password'),
                                    form.password.data):
                current_user = User.from_mongo(**user_doc)
                session['username'] = current_user.name
                session['email'] = current_user.email 
                session['_id'] = str(current_user._id)
                flash(f"{session['username']} has successfully logged in!")
                return redirect(url_for('profile', user=current_user))
        else:
            flash('Username Incorrect')
            redirect(url_for('login'))
    return render_template("login.html", title="Sign In", form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    """
    TODO: Add server-side validation.
    """
    if session.get('username') is not None:
        return redirect(url_for('profile',
            username=session.get('username')))
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User.add_user(
                password=form.password.data,
                name = form.username.data,
                email = form.email.data
                )
        flash('Registration Successful')
        session['username'] = new_user.name
        session['email'] = new_user.email
        session['_id'] = str(new_user._id)
        return redirect(url_for('profile', 
            username=session.get('username')))
    return render_template("register.html", 
                title="Registration", 
                form=form)
            
@app.route('/user/<username>')
def profile(username):
    """
    If statement prevents access to profile unless logged in. Consider using session cookie to hold boolean value - .is_logged_in
    """
    if session.get('username') is not None:      
        current_user = User.from_mongo(**mongo.db.users.find_one({"name": session.get('username')}))
        return render_template("user_profile.html", title="My Profile", user=current_user)
    else:
        flash('Please log in to access user profile')
        return redirect(url_for('login'))


@app.route('/user/<username>/edit_profile', methods=['GET', 'POST'])
def edit_profile(username):
    form = EditProfileForm()
    user = User.from_mongo(**mongo.db.users.find_one({"email": session.get('email')}))
    if form.validate_on_submit():
        pass
    elif request.method == 'GET':
        pass


@app.route('/logout')
def logout():
    session.pop('username')
    session.pop('email')
    session.pop('_id')
    flash('Successfully Logged Out.')
    return redirect(url_for('main'))


@app.route('/games')
def games():
    """
    Returns a list of documents in the games collection.
    Second query grabs a list of publishers.
    """
    games = mongo.db.games.find({})
    return render_template('browse_games.html', games=games)


@app.route('/games/<game_name>')
def game_page(game_name):
    game = Game.from_mongo(**mongo.db.games.find_one({"name": game_name}))
    if session.get('username') is not None:
        user = User.from_mongo(**mongo.db.users.find_one({"name": session.get('username')}))
    else:
        user = None 
    # TODO: Rewrite this to account for publisher info in game document
    return render_template('game.html', game_name=game_name, game=game, user=user)


@app.route('/user/<username>/add_game', methods=['GET', 'POST'])
def add_game(username):
    if 'username' in session:
        # As above, this checks if the session cookie has a username key
        # if not, send the user to a login screen.
        form = AddGameForm()
        # is this try...except block necessary?
        
        current_user = User.from_mongo(**mongo.db.users.find_one({"name": session.get('username')}))
        if current_user is None:
            flash('Oops. We encountered a problem. Please log in to continue')
            session.pop('username')
            session.pop('email')
            session.pop('_id')
            return redirect(url_for('login'))
        else:
            if form.validate_on_submit():
                label = form.title.data
                platform = form.platform.data
                year = int(form.year.data)
                genre = form.genre.data
                publisher = form.publisher.data
                # ensure publisher is selectfield with id as values 
                new_game_name = label.replace(" ", "_").lower() 
                new_game = Game.add_game(label=label, 
                        platform=platform, 
                        year=year, 
                        genre=genre, 
                        publisher=publisher)
                new_game_ref = new_game.create_game_ref() 

                # Add new game to Users list of games
                current_user.game_list.append(new_game_ref) 
                # Update User on the database
                current_user.update_user()    
                flash('Game Added Successfully')
                return redirect(url_for('profile', 
                    username=session['username']))
            else:
                return render_template('add_game.html', 
                                username=username, 
                                form=form)
    else:
        flash('Please log in to continue')
        return redirect(url_for('login'))


@app.route('/game/<game_name>/add_review', methods=['GET', 'POST'])
def add_review(game_name):
    game = Game.from_mongo(**mongo.db.games.find_one({ "name": game_name }))
    username = session['username']
    user_dict = mongo.db.users.find_one({"name": username})
    user = User.from_mongo(**user_dict)

    if session:
        form = ReviewForm()
        if form.validate_on_submit():
            author_ref = user.create_author_ref()
            pub_date = str(datetime.now(timezone.utc))
            game_ref = game.create_game_ref()
            
            new_review = Review.add_review(
                    name=form.title.data,
                    game=game.label,
                    author=user.name, 
                    author_id=user._id, 
                    text=form.review_text.data, 
                    game_id=game._id, 
                    pub_date=pub_date, 
                    game_ref=game_ref, 
                    author_ref=author_ref
                    )
            flash('Review Successfully Posted')
            review_ref = new_review.create_review_ref()
            game.reviews.append(review_ref)
            game.update_game()
            user.reviews.append(review_ref)
            user.update_user()
            return redirect(url_for('review', review_id=new_review._id))
        return render_template('add_review.html', game_name=game_name, user=user, game=game, form=form)

    else:
        flash('Please Log In to post a review')
        return redirect(url_for('login'))

@app.route('/user/<username>/games', methods=['GET'])
def user_games(username):
    if session.get('username') is None:
        flash('Please log in to view content')
        return redirect(url_for('login'))
    elif session.get('username') == username:
        # TODO: Restructure Data Model top permit holding game data in User collection for optimised querying.
        # Use of extended reference in User model allows for simpler queries to retrieve games and other user data
        current_user = User.from_mongo(**mongo.db.users.find_one({"_id": ObjectId(session.get("_id"))  }))
        return render_template('user_games.html', games=current_user.game_list)
    # TODO: Refactor and permit a public profile.


@app.route('/user/<username>/reviews', methods=['GET'])
def user_reviews(username):

    user = User.from_mongo(**mongo.db.users.find_one({"_id": ObjectId(session['_id'])}))
    return render_template('user_reviews.html', user=user)


@app.route('/review/<review_id>', methods=['GET'])
def review(review_id):
    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id) })
    return render_template('review.html.jinja', review=review)


@app.route('/review/<review_id>/edit_review', methods=['GET', 'POST'])
def edit_review(review_id):
    form = EditReviewForm()
    review = Review.from_mongo(**mongo.db.reviews.find_one({ "_id": ObjectId(review_id) }))
    user_email = session.get('email')
    if form.validate_on_submit():
        review.name = form.title.data
        review.text = form.review_text.data
        review.update_review()
    elif request.method == "GET":
        form.title.data = review.name
        form.review_text.data = review.text
    return render_template('edit_review.html', title='Edit Review', form=form)

