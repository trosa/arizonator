from flask import Flask, render_template
from flask_frozen import Freezer
from configparser import ConfigParser
import requests
from datetime import datetime

def get_querystring(config):
    api_key = config['WeatherBit']['api_key']
    lat = config['Coordinates']['lat']
    lon = config['Coordinates']['lon']
    querystring = {}
    querystring["key"] = api_key
    querystring["lat"] = lat
    querystring["lon"] = lon
    return querystring

app = Flask(__name__)
app.config.from_pyfile('settings.py')
freezer = Freezer(app)

@app.route("/")
def index():
    config = ConfigParser()
    config.read('config')
    api_url = config['WeatherBit']['api_url']
    querystring = get_querystring(config)

    response = requests.request("GET", api_url, params=querystring)

    weatherdata = response.json()["data"][:6]

    rains = {}

    for date in weatherdata:
        year, month, day = tuple([int(d) for d in date["valid_date"].split("-")])
        weekday = datetime(year, month, day).strftime("%A")
        if weekday in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            rains[weekday] = date["precip"]
            print(rains[weekday])

    arizonaday = max(rains, key=rains.get)

    return render_template('index.html', arizonaday=arizonaday), 200

if __name__ == "__main__":
    app.run()