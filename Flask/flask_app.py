from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim
from utils import db_connector

app = Flask(__name__)


def get_city_info(city_name):
    geolocator = Nominatim(user_agent="city_info_app")



    try:
        location = geolocator.geocode(city_name)
        if location:
            city_info = {
                "city": city_name.capitalize(),
                "latitude": location.latitude,
                "longitude": location.longitude,
            }
            return city_info
    except Exception as e:
        return {"error": str(e)}


@app.route('/')
def index():
    return jsonify({'data': 'Hi'})


@app.route('/geo/', methods=['POST'])
def lang_lat_return():
    city_name = request.form['city_name']
    city_info = get_city_info(city_name)
    if "error" in city_info:
        return jsonify({"error": "City not found"})
    else:

        db_info = db_connector(fetch=True, name='Joe Elm', email='JE@gmail.com', lounge=city_name)
        city_info['db_info'] = db_info

        return jsonify(city_info)


if __name__ == "__main__":
    app.run()
