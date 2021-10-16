import os
from app import app


if __name__ == "__main__":
    app.run(host=os.environ.get('IP'), port=(os.environ.get("PORT")) or process.env.PORT)

