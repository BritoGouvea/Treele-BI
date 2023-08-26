from datetime import datetime
import requests
import json
import os
from sienge_classes import get_lists_from_sienge, baseURL

class Obra:

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
        self.orçamento = None
        self.solicitações = []
        Obra.path(self.id)

    def to_dict(self) -> dict:
        data_dict = self.__dict__.copy()
        data_dict['coordenadas'] = self.coordenadas.__dict__
        data_dict.pop('solicitações')
        data_dict.pop('orçamento')
        return data_dict

    def __repr__(self) -> str:
        return f"< {self.id} - {self.nome} >"

    @staticmethod
    def traduzir(enterprise):
        return {
            'id': enterprise['id'],
            'nome': enterprise['name'],
            'cnpj': enterprise['cnpj'],
            'endereço': enterprise['adress'],
            'data': enterprise['creationDate'],
            'coordenadas': None
        }
    @staticmethod
    def path(id_obra: int) -> str:
        raiz = os.getcwd()
        diretorioObra = os.path.join(raiz, f"dados/obras/obra_{id_obra}")
        diretorioExiste = os.path.exists(diretorioObra)
        if not diretorioExiste:
            os.mkdir(diretorioObra)
        return diretorioObra
        
    @staticmethod
    def abrir() -> dict:
        obras = json.load(open(f'./dados/bases/Obras.json'))
        return { int(key): Obra(obra) for key, obra in obras.items() }
    
    @staticmethod
    def carregar() -> dict:
        url = baseURL + f"/enterprises"
        obras = []
        get_lists_from_sienge(obras, url)
        obras_dict = { obra['id']: Obra(Obra.traduzir(obra)) for obra in obras }
        Obra.salvar(obras_dict)
        return obras_dict

    @staticmethod
    def salvar(obras: dict):
        with open(f'./dados/bases/Obras.json', 'w') as outfile:
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