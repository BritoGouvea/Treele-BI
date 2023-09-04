from datetime import datetime, date
import json
import requests
import os
from sienge_classes import baseURL, get_lists_from_sienge, get_item_from_sienge

class SolicitaçãoDeCompras:

    def __init__(self, solicitação: dict, obras: dict) -> None:
        self.id = solicitação['id']
        self.obra = obras[solicitação['obra']]
        self.data = date.fromisoformat(solicitação['data'])
        self.status = solicitação['status']
        self.criado_por = solicitação['criado_por']
        self.itens = []

    def __repr__(self) -> str:
        return f"<Obra: {self.obra.nome} - {self.id}>"

    def to_dict(self) -> dict:
        data_dict = self.__dict__.copy()
        data_dict['obra'] = self.obra.id
        data_dict['data'] = self.data.isoformat()
        data_dict.pop('itens')
        return data_dict

    @staticmethod
    def abrir(obras: dict, solicitações: dict = None) -> dict:
        if not solicitações:
            solicitações = json.load(open('./dados/bases/SolicitaçõesDeCompras.json'))
        return { int(key): SolicitaçãoDeCompras(solicitação, obras) for key, solicitação in solicitações.items() }

    @staticmethod
    def carregar(id: int, obras: dict) -> dict:
        url = baseURL + f"/purchase-requests/{id}"
        sienge_item = get_item_from_sienge(url)
        solicitação = SolicitaçãoDeCompras.traduzir(sienge_item)
        return { solicitação['id']: SolicitaçãoDeCompras(solicitação, obras) }

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

class Item_Solicitação:

    def __init__(self, item: dict, solicitações: dict, insumos: dict) -> None:
        self.solicitação_de_compra = solicitações[item['solicitação_de_compra']]
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
        try:
            self.apropriações = item['apropriações']
        except:
            self.apropriações = None

    def __repr__(self) -> str:
        return f"<{self.solicitação_de_compra.obra.nome} - {self.produto.descrição}:{self.quantidade} {self.produto.unidade}>"

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
    def abrir(solicitações: dict, insumos: dict) -> dict:
        lista_itens = json.load(open('./dados/bases/ItensDeSolicitaçãoDeCompras.json'))
        return { key: Item_Solicitação(item, solicitações, insumos) for key, item in lista_itens.items() }

    @staticmethod
    def carregar(solicitações: dict, obras: dict, insumos: dict, última_data: date) -> dict:
        itens = None
        if última_data:
            params = {'startDate': última_data.isoformat()}
            itens = Item_Solicitação.abrir(solicitações, insumos)
        url = baseURL + '/purchase-requests/all/items'
        itens_sienge = []
        get_lists_from_sienge(itens_sienge, url, params= params)
        for id in ( item['purchaseRequestId'] for item in itens_sienge ):
            try:
                solicitações[id]
            except:
                solicitações.update(SolicitaçãoDeCompras.carregar(id, obras))
        SolicitaçãoDeCompras.salvar({ key: solicitação.to_dict() for key, solicitação in solicitações.items() })
        novos_itens = { f"{item['purchaseRequestId']}.{item['itemNumber']}": Item_Solicitação(Item_Solicitação.traduzir(item), solicitações, insumos) for item in itens_sienge }
        for key, item in novos_itens.items():
            try:
                itens[key]
            except:
                itens.update({key: item})
        Item_Solicitação.salvar({ key: item.to_dict() for key, item in itens.items() })
        return itens

    @staticmethod
    def salvar(itens: dict) -> None:
        with open('./dados/bases/ItensDeSolicitaçãoDeCompras.json', 'w') as outfile:
            json.dump(itens, outfile, ensure_ascii=False, indent=4)

    @staticmethod
    def traduzir(item: dict):
        return {
            'solicitação_de_compra': item['purchaseRequestId'],
            'número': item['itemNumber'],
            'produto': item['productId'],
            'opção': item['detailId'],
            'marca': item['trademarkId'],
            'quantidade': item['quantity'],
            'autorizado': item['authorized'],
            'data_autorização': None
        }