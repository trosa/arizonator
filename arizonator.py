from flask import Flask, render_template
from configparser import ConfigParser
import requests
from datetime import datetime, timezone
import pytz

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
    icons_url = config['WeatherBit']['icons_url']
    querystring = get_querystring(config)
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    response = requests.request("GET", api_url, params=querystring)
    weatherdata = response.json()["data"]

    todaysweekday = datetime.today().isoweekday()-1
    startdayoffset = 0

    naivetimenow = datetime.now()
    desiredtimezone = pytz.timezone(config['Defaults']['timezone'])
    awaretimenow = desiredtimezone.localize(naivetimenow)
    if awaretimenow.hour > 12 and todaysweekday < 4:
        todaysweekday += 1
        startdayoffset = 1

    if todaysweekday > 4:
        thisweeksdata = weatherdata[:6]
    else:
        daystopick = 6 - todaysweekday
        thisweeksdata = weatherdata[startdayoffset:daystopick]

    nextweeksdata = weatherdata[(7-todaysweekday):(11-todaysweekday)]

    rains = {}
    icons = {}
    nextweeksrains = {}

    for date in thisweeksdata:
        year, month, day = tuple([int(d) for d in date["valid_date"].split("-")])
        weekday = datetime(year, month, day).strftime("%A")
        if weekday in weekdays:
            rains[weekday] = date["pop"]
            icons[weekday] = icons_url + date["weather"]["icon"] + ".png"

    for date in nextweeksdata:
        year, month, day = tuple([int(d) for d in date["valid_date"].split("-")])
        weekday = datetime(year, month, day).strftime("%A")
        if weekday in weekdays:
            nextweeksrains[weekday] = date["pop"]

    arizonaday = config['Defaults']['arizona_day']
    if datetime.today().weekday() > 1:
        arizonaday = datetime.today().strftime("%A")

    mostrainyday = max(rains, key=rains.get)
    if rains[mostrainyday] != 0:
        arizonaday = mostrainyday
    if weekdays.index(arizonaday) <= todaysweekday:
        if todaysweekday < 5:
            arizonaday = weekdays[todaysweekday]

    nextarizonaday = config['Defaults']['arizona_day']
    nextweeksmostrainyday = max(nextweeksrains, key=nextweeksrains.get)
    if nextweeksrains[nextweeksmostrainyday] != 0:
        nextarizonaday = nextweeksmostrainyday

    return render_template('index.html', arizonaday=arizonaday, rains=rains, icons=icons, nextarizonaday=nextarizonaday, nextweeksrains=nextweeksrains), 200

if __name__ == "__main__":
    app.run()
