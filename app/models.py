#!Python3.9
from typing import Type, Set, Dict, Optional, List, TypeVar
from dataclasses import dataclass, field, asdict
import os
import urllib.parse
from bson import ObjectId

from werkzeug.security import check_password_hash, generate_password_hash 

if os.path.exists('env.py'):
    import env

from app.database_mongo import mongo


class BaseModel:
    """
    A basic model with a name field and will hold our to_mongo_dict method and our from_mongo method.
    This will permit us to manipulate class instances via the database model rather than dictionaries. Manipulating instances allows us to set and enforce certain data-types, use type hinting and control how data is changed.  
    """
    def __init__(self, name):

        self.name  = name 

    def to_mongo_dict(self):
        """
        TODO: Reword this docstring
        Instance Method converting dataclass to dict allowing for a smoother exchange between MongoDB and the app.
        _id is not specified on the BaseClass due to limitations inherent in dataclass (cannot have positional fields after optional fields when inheriting). However, the method pops any _id class 
        NOTE: This destroys the cls in question and removes the _id attribute.
        """
        mongo_obj = self.__dict__
        mongo_obj.pop('_id')
        return mongo_obj


    @classmethod
    def from_mongo(cls, **mongodict):
        """
        Creates a class from a return value from a mongo query. Add the _id to the class instance which will permit useful querying. 
        Params:
            dictionary from mongodb query
        Returns:
            Class instance.
        """
        new_model = cls(**mongodict)
        return new_model


class User(BaseModel):
    """
    Class of user.
    TODO: Add ability to like reviews, follow other Users and be followed.
    Schema: 
        name: Username chosen by User -> str
        email: User's email -> str
        _password: set with self.password
        game_list: Optional["GameList"] 
        reviews: Optional["ReviewList"] 
    """
    
    def __init__(self, name, email, _password, game_list = [], avatar_url = "", reviews = [], _id=None, bio=""):
        self.name = name
        self.email = email
        self._password = _password
        self.game_list: List[Dict[str. str]] = game_list 
        self.avatar_url = avatar_url
        self.reviews: List[Dict[str, str]] = reviews
        self._id = _id
        self.bio = bio

    @property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, password_string):
        """
        To be used by User to change password
        runs password_string through the generate_password_hash function
        sets the User password as the newly hashed & salted string
        """
        hashed_pass = generate_password_hash(password_string, method='pbkdf2:sha256', salt_length=16)
        self._password = hashed_pass

    def check_pass(self, password_string):
        """
        To be used for login verification
        Checks hashed pass against password_string and returns True if match, false otherwise
        """
        return check_password_hash(self.password, password_string)

    @classmethod
    def create_pass(cls, password_string):
        """
        Uses werkzeug built in password hash to generate a hashed pass and return it
        """
        hashed_pass = generate_password_hash(password_string, method='pbkdf2:sha256', salt_length=16)
        return hashed_pass
        
    @classmethod
    def create_user(cls, password, name, email, game_list=[], reviews=[], bio=""):
        hashed_pass = User.create_pass(password)
        avatar_name = urllib.parse.quote_plus(name)
        avatar_url = f'https://robohash.org/{avatar_name}.png'
        return cls(name=name, email=email, _password=hashed_pass, game_list=game_list, avatar_url=avatar_url, reviews=reviews, bio=bio) 

    @classmethod
    def add_user(cls, password, name, email, db_loc=mongo.db.users, **kwargs):
        new_user = User.create_user(password, name, email, **kwargs)
        uploaded_user = db_loc.insert_one(new_user.to_mongo_dict())
        new_user._id = uploaded_user.inserted_id
        return new_user

    def upload_user(self, db_loc=mongo.db.users):
        uploaded_user = db_loc.insert_one(self.to_mongo_dict())
        self._id = uploaded_user.inserted_id
        return self

    def update_user_with_dict(self, db_loc=mongo.db.users, **fields):
        """
        Updates User.         
        Params:
            db_loc: database to update to
            **field: kwargs which is a nested dict
            TODO: COnsider adding a check to see if updated_user returns an error
        """
        for key, value in fields.items():
            setattr(self, key, value)
        updated_user = db_loc.find_one_and_update({"_id": self._id}, {"$set": self.__dict__}) 
        return updated_user


    def update_user(self, db_loc=mongo.db.users):
        updated_user = db_loc.find_one_and_update({"_id": self._id}, { "$set": self.__dict__ })
        return updated_user

    def delete_user(self, db_loc=mongo.db.users):
        deleted_user = db_loc.delete_one({"_id": ObjectId(self._id)})
        return deleted_user

        
    def create_author_ref(self):
        author_dict = {}
        author_dict['author_id'] = self._id
        author_dict['author_name'] = self.name
        author_dict['author_avatar'] = self.avatar_url
        return author_dict


class Game(BaseModel):
    """
    Document for Computer and video games
    fields with types:
    NOTE: name is in snake_case
    name -> str
    NOTE: label is natural case
    label -> str
    platform -> str
    year -> int
    genre -> str
    publisher -> str
    reviews -> List[str]
    """
    def __init__(self, name, label, platform, year, genre, publisher, publisher_id, reviews = [], cover_art="", _id=None):
        self.name = name
        self.label = label
        self.platform = platform
        self.year = year
        self.genre = genre
        self.publisher = publisher
        self.publisher_id = publisher_id
        self.reviews: List[Dict[str, str]] = reviews
        self.cover_art = cover_art
        self._id = _id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @classmethod
    def create_name(cls, label):
        name = label.lower().replace(" ", "_")
        return name

    @classmethod
    def create_game(cls, label, platform, year, genre, publisher, publisher_id, reviews=[]):
        name = cls.create_name(label)
        return cls(name=name, label=label, platform=platform, year=year, genre=genre, publisher=publisher, publisher_id=publisher_id, reviews=reviews)

    @classmethod
    def add_game(cls, label, platform, year, genre, publisher, db_loc=mongo.db.games):
        """
        Creates a game with the passed arguments. 
        Uploads it to the db, label -> str, 
        platform -> str, year -> int, 
        genre-> str, publisher -> publisher object, 
        db_loc: location of db collection

        """
        if isinstance(publisher, Publisher):
            new_game = Game.create_game(label=label, 
                        platform=platform, 
                        year=year, 
                        genre=genre, 
                        publisher=publisher.label, 
                        publisher_id=publisher._id)
        elif type(publisher) is dict:
            publisher = mongo.db.publisher.find_one(
                            { "_id": ObjectId(str(publisher.get("_id" )) )})
            if publisher and publisher.get("_id") is not None:
                new_game = Game.create_game(label=label, 
                                    platform=platform, 
                                    year=year, 
                                    genre=genre, 
                                    publisher=publisher.get("label"), 
                                    publisher_id=publisher.get("_id"))
            else:
                raise ValueError('Publisher does not exist on db')
        elif type(publisher) is str:
            publisher = mongo.db.publisher.find_one(
                            { "_id": ObjectId(publisher)})
            new_game = Game.create_game(label=label, 
                                platform=platform, 
                                year=year, 
                                genre=genre, 
                                publisher=publisher.get("label"), 
                                publisher_id=publisher.get("_id"))
        else:
            raise TypeError('Param. Publisher must be str, Publisher, or dict')

        uploaded_game = db_loc.insert_one(new_game.to_mongo_dict())
        new_game._id = uploaded_game.inserted_id
        return new_game

    def update_game_with_dict(self, db_loc=mongo.db.games, **fields):
        for key, value in fields.items():
            setattr(self, key, value)
        if self._id:
            updated_game = db_loc.find_one_and_update({"_id": self._id}, {"$set": self.__dict__}) 
        else:
            raise ValueError('_id is not present for some reason')
        
    def update_game(self, db_loc=mongo.db.games):
        updated_game = db_loc.find_one_and_update({"_id": self._id}, {"$set": self.__dict__})


    def delete_game(self, db_loc=mongo.db.games):
        deleted_game = db_loc.delete_one({"_id": ObjectId(self.id)})


    def create_game_ref(self):
        game_dict = {}
        game_dict['game_name'] = self.name
        game_dict['game_id'] = self._id
        game_dict['game_label'] = self.label
        game_dict['game_platform'] = self.platform
        return game_dict


class Publisher(BaseModel):
    """
    Class for Publisher Document
    Fields: name: str, label: str
    name: should have the pattern: 'devolver_digital, sony_computer_entertainment' -> lowercase, snake_case
    label: Regular spelling.
    """
    def __init__(self, name, label, _id=None):
        self.name = name

        self.label = label
        self._id = _id

    @classmethod
    def create_publisher(cls, label):
        name = str(label).replace(" ", "_").lower()
        return cls(label=label, name=name)

    def upload_publisher(self, db_loc=mongo.db.publisher):
        uploaded_pub = db_loc.insert_one(self.to_mongo_dict())
        self._id = uploaded_pub.inserted_id
        return self



class Review(BaseModel):
    """
    game: str               # Label for game
    game_id: str            # Id for game                 
    author: str             # name for author (User)       
    author_id: str          # id for user 
    text: str                   # Text of Review
    pub_date: str               # Publication Date of Review in str
    _id: Optional[str] = None
    
    Model for reviews which will be made and uploaded by users. 
    """
    def __init__(self, name: str, game: str, game_id:str, author: str, author_id: str,  text: str, pub_date:str, _id=None, game_ref: Optional[Dict[str, str]]=None, author_ref: Optional[Dict[str, str]] = None):
        self.name = name
        self.game = game                 # GameDoc -> Ref for Game
        self.game_id = game_id
        self.game_ref: Dict[str, str] = game_ref
        self.author = author             # Author Name
        self.author_id = author_id       # str -> name for user 
        self.author_ref: Dict[str, str] = author_ref
        self.text = text                 # Text of Review
        self.pub_date = pub_date         # Publication Date of Review in str
        self._id = _id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @classmethod
    def add_review(cls, name, game, game_id, author, author_id, text, pub_date, game_ref=None, author_ref=None, db_loc=mongo.db.reviews):
        new_review = Review(name=name, game=game, game_id=game_id, author=author, author_id=author_id, text=text, pub_date=pub_date, author_ref=author_ref, game_ref=game_ref)
        added_review = db_loc.insert_one(new_review.to_mongo_dict())
        new_review._id = added_review.inserted_id
        return new_review

    def update_review(self, db_loc=mongo.db.reviews):
        updated_review = db_loc.find_one_and_update({"_id": self._id}, {"$set": self.__dict__}) 
        return updated_review
    
    def update_review_with_dict(self, db_loc=mongo.db.tests, **fields):
        for key, value in fields.items():
            setattr(self, key, value)
        updated_review = db_loc.find_one_and_update({"_id": self.id}, {"$set": self.__dict__})
        return updated_review


    def delete_review(self, db_loc=mongo.db.reviews):
        deleted_review = db_loc.delete_one({"_id":ObjectId(self.id)})
        return deleted_review


    def create_review_ref(self):
        review_dict = {}
        review_dict['review_id'] = self._id
        review_dict['review_title'] = self.name
        review_dict['review_author'] = self.author        
        review_dict['review_author_id'] = self.author_id
        review_dict['review_text'] = self.text
        review_dict['review_pub_date'] = self.pub_date
        return review_dict


@dataclass
class Genre:
    """
    Generic class which will contain genres
    """
    genre_label: str


class GameList:
    """
    user -> str @id "User"
    games: set["Game"]
    This class functions as a bucket for managing the user to games relatioship i.e. a one-to-many table if we were using a relational db.
    """
    def __init__(self, name, user, page, count, games = set(), _id=None):
        self.name = name
        self.user = user
        self.page = page
        self.count = count
        self.games = games
        self._id = _id


class ReviewList:
    """
    game -> str @id "Game"
    reviews -> set["Review"]
    A bucket for reviews. A one-to-many relationship between games and reviews.
    """
    def __init__(self, name, game, page, count, reviews = set(), _id=None):
        self.game = game
        self.page = page,
        self.count = count
        self.reviews = reviews
        self._id = _id
    
def main():
    pass

if __name__ == "__main__":
    main()
    
