from flask import Flask
from configparser import ConfigParser

config = ConfigParser()
config.read('config')

app = Flask(__name__)

@app.route("/")
def index():
    api_key = config['OpenWeatherMap']['api_key']
    return "TERÇA!!!"

if __name__ == "__main__":
    app.run()
