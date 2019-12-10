from flask import Flask
from configparser import ConfigParser
import requests

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
    config.read('config')
    api_url = config['WeatherBit']['api_url']
    querystring = get_querystring(config)

    response = requests.request("GET", api_url, params=querystring)
    return response.json()

if __name__ == "__main__":
    app.run()
