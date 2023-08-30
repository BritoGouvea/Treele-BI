from datetime import datetime
import json
import requests
from sienge_classes import baseURL, get_lists_from_sienge, get_item_from_sienge
from sienge_classes.Insumos import Insumo

class SolicitaçãoDeCompras:

    def __init__(self, solicitação: dict, obras: dict) -> None:
        self.id = solicitação['id']
        self.obra = obras[solicitação['obra']]
        self.data = datetime.fromisoformat(solicitação['data'])
        self.status = solicitação['status']
        self.criado_por = solicitação['criado_por']
        self.itens = []

    def to_dict(self) -> dict:
        data_dict = self.__dict__.copy()
        data_dict['obra'] = self.obra.id
        data_dict['data'] = self.data.strftime('%Y-%m-%d')
        data_dict.pop('itens')
        return data_dict

    @staticmethod
    def abrir(solicitações: dict = None) -> dict:
        if not solicitações:
            solicitações = json.load(open('./dados/bases/SolicitaçõesDeCompras.json'))
        return { int(key): SolicitaçãoDeCompras(solicitação) for key, solicitação in solicitações.items() }

    @staticmethod
    def carregar(id: int):
        url = baseURL + f"/purchase-requests/{id}"
        solicitação = SolicitaçãoDeCompras.traduzir(get_item_from_sienge(url))
        return { solicitação['id']: SolicitaçãoDeCompras(solicitação) }

    @staticmethod
    def salvar(solicitações: dict) -> None:
        with open('./dados/bases/SolicitaçõesDeCompras.json', 'w') as outfile:
            json.dump(solicitações, outfile, ensure_ascii=False, indent=4)

    @staticmethod
    def traduzir(solicitação: dict) -> dict:
        return {
            'id': solicitação['id'],
            'obra': solicitação['buildingId'],
            'data': solicitação['requestDate'],
            'status': solicitação['status'],
            'criado_por': solicitação['createdBy']
        }

class Item_SolicitaçãoDeCompras:

    def __init__(self, item: dict, solicitações: dict, insumos: dict) -> None:
        try:
            solicitação = solicitações[item['solicitação_de_compra']]
        except:
            try:
                solicitação = SolicitaçãoDeCompras.carregar(item['solicitação_de_compra'])
            except:
                solicitação = None
                print('Solicitação de compra não encontrada no sienge')
        self.solicitação_de_compra = solicitação
        self.número = item['número']
        self.produto = insumos[item['produto']]
        self.opção = item['opção']
        self.marca = item['marca']
        self.quantidade = item['quantidade']
        self.autorizado = item['autorizado']
        if item['data_autorização']:
            data = datetime.fromisoformat(item['data_autorização'])
        else:
            data = None
        self.data_autorização = data
        self.apropriações = item['apropriações']

    def to_dict(self) -> dict:
        data_dict = self.__dict__.copy()
        data_dict['solicitação_de_compra'] = self.solicitação_de_compra.id
        data_dict['produto'] = self.produto.id
        if self.data_autorização:
            data_dict['data_autorização'] = self.data_autorização.strftime('%Y-%m-%d')
        return data_dict

    def get_building_apropriation(self) -> None:
        
        b_response = requests.get(
            url=baseURL + f"/purchase-requests/{self.solicitação_de_compra.id}/items/{self.número}/buildings-appropriations",
            params={
                "offset": 0,
                "limit": 200
            }
        )
        requestJson = json.loads(b_response.content.decode("utf-8"))
        self.apropriações.extend(requestJson['results'])

    @staticmethod
    def criar():

        def cria_e_anexa(item_solicitação_dict: dict) -> Item_SolicitaçãoDeCompras:
            item_solicitação = Item_SolicitaçãoDeCompras(item_solicitação_dict)
            item_solicitação.solicitação_de_compra.itens.append(item_solicitação)
            return item_solicitação

        lista_itens = json.load(open('./treele_dados/bases/ItensDeSolicitaçãoDeCompras.json'))
        Item_SolicitaçãoDeCompras.itens = { key: cria_e_anexa(item) for key, item in lista_itens.items() }

    @staticmethod
    def salvar():
        lista_itens = { f"{item.solicitação_de_compra.id}.{item.número}": item.to_dict() for key, item in Item_SolicitaçãoDeCompras.itens.items() }
        with open('./treele_dados/bases/ItensDeSolicitaçãoDeCompras.json', 'w') as outfile:
            json.dump(lista_itens, outfile, ensure_ascii=False, indent=4)

    @staticmethod
    def traduzir(item: dict):
        return {
            'solicitação_de_compra': item['purchaseRequestId'],
            'produto': item['productId'],
            'opção': item['detailId'],
            'marca': item['trademarkId'],
            'quantidade': item['quantity'],
            'autorizado': item['authorized'],
            'data_autorização': None
        }