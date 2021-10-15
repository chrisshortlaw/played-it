#!Python3.9
from typing import Type, Set, Optional, List, TypeVar
from dataclasses import dataclass, field, asdict
import os
import urllib.parse

from werkzeug.security import check_password_hash, generate_password_hash 

if os.path.exists('env.py'):
    import env


def make_lexical_key(prefix: str, str_list: List[str]) -> str:
    """
    creates a lexical key in snake case & lower from prefix & string list.
    Params:
        Prefix: str (example: 'User/')
        str_list: [str...] (example: [username, email] -> ['new_user1', 'fake@fakemail.com'])
    Returns:
        String (Example: 'User/new_user1_fake%40fakemail.com'
    """
    id_string = "".join([urllib.parse.quote_plus(key) for key in str_list])
    lexical_key = prefix + id_string
    print(lexical_key)
    return lexical_key

@dataclass
class BaseModel:
    """
    A basic model with a name field and will hold our to_mongo_dict method and our from_mongo method.
    """
    name: str

    def to_mongo_dict(self):
        mongo_obj = asdict(self)
        mongo_obj.pop('_id')
        return mongo_obj


@dataclass
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
    email : str
    _password: str
    reviews: List[str] 
    game_list: List[str] 
    _id: Optional[str] = None

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
    def create_user(cls, password, name, email, reviews=[], game_list=[]):
        hashed_pass = User.create_pass(password)
        return cls(name=name, email=email, _password=hashed_pass, reviews=reviews, game_list=game_list) 

    @classmethod
    def add_user(cls, password, name, email, db_loc):
        new_user = User.create_user(password, name, email)
        uploaded_user = db_loc(to_mongo_dict(new_user))
        return uploaded_user.inserted_id



@dataclass
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
    label: str
    platform: str
    year: int
    genre: str
    publisher: str 
    reviews: List[str] 

    @classmethod
    def create_name(cls, label):
        name = label.lower().replace(" ", "_")
        return name

    @classmethod
    def create_game(cls, label, platform, year, genre, publisher, reviews=[]):
        name = cls.create_name(label)
        return cls(name=name, label=label, platform=platform, year=year, genre=genre, publisher=publisher, reviews=reviews) 


@dataclass
class Publisher(BaseModel):
    """
    Class for Publisher Document
    Key is LexicalKey which is taken from 'name' field
    Fields: name: str, label: str
    name: should have the pattern: 'devolver_digital, sony_computer_entertainment' -> lowercase, snake_case
    label: Regular spelling.
    """
    name: str

    @classmethod
    def create_publisher(cls, label):
        name = str(label).replace(" ", "_").lower()
        return cls(label=label, name=name)


@dataclass
class Review:
    """
    title: str
    game: id for game          
    game_label: str                 
    author: id for author (User)       
    author_name: str            # str -> name for user 
    text: str                   # Text of Review
    pub_date: str               # Publication Date of Review in str

    """
    game: str                   # GameDoc -> Ref for Game
    game_label: str             # label for game
    author: str                 # AuthorDoc -> Ref for User
    author_name: str            # str -> name for user 
    text: str                   # Text of Review
    pub_date: str               # Publication Date of Review in str


@dataclass
class Genre:
    """
    Generic class which will contain genres
    """
    genre_label: str


@dataclass
class GameList:
    """
    user -> str @id "User"
    games: List["Game"]
    """
    user: str 
    games: Set[str]


@dataclass
class ReviewList:
    """
    game -> str @id "Game"
    reviews -> List["Review"]
    """
    game: str
    reviews: Set[str]


def main():
    pass

if __name__ == "__main__":
    main()
    