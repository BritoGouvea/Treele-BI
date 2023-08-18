from datetime import datetime
import requests
import json

class Obra:

    obras = None

    def __init__(self, obra: dict) -> None:
        self.id = obra['id']
        self.nome = obra['nome']
        self.cnpj = obra['cnpj']
        self.endereço = obra['endereço']
        if obra['coordenadas']:
            self.coordenadas = Coordenadas(obra['coordenadas'])
        else:
            geocoding = Coordenadas.get_latitude_longitude(self.endereço)
            if geocoding:
                self.coordenadas = geocoding
            else:
                self.coordenadas = None
        self.data = datetime.fromisoformat(obra['data'])
        self.solicitações = []

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'nome': self.nome,
            'cnpj': self.cnpj,
            'endereço': self.endereço,
            'coordenadas': {
                'latitude': self.coordenadas.latitude,
                'longitude': self.coordenadas.longitude
            },
            'data': self.data.strftime('%Y-%m-%d')
        }

    @staticmethod
    def traduzir_enterprise(enterprise):
        return {
            'id': enterprise['id'],
            'nome': enterprise['name'],
            'cnpj': enterprise['cnpj'],
            'endereço': enterprise['adress'],
            'data': enterprise['creationDate'],
            'coordenadas': None
        }
    
    @staticmethod
    def criar_obras() -> None:
        obras = json.load(open('./treele_dados/bases/Obras.json'))
        Obra.obras = { int(key): Obra(obra) for key, obra in obras.items() }
    
    @staticmethod
    def salvar_obras_tojson():
        obras = { key: obra.to_dict() for key, obra in Obra.obras.items() }
        with open('./treele_dados/bases/Obras.json', 'w') as outfile:
            json.dump(obras, outfile, ensure_ascii=False, indent=4)
    
class Coordenadas:

    def __init__(self, coordenadas: dict) -> None:        
        self.latitude = coordenadas['latitude']
        self.longitude = coordenadas['longitude']

    @staticmethod
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
            coordenadas = {
                "latitude": location["lat"],
                "longitude": location["lng"]
            }
            return Coordenadas(coordenadas)
        else:
            return None