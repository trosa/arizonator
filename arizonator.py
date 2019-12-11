from flask import Flask, render_template
from configparser import ConfigParser
import requests
from datetime import datetime
import pprint

pp = pprint.PrettyPrinter(indent=4)

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

@app.route("/")
def index():
    config = ConfigParser()
    config.read('./config')
    api_url = config['WeatherBit']['api_url']
    querystring = get_querystring(config)

    response = requests.request("GET", api_url, params=querystring)

    todaysweekday = datetime.today().weekday()

    if todaysweekday > 4:
        weatherdata = response.json()["data"][:6]
    else:
        daystopick = 6 - todaysweekday
        weatherdata = response.json()["data"][:daystopick]

    rains = {}
    icons = {}

    for date in weatherdata:
        pp.pprint(date)
        print("\n")
        year, month, day = tuple([int(d) for d in date["valid_date"].split("-")])
        weekday = datetime(year, month, day).strftime("%A")
        if weekday in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            rains[weekday] = date["precip"]
            icons[weekday] = "https://weatherbit.io/static/img/icons/" + date["weather"]["icon"] + ".png"
            # print(weekday, rains[weekday])

    arizonaday = config['Defaults']['arizona_day']
    if datetime.today().weekday() > 1:
        arizonaday = datetime.today().strftime("%A")

    mostrainyday = max(rains, key=rains.get)

    if rains[mostrainyday] != 0:
        arizonaday = mostrainyday

    return render_template('index.html', arizonaday=mostrainyday, rains=rains, icons=icons), 200

if __name__ == "__main__":
    app.run()
