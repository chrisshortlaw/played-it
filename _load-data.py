#!python3

import csv
from typing import Set
import itertools
import re

from terminusdb_client import WOQLClient, WOQLQuery


from models import Game, Publisher
from config import Config
from database import played_it_db


# Global Vars
games_list = []
publisher_set = set()


def db_client():
    played_it_db.db_connect()
    client = played_it_db.client


    return client


def game_extract():
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


def load_publishers(client):
    """
    Loads list of publisher docs
    Create a publisher key which shall be used as a lexicalkey
    Makes it easier to obtain publisher key.
    """
    
    #list comprehension: takes strings from set and instantiates as Publisher docType
    # returns label and name - a string in snake case
    publisher_list = [Publisher(label=publisher, name=get_lexical_key(publisher)) 
            for publisher in publisher_set ]

    print(f"{publisher_list[1].name}, {publisher_list[1].label}")

    client.insert_document(publisher_list, commit_msg='Populated publishers docType')
    

def check_publishers(client):


    publisher_iter = client.get_documents_by_type("Publisher")
    print(f"check_publishers -> Publisher Length: {len(list(publisher_iter))}")


def get_publisher_id(name):

    return f"Publisher/{get_lexical_key(name)}"


def get_lexical_key(name):
    """
    Method to retrieve lexical_key from publisher name.
    lexical_key should be snake_case form: 'this_is_a_lexical_key'
    """
    _lexical_key = str(name).replace(" ", "_").lower()

    return _lexical_key


def delete_document_by_type(doc_type_string, client):
    """
    Deletes documents of a certain type in database.
    To be used for cleaning.
    TODO: Review how replace_document works - params not clear at present
    """

    docs_by_type = client.get_documents_by_type(doc_type_string)

    existing_docs = [doc['@id'] for doc in docs_by_type]

    client.delete_document(existing_docs)
    
    if len(client.get_documents_by_type(str(doc_type_string))) == 0:
        print(f"No Documents of type: '{doc_type_string}' present")
    else:
        print(f"Documents of type: '{doc_type_string}' present. Deletion failed.")


def load_games(client):
    """
    Calls game_etl and retrieves a list of dicts populated from csv,
    Creates documents from that list of dicts and loads them to db
    """

    #games_list = [{'Rank': '1', 'Name': 'Wii Sports', 'Platform': 'Wii', 'Year': '2006', 'Genre': 'Sports', 'Publisher': 'Nintendo', 'NA_Sales': '41.49', 'EU_Sales': '29.02', 'JP_Sales': '3.77', 'Other_Sales': '8.46', 'Global_Sales': '82.74', '': ''}]
    game_doc_list = []
    for game in games_list: 
            i = 0
            if i == 20:
                break
            else:
                # Complete this
                game_publisher = Publisher.create_publisher(game["Publisher"])
                # game_publisher = client.query_document({"@type": "Publisher", "@id": get_publisher_id(game['Publisher'])})
                game_name_key = get_lexical_key(game['Name'])

                #type checking
                year_check = re.compile('\d{4}|[Nn][\/\\][Aa]')
                if year_check.fullmatch(game['Year']): 
                    new_game = Game(
                            label = game['Name'],
                            name=game_name_key, 
                            year=int(game['Year']), 
                            platform=game['Platform'], 
                            genre=game['Genre'],
                            publisher = set([game_publisher]),
                            reviews = set()
                            )
                    game_doc_list.append(new_game)
                else:
                    print(f"{game['Name']} contained corrupted data and was excluded.")
                    continue

                client.insert_document(game_doc_list, commit_msg='Added games library')
                i += 1
    print(game_doc_list[1].items())
# import classes and load to db


def main():
    client = db_client()
    game_extract()
    load_games(client)


if __name__ == "__main__":
    main()
