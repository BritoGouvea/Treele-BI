import requests

def get_latitude_longitude(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": 'AIzaSyDIHbEolhwO7uzJvyyWbFtgwQL9PD78r9M'
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        latitude = location["lat"]
        longitude = location["lng"]
        return Coordenadas(latitude, longitude)
    else:
        return None
    
class Coordenadas:

    def __init__(self, coordenadas: dict) -> None:        
        self.latitude = coordenadas['latitude']
        self.longitude = coordenadas['longitude']