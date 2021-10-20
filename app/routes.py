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
                return redirect(url_for('profile', username=current_user.name))
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
    user = session.get('username')
    if user is not None:      
        if user == username:
            current_user = User.from_mongo(**mongo.db.users.find_one({"name": session.get('username')}))
            return render_template("user_profile.html", title="My Profile", user=current_user)
        else:
            user = User.from_mongo(**mongo.db.users.find_one({'name': username}))
            return render_template("user_profile.html", title=f"{user.name}'s Profile", user=user)
    else:
        flash('Please log in to access user profile')
        return redirect(url_for('login'))


@app.route('/user/<username>/edit_profile', methods=['GET','POST'])
def edit_profile(username):
    # TODO: Finish this.
    session_name = session.get('username')
    if session_name is not None and session_name == username: 
        user = User.from_mongo(
                **mongo.db.users.find_one(
                    {"email": session.get('email')}
                    )
                )
        form = EditProfileForm(current_username=user.name, current_email=user.email)
        if form.validate_on_submit():
            user.email = form.email.data
            user.name = form.username.data
            user.bio = form.bio.data
            user.update_user()
            flash('Profile Updated Successfully')
            return redirect(url_for('profile', username=user.name))

        elif request.method == 'GET':
            form.email.data = user.email
            form.username.data = user.name
            form.bio.data = user.bio
        return render_template('edit_profile.html.jinja', 
                                    form=form, 
                                    user=user, title="Edit Profile")
    elif session_name != username:
        return redirect(url_for('profile', username=session_name))
    else:
        flash('Please log in to edit your profile')
        return redirect(url_for('login'))


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
    """
    Users can add a game and have a reference to this game appear on their user profile.
    """

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
    """
    Adds a review and updates the user and game objects, accordingly.
    """
    game = Game.from_mongo(**mongo.db.games.find_one({ "name": game_name }))
    username = session.get('username')
    if username is not None:
        user_dict = mongo.db.users.find_one({"name": username})
        user = User.from_mongo(**user_dict)

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
            game_ref = game.create_game_ref()
            user.reviews.append(review_ref)
            if game_ref not in user.game_list:
                user.game_list.append(game_ref)
            user.update_user()
            return redirect(url_for('review', review_id=new_review._id))
        return render_template('add_review.html', game_name=game_name, user=user, game=game, form=form)
    else:
        flash('Please log in to post a review')
        return redirect(url_for('login'))


@app.route('/user/<username>/games', methods=['GET'])
def user_games(username):
    if session.get('username') is None:
        flash('Please log in to view content')
        return redirect(url_for('login'))
    elif session.get('username') == username:
        # Use of extended reference in User model allows for simpler queries to retrieve games and other user data
        current_user = User.from_mongo(
                **mongo.db.users.find_one(
                    {"_id": ObjectId(session.get("_id"))  }
                    )
                )
        return render_template('user_games.html', 
                user=current_user)
    else:
        user = User.from_mongo(
                **mongo.db.users.find_one({"name": username})
                )
        return render_template('user_games.html', user=user)


@app.route('/user/<username>/reviews', methods=['GET'])
def user_reviews(username):

    if session.get('username') == username:
        user = User.from_mongo(
                **mongo.db.users.find_one(
                    {"_id": ObjectId(session.get('_id'))})
                )
    else:
        user = User.from_mongo(
                **mongo.db.users.find_one({'name': username})
                )

    return render_template('user_reviews.html', user=user)


@app.route('/review/<review_id>', methods=['GET'])
def review(review_id):
    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id) })
    return render_template('review.html.jinja', title="Review", review=review)


@app.route('/review/<review_id>/edit_review', methods=['GET', 'POST'])
def edit_review(review_id):
    """
    Allows users to edit reviews. Ensures the extended ref contained in the game object stays current by checking if the reference and the review share the same time. If they do, remove that review_ref and push the other review_ref on to the list.
    """
    form = EditReviewForm()
    print(review_id)
    review = Review.from_mongo(**mongo.db.reviews.find_one({ "_id": ObjectId(review_id) }))
    game = Game.from_mongo(**mongo.db.games.find_one({ "_id":review.game_id }))
    user_name = session.get('username')
    if user_name == review.author_ref['author_name']:
        user = User.from_mongo(**mongo.db.users.find_one({ "name": user_name }))

        if form.validate_on_submit():
            review.name = form.title.data
            review.text = form.review_text.data
            review_ref = review.create_review_ref()
            review.update_review()
            for game_review in game.reviews:
                if game_review.get('review_pub_date') == review.pub_date:
                    game.reviews.remove(game_review)
            game.reviews.append(review_ref)

            game.update_game()
            for user_review in user.reviews:
                if user_review.get('review_pub_date') == review.pub_date:
                    user.reviews.remove(user_review)
            user.reviews.append(review_ref)
            user.update_user()
            return redirect(url_for('review', review_id=review_id))
        elif request.method == "GET":
            form.title.data = review.name
            form.review_text.data = review.text
    return render_template('edit_review.html.jinja', 
                                title='Edit Review', 
                                review_id=review_id,
                                form=form)

@app.route('/add_game_ref/<game_id>', methods=['POST'])
def add_game_ref(game_id):
    form = AddGameRef()
    if form.validate_on_submit():
        user = User.from_mongo(**mongo.db.users.find_one({"name": session.get('username')}))
        game = Game.from_mongo(**mongo.db.games.find_one('_id': game_id))
        game_ref = Game.create_game_ref()
        for game in user.game_list:
            if game.get('game_id') == game_ref.get('game_id'):
                user.game_list.remove(game)
        user.game_list.append(game_ref)
    return redirect(url_for('profile', username=user.name))
        

@app.route('/delete_game/<game_id>', methods=['POST'])
def del_game_ref(game_id):
    form = DeleteGame()
    if form.validate_on_submit():
        user = User.from_mongo(**mongo.db.users.find_one({"name": session.get('username')}))
        for game in user.game_list:
            if game.get(game_id) == game_id:
                user.game_list.remove(game)
                flash('Game Successfully Removed')
    return redirect(url_for('profile', username=user.name))


@app.route('/delete_review/<review_id>')
def del_review(review_id):
    form = DeleteReview()
    if form.validate_on_submit():
        user = User.from_mongo(**mongo.db.users.find_one({ "name": session.get('username') }))
        review = Review.from_mongo(**mongo.db.reviews.find_one('_id': ObjectId(review_id)))

        if user._id == review.author_id:
            for del_review in user.reviews:
                if del_review.get('_id') == review_id:
                    user.reviews.remove(del_review)
            user.update_user()
            review.delete_review()
            flash('Review Deleted')
    return redirect(url_for('profile', username = user.name))



