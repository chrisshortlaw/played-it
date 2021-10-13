#!python3.9
from typing import Type, Set, Optional, List
import os

from terminusdb_client import WOQLSchema, WOQLClient
from models import User, Review, Publisher, GameList, ReviewList, schema 

from database import played_it_db
if os.path.exists('../env.py'):
    import env


played_it_db.db_connect()
schema.from_db(played_it_db.client)


game_raw = list(played_it_db.client.query_document({"@type": "Game", "label":"Fake Game"}))
user_raw = list(played_it_db.client.query_document({"@type": "User", "name": "new_user1"}))
user_id = user_raw[0].get("@id")
game_id = game_raw[0].get("@id")
game_doc = schema.import_objects(game_raw)
user_doc = schema.import_objects(user_raw)
user_name = user_raw[0].get("name")
game_label = game_raw[0].get("label")
 

def load_user_test():
    pass

def load_game_test():
    publisher_doc = schema.import_objects([played_it_db.client.get_document('Publisher/nintendo')])
    fake_game = Game.create_game(label="Fake Game", platform = "Nintendo GameBoy", year = 1994, genre="action", publisher=set(publisher_doc))
    try:
        played_it_db.client.update_document(fake_game)
    except Exception as e:
        print(f"Fake_game threw exception: {e}")
        
    else:
        print(f"Fake game successfully loaded.")


def load_review_test():

    fake_review = Review(title="I like this", game_label=game_label, game=game_doc[0], _game_id=game_id, author=user_doc[0], author_name=user_name, _author=user_id, text="This fake game is great", pub_date="15-12-2021 04:00:33.764" )

    try:
        played_it_db.client.update_document(fake_review)
    except Exception as e:
        print(f"Fake_review threw exception: {e}")
        
    else:
        print(f"Fake review successfully loaded.")


def load_game_list_test():
    # fake_game_list = GameList(user=user_id, games=list(game_doc))
    # NOTE: the above and various other concatenations do not work. Python client has bugs when linking to type
    
    fake_game_list = GameList(user=user_id, games=set([game_id]))

    try:
        played_it_db.client.update_document(fake_game_list)
    except Exception as e:
        print(f"Fake_game_list threw exception: {e}")
    else:
        print("Fake game list successfully uploaded")


def load_review_list_test():
    reviews = {review["@id"] for review in played_it_db.client.query_document({"@type": "Review", "_game_id": game_id})}
                                                                        
    fake_review_list = ReviewList(game=game_id, reviews=reviews)

    try:
        played_it_db.client.update_document(fake_review_list)
    except Exception:
        print(f"Fake_review_list threw exception: {e}")
    else:
        print("Fake review list successfully uploaded")


def add_game_list_to_user():
    game_list = list(played_it_db.client.query_document({"@type": "GameList", "user": user_id}))
    game_list_doc = schema.import_objects(game_list)
    print(game_list)
    game_list_user = played_it_db.client.get_document(user_id)
    print(game_list_user)
    game_list_user["game_list"] = game_list

    try:
        played_it_db.client.update_document(game_list_user)
    except Exception as e:
        print(f"Game_list_User did not update. Exception: {e}")
    else:
        print("Game list USer successfully updated with game_list")


def delete_all_test_docs(doc_type):
    del_list = list(played_it_db.client.get_documents_by_type(doc_type))
    del_ids = [doc["@id"] for doc in del_list]
    print(del_list)

    played_it_db.client.delete_document(del_list[0])

    check_del = list(played_it_db.client.get_documents_by_type(doc_type))
    if len(check_del) > 0:
        print(f"{check_del}")
        print(f"Delete_all_test_docs: Error: Delete did not occur")
    else:
        print("Delete all test docs successful")


def main():
#   Update Schema
#    played_it_db.db_connect()
    schema.commit(played_it_db.client, commit_msg="Updated Review Model")

# Update docs programmatically. Test Schema

    delete_all_test_docs("ReviewList") 
 

if __name__ == "__main__":
    main()
    
