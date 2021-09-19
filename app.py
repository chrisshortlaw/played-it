from flask import Flask, flash, render_template, redirect, request, session, url_for
import flask_wtf
from terminusdb_client import WOQLClient, WOQLQuery 
import os
if os.path.exists("env.py"):
    import env
#from models import User


app = Flask(__name__)

user = 'chris'
team = 'team_of_me'
endpoint = f"https://cloud.terminusdb.com/{team}/"
client = WOQLClient(endpoint)


client.connect(user=user, team=team, db="played_it_db", use_token=True)


@app.route("/")
def main():
    documents = client.get_all_documents()
    return render_template("main.html", documents=documents)

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
