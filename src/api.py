import datetime
import json
import random

from flask import Flask, request
from flask_pymongo import PyMongo

from jsonencoder import JSONEncoder
from settings import DB_ADDRESS


app = Flask(__name__)
app.config["MONGO_URI"] = DB_ADDRESS
mongo = PyMongo(app)
countries = mongo.db.country


@app.route('/<name>', methods=['GET', 'POST'])
def index(name):
    if request.method == 'GET':
        country = countries.find_one({"country": name})
        return json.dumps(country, cls=JSONEncoder)
    elif request.method == 'POST':
        country = {
            "country": name,
            "density": random.randint(0, 26337),
            "createdAt": datetime.datetime.utcnow()
        }
        country_id = countries.insert(country)
        return f"Inserted {country_id}"


@app.route('/', methods=['GET'])
def get_country_by_quartile_density():
    sorted_countries = list(countries.find().sort("density"))
    n = len(sorted_countries)
    first_quartile = int(n/4) if (n/4).is_integer() else int(n/4) + 1
    second_quartile = int(n/2) if (n/2).is_integer() else int(n/2) + 1
    third_quartile = int(3*n/4)

    return json.dumps({
        f"1st (0-{first_quartile} P/Km²)": sorted_countries[:first_quartile],
        f"2nd  ({first_quartile}-{second_quartile} P/Km²)": sorted_countries[
            first_quartile:second_quartile],
        f"3rd  ({second_quartile}-{third_quartile} P/Km²)": sorted_countries[
            second_quartile:third_quartile],
        f"4th  ({third_quartile}-{sorted_countries[-1]['density']} P/Km²)":
        sorted_countries[third_quartile:]}, cls=JSONEncoder)
