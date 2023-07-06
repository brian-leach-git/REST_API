from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import randint

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
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
    num_rows = db.session.query(Cafe).count()
    rand_id = randint(1, num_rows)
    cafe = db.session.get(Cafe, rand_id)

    response = jsonify(id=cafe.id,
                       name=cafe.name,
                       map_url=cafe.map_url,
                       img_url=cafe.img_url,
                       location=cafe.location,
                       seats=cafe.seats,
                       has_toilet=cafe.has_toilet,
                       has_wifi=cafe.has_wifi,
                       has_sockets=cafe.has_sockets,
                       can_take_calls=cafe.can_take_calls,
                       coffee_price=cafe.coffee_price)

    return response


@app.route("/all")
def all_cafes():
    all_records = db.session.query(Cafe).all()
    lst = []

    for i in all_records:
        dct = i.__dict__
        del dct['_sa_instance_state']
        lst.append(dct)

    jsn = {'cafes': lst}
    response = jsonify(jsn)

    return response
    

## HTTP GET - Read Record

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
