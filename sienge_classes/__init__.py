import json
import os
import requests
from requests.auth import HTTPBasicAuth

company = "treele"
username = "treele-sistema-x"
token = "hinUoLzppvsCqpIRt9blchboNPLGf4V4"
baseURL = f"https://api.sienge.com.br/{company}/public/api/v1"
auth = HTTPBasicAuth(username, token)

class Caminho:

    def __init__(self, id: int) -> None:
        self.raiz = os.getcwd() + f'/dados/obras/obra_{id}'
        self.insumos = self.raiz + f'/Insumos.json'
        self.planilhas = self.raiz + f'/Planilhas.json'
        self.eap = self.raiz + f'/EAP.json'
        self.recursos = self.raiz + f'Recursos.json'

def get_lists_from_sienge(items: list, url: str, offset: int = 0) -> list:
    b_response = requests.get(
        url=url,
        auth=auth,
        params={
            "offset": offset,
            "limit": 200
        }
    )
    requestJson = json.loads(b_response.content.decode("utf-8"))
    print(requestJson)
    items.extend(requestJson['results'])

    if len(items) < requestJson['resultSetMetadata']['count']:
        get_lists_from_sienge(items, url, offset + 200)