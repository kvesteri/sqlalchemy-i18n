import json
from flask import Flask
from model.sqlalchemy import db, babel
from flask import request
from model.item import Item

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres@localhost/strive_development"

db.init_app(app)
babel.init_app(app)


@babel.localeselector
def get_locale():
    return request.headers.get("Accept-Language") or "en"


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/item", methods=["GET", "POST"])
def article():

    if request.method == "GET":
        items = Item.query.limit(10).all()
        return {
            "items": [
                {
                    "id": a.id,
                    # TODO: cleanup of this syntax reliant on `t` attribute
                    "name": a.current_translation.name or a.fallback_translation.name,
                }
                for a in items
            ]
        }

    body = request.json

    new_item = Item(**body)
    db.session.add(new_item)
    db.session.commit()
    return {"message": "Good job!"}
