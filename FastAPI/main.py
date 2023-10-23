from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from typing import Union

from geopy.geocoders import Nominatim
from geonamescache import GeonamesCache

app = FastAPI()


def get_city_info(city_name):
    geolocator = Nominatim(user_agent="city_info_app")

    try:
        location = geolocator.geocode(city_name)
        if location:
            city_info = {
                "city": city_name.capitalize(),
                "latitude": location.latitude,
                "longitude": location.longitude
            }
            return city_info
        
    except Exception as e:
        return {"error": str(e)}
    

@app.get('/')
def index(): 
    return {'data': 'Hi'}

@app.post('/geo/')
def lang_lat_return(city_name: str):
    city_info = get_city_info(city_name)
    if "error" in city_info:
        return {"error": "City not found"}
    else:
        return city_info

if __name__ == "__main__":
    uvicorn.run("main:app")
