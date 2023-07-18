from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import randint, choice

# API key needed to delete records
KEY = "TopSecretAPIKey"

app = Flask(__name__)

# Connect to Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def random():
    all_records = db.session.query(Cafe).all()
    cafe = choice(all_records)

    response = jsonify(
        id=cafe.id,
        name=cafe.name,
        map_url=cafe.map_url,
        img_url=cafe.img_url,
        location=cafe.location,
        seats=cafe.seats,
        has_toilet=cafe.has_toilet,
        has_wifi=cafe.has_wifi,
        has_sockets=cafe.has_sockets,
        can_take_calls=cafe.can_take_calls,
        coffee_price=cafe.coffee_price,
    )

    return response


@app.route("/all")
def all_cafes():
    all_records = db.session.query(Cafe).all()
    lst = []

    for i in all_records:
        dct = i.__dict__
        del dct["_sa_instance_state"]
        lst.append(dct)

    response = jsonify(cafes=lst), 200

    return response


# HTTP GET - Read Record
@app.route("/search")
def search():
    loc = request.args.get("loc")
    cafe = db.session.query(Cafe).filter(Cafe.location == loc).first()

    if cafe:
        cafe = cafe.__dict__
        del cafe["_sa_instance_state"]

        response = (jsonify(cafe), 200)

        return response

    else:
        return (
            jsonify(
                error={"Not Found": "Sorry, we don't have a cafe at that location."}
            ),
            404,
        )


## HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add():
    body = request.json

    # Exit if authentication fails
    if request.args.get("api-key") != KEY:
        return (
            jsonify(
                error={
                    "Unauthorized": "Sorry, that's not allowed. Please make sure you have the right API key."
                }
            ),
            401,
        )

    try:
        new_cafe = Cafe(
            name=body["name"],
            map_url=body["map_url"],
            img_url=body["img_url"],
            location=body["loc"],
            has_sockets=bool(body["sockets"]),
            has_toilet=bool(body["toilet"]),
            has_wifi=bool(body["wifi"]),
            can_take_calls=bool(body["calls"]),
            seats=body["seats"],
            coffee_price=body["coffee_price"],
        )

        db.session.add(new_cafe)
        db.session.commit()

    except Exception:
        return (
            jsonify(
                Error={"Error": "There was an error with your request to add a cafe"}
            ),
            418,
        )

    else:
        return jsonify(success={"success": "Successfully added the new cafe."}), 200


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PUT", "PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.get(Cafe, int(cafe_id))

    if not cafe:
        return (
            jsonify(
                error={"Not Found": "No cafe with that ID was found in the database."}
            ),
            404,
        )

    cafe.coffee_price = float(new_price)
    db.session.commit()

    return (jsonify(success={"Cafe Added": "Successfully updated the price."}), 200)


## HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete(cafe_id):
    # Send 404 if incorrect authorization
    if request.args.get("api-key") != KEY:
        return (
            jsonify(
                error={
                    "Unauthorized": "Sorry, that's not allowed. Please make sure you have the right API key."
                }
            ),
            401,
        )

    # if there is no cafe with the requested ID, return 404
    elif not db.session.get(Cafe, int(cafe_id)):
        return (
            jsonify(
                error={"Not Found": "No cafe with that ID was found in the database."}
            ),
            404,
        )

    else:
        cafe = db.session.get(Cafe, int(cafe_id))
        db.session.delete(cafe)
        db.session.commit()

        return (
            jsonify(
                success={
                    "Cafe Deleted": "The selected cafe has been removed from the database."
                }
            ),
            200,
        )


if __name__ == "__main__":
    app.run(debug=True)
