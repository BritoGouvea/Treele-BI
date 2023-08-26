from datetime import datetime
import json
import requests
from sienge_classes.DadosLogin import baseURL, auth
from sienge_classes.Obras import Obra
from sienge_classes.Insumos import Insumo

class SolicitaçãoDeCompras:

    solicitações = None

    def __init__(self, solicitação: dict) -> None:
        self.id = solicitação['id']
        self.obra = Obra.obras[solicitação['obra']]
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
    def criar():

        def cria_e_anexa(solicitação_dict: dict) -> SolicitaçãoDeCompras:
            solicitação = SolicitaçãoDeCompras(solicitação_dict)
            solicitação.obra.solicitações.append(solicitação)
            return solicitação
        
        lista_solicitações = json.load(open('./treele_dados/bases/SolicitaçõesDeCompras.json'))
        SolicitaçãoDeCompras.solicitações = { int(key): cria_e_anexa(solicitação) for key, solicitação in lista_solicitações.items() }

    @staticmethod
    def salvar():
        lista_solicitações = { key: solicitação.to_dict() for key, solicitação in SolicitaçãoDeCompras.solicitações.items() }
        with open('./treele_dados/bases/SolicitaçõesDeCompras.json', 'w') as outfile:
            json.dump(lista_solicitações, outfile, ensure_ascii=False, indent=4)

class Item_SolicitaçãoDeCompras:

    itens = None

    def __init__(self, item: dict) -> None:
        self.solicitação_de_compra = SolicitaçãoDeCompras.solicitações[item['solicitação_de_compra']]
        self.número = item['número']
        self.produto = Insumo.insumos[item['produto']]
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
            auth=auth,
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