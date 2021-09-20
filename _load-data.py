#!python3

import csv
from typing import Set
from models import Game, Publisher
from config import Config
from terminusdb_client import WOQLClient, WOQLQuery

games_list = []
publisher_set = set()


def game_etl():
    """
    Takes a csv (retrieved from kaggle) and converts it to dict
    uses replace string method to exchange ' ' <spaces> for '_'
    Makes it easier to use names as LexicalKeys
    """
    with open ('_raw-data/archive/vgsales.csv', 
            newline='') as csvfile:
        reader = csv.DictReader(csvfile) 
        for row in reader:
            games_list.append(row)
            game_publisher = row['Publisher']
            publisher_set.add(game_publisher)

    print(f'Game : {games_list[0]}')
    print(f'publisher_set')


def db_connect():
    """
    function to connect to database
    """
    user = "chris"
    team = "team_of_me"
    endpoint = f"https://cloud.terminusdb.com/{team}"
    db = "played_it_db"
    client = WOQLClient(endpoint)

    client.connect(user=user, team=team, db=db, use_token=True)
    return client


def load_publishers():
    """
    Loads list of publisher docs
    Create a publisher key which shall be used as a lexicalkey
    Makes it easier to obtain publisher key.
    """
    client = db_connect()
    
    publisher_list = []

    for publisher in publisher_set:
        publisher_lexical_key = get_publisher_lexical_key(publisher)
        publisher_list.append(Publisher(name=publisher, key_name=publisher_lexical_key))

    client.insert_document(publisher_list, commit_msg='Populated publishers')


def get_publisher_lexical_key(publisher_name):
    """
    Method to retrieve lexical_key from publisher name
    """

    publisher_lexical_key = str(publisher_name).replace(" ", "_")

    return publisher_lexical_key

def delete_document_by_type(doc_type_string):
    """
    Deletes documents of a certain type in database.
    To be used for cleaning.
    TODO: Review how replace_document works - params not clear at present
    """
    client = db_connect()

    docs_by_type = client.get_documents_by_type(doc_type_string)

    existing_docs = [doc for doc in docs_by_type]

    client.delete_document(existing_docs)
    
    if len(client.get_documents_by_type(str(doc_type_string))) == 0:
        print(f"No Documents of type: '{doc_type_string}' present")
    else:
        print(f"Documents of type: '{doc_type_string}' present. Deletion failed.")


def load_games():
    """
    Calls game_etl and retrieves a list of dicts populated from csv,
    Creates documents from that list of dicts and loads them to db
    """

    client = db_connect()
    game_etl()
    game_doc_list = []
    for game in games_list: 
        # Complete this
        game_publisher = client.get_document(str(game['Publisher']).replace(' ', '_'))
        
        new_game = Game(
                rank=int(game['Rank']), 
                name=game['Name'], 
                year=int(game['Year']), 
                platform=game['Platform'], 
                genre=game['Genre'],
                publisher = game_publisher,
                na_sales = float(game['NA_Sales']),
                eu_sales = float(game['EU_Sales']),
                jp_sales = float(game['JP_Sales']),
                other_sales = float(game['Other_Sales']),
                global_sales = float(game['Global_Sales'])
                )
        game_doc_list.append(new_game)


# import classes and load to db

if __name__ == "__main__":
