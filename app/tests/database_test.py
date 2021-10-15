#!python3.9
from typing import Type, Set, Optional, List, TypeVar, Dict, Any
import os

from dataclasses import dataclass, asdict
from dacite import from_dict

from models import User, Review, Publisher, GameList, ReviewList, Game 

if os.path.exists('../env.py'):
    import env

from app import mongo

UserType = TypeVar("User")


fake_user=User.create_user(password='pass', name='fake_user2', email='fake2@fakemail.com')


def load_user_test(user: UserType) -> Any:
    """
    Checks if user can be uploaded, queried and confirmed to be of same type.
    Assertion holds as of 14-10-21
    TODO: Need to add optional str field ('id') to dataclasses so they can hold attribute.
    """
    new_user = mongo.db.users.insert_one(asdict(user))
    print(new_user.inserted_id)
    _user = mongo.db.users.find_one({"name": user.name})
    print(_user["_id"])
    check_user = from_dict(data_class=User, data=_user)
    assert _user["_id"] == new_user.inserted_id, "load_user_test: Fail. User ids did not match" 

def load_game_test():
    """
    Test Games. Note: As long as IDs differ, MongoDb will prevent population of duplicate data.
    """
    publisher_doc = mongo.db.publisher.find_one({"label": "Nintendo"})
    fake_game = Game.create_game(label="Fake Game", platform = "Nintendo GameBoy", year = 1994, genre="action", publisher=publisher_doc["_id"], reviews=[])
    new_game = mongo.db.games.insert_one(asdict(fake_game))
    _check_game = mongo.db.games.find_one({"name": fake_game.name})
    assert _check_game.get("_id") == new_game.inserted_id, "load game test failed. Ids did not match."

def load_review_test():

    fake_review = Review(title="I like this", game_label=game_label, game=game_doc[0], _game_id=game_id, author=user_doc[0], author_name=user_name, _author=user_id, text="This fake game is great", pub_date="15-12-2021 04:00:33.764" )

    # try:
        # pass
    # except Exception as e:
        # print(f"Fake_review threw exception: {e}")
        
    # else:
        # print(f"Fake review successfully loaded.")
    pass

def load_game_list_test():
    # fake_game_list = GameList(user=user_id, games=list(game_doc))
    # NOTE: the above and various other concatenations do not work. Python client has bugs when linking to type
    
    fake_game_list = GameList(user=user_id, games=set([game_id]))

   #  try:
        # played_it_db.client.update_document(fake_game_list)
    # except Exception as e:
        # print(f"Fake_game_list threw exception: {e}")
    # else:
        # print("Fake game list successfully uploaded")
    pass


def load_review_list_test():
    # reviews = {review["@id"] for review in played_it_db.client.query_document({"@type": "Review", "_game_id": game_id})}
                                                                        
    fake_review_list = ReviewList(game=game_id, reviews=reviews)

   #  try:
        # played_it_db.client.update_document(fake_review_list)
    # except Exception:
        # print(f"Fake_review_list threw exception: {e}")
    # else:
        # print("Fake review list successfully uploaded")
    pass


def add_game_list_to_user():
    # game_list = list(played_it_db.client.query_document({"@type": "GameList", "user": user_id}))
    # game_list_user["game_list"] = game_list

    # try:
        # played_it_db.client.update_document(game_list_user)
    # except Exception as e:
        # print(f"Game_list_User did not update. Exception: {e}")
    # else:
        # print("Game list USer successfully updated with game_list")
    pass

def delete_all_test_docs(doc_type):
    pass    

def main():

    load_game_test()

# Update docs programmatically. Test Schema

 

if __name__ == "__main__":
    main()
    
