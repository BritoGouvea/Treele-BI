import json
import requests
import os
from sienge_classes.DadosLogin import baseURL, auth
from sienge_classes.Obras import Obra
from sienge_classes.Insumos import Insumo

class Orçamento:
    
    def __init__(self, orçamento: dict) -> None:
        self.obra = Obra.obras[orçamento['obra']]
        self.path = orçamento['path']
        # self.insumos = { int(key): Insumo(insumo) for key, insumo in orçamento['insumos'].items() } if orçamento['insumos'] else Orçamento.carregar_insumos(self.obra)
        # self.planilhas = { int(key): Planilha(self.obra, self.insumos, planilha) for key, planilha in orçamento['planilhas'].items() } if orçamento['planilhas'] else Orçamento.carregar_planilhas(self.obra)

    def __repr__(self) -> str:
        return f"< Orçamento da obra: {self.obra.id} - {self.obra.nome} >" 

    def to_dict(self) -> dict:
        data_dict = self.__dict__.copy()
        data_dict['obra'] = self.obra.id
        data_dict['planilhas'] = { key: planilha.to_dict() for key, planilha in self.planilhas.items() }
        data_dict['insumos'] = { key: insumo.to_dict() for key, insumo in self.insumos.items() }
        return data_dict

    def salvar(self):
        with open(f'./treele_dados/bases/orçamento_obra_{self.obra.id}.json', 'w') as outfile:
            json.dump(self.to_dict(), outfile, ensure_ascii=False, indent=4)

    @staticmethod
    def carregar(arquivo: str):
        orçamento_json = json.load(open(arquivo))
        return Orçamento(orçamento_json)

    @staticmethod
    def carregar_planilhas(obra: Obra) -> list:

        def get_sheets(planilhas: list, url: str, offset: int = 0) -> list:
            b_response = requests.get(
                url=url,
                auth=auth,
                params={
                    "offset": 0,
                    "limit": 200
                }
            )
            requestJson = json.loads(b_response.content.decode("utf-8"))
            planilhas.extend(requestJson['results'])

            if len(planilhas) < requestJson['resultSetMetadata']['count']:
                get_sheets(planilhas, url, offset + 200)

        url = baseURL + f"/building-cost-estimations/{obra.id}/sheets"
        planilhas = []
        get_sheets(planilhas, url)
        return { planilha['id']: Planilha(obra, Planilha.traduzir(planilha)) for planilha in planilhas }

    @staticmethod
    def carregar_insumos(obra: Obra) -> list:

        def get_resources(insumos: list, url: str, offset: int = 0) -> list:
            b_response = requests.get(
                url=url,
                auth=auth,
                params={
                    "offset": 0,
                    "limit": 200
                }
            )
            requestJson = json.loads(b_response.content.decode("utf-8"))
            insumos.extend(requestJson['results'])

            if len(insumos) < requestJson['resultSetMetadata']['count']:
                get_resources(insumos, url, offset + 200)

        url = baseURL + f"/building-cost-estimations/{obra.id}/resources"
        insumos = []
        get_resources(insumos, url)
        return { insumo['id']: Insumo(Insumo.traduzir(insumo)) for insumo in insumos }

class Planilha:

    def __init__(self, obra: Obra, insumos: dict, planilha: dict) -> None:
        self.obra = obra
        self.id = int(planilha['id'])
        self.descrição = planilha['descrição']
        self.status = planilha['status']
        self.itens = { key: Itens_Planilha(insumos, item) for key, item in planilha['itens'].items() } if planilha['itens'] else Planilha.pegar_itens(self.obra, insumos, self.id)
        Planilha.pegar_recursos(self.obra, insumos, self.id, self.itens)

    def __repr__(self) -> str:
        return f"< Planilha: {self.id} - {self.descrição} >"

    def to_dict(self) -> dict:
        data_dict = self.__dict__.copy()
        data_dict.pop('obra')
        data_dict['itens'] = { key: item.to_dict() for key, item in self.itens.items() }
        return data_dict

    @staticmethod
    def pegar_itens(obra: Obra, insumos: dict, id: int) -> dict:

        def get_items(itens: list, url: str, offset: int = 0) -> None:
            b_response = requests.get(
                url=url,
                auth=auth,
                params={
                    "offset": offset,
                    "limit": 200
                }
            )
            requestJson = json.loads(b_response.content.decode("utf-8"))
            itens.extend(requestJson['results'])

            if len(itens) < requestJson['resultSetMetadata']['count']:
                get_items(itens= itens, url= url, offset= offset + 200)

        url=baseURL + f"/building-cost-estimations/{obra.id}/sheets/{id}/items"
        itens = []
        get_items(itens= itens, url= url)
        return { item['wbsCode']: Itens_Planilha(insumos, Itens_Planilha.traduzir(item)) for item in itens }
    
    @staticmethod
    def pegar_recursos(obra: Obra, insumos: dict, id_planilha: int, itens: dict) -> None:

        for value in itens.values():
            if value.recursos:
                return
            break

        def get_resources(id_planilha: int, itens: list, url: str, offset: int = 0) -> None:
            b_response = requests.get(
                url=url,
                auth=auth,
                params={
                    "offset": offset,
                    "limit": 200,
                    "buildingUnitId": id_planilha
                }
            )
            requestJson = json.loads(b_response.content.decode("utf-8"))
            itens.extend(requestJson['results'])

            if len(itens) < requestJson['resultSetMetadata']['count']:
                get_resources(id_planilha= id_planilha, itens= itens, url= url, offset= offset + 200)

        url=baseURL + f"/building-cost-estimations/{obra.id}/cost-estimate-resources"
        recursos = []
        get_resources(id_planilha= id_planilha, itens= recursos, url= url)
        for r in recursos:
            recurso = Recurso(insumos, Recurso.traduzir(r))
            itens[recurso.wbs].recursos | {recurso.insumo.id: recurso}


    @staticmethod
    def traduzir(sheet: dict) -> dict:
        return {
            'id': sheet['id'], 
            'descrição': sheet['description'],
            'status': sheet['status'],
            'itens': {}
        }


class Itens_Planilha:

    def __init__(self, insumos: dict, item: dict) -> None:
        self.id = int(item['id'])
        self.wbs = item['wbs']
        self.descrição = item['descrição']
        self.unidade = item['unidade']
        self.quantidade = item['quantidade']
        self.preçoUnitário = item['preçoUnitário']
        self.preçoTotal = item['preçoTotal']
        self.preçoPorCategoria = item['preçoPorCategoria']
        self.recursos = { key: Recurso(insumos, recurso) for key, recurso in item['recursos'] } if item['recursos'] else {}

    
    def __repr__(self) -> str:
        return f"< {self.wbs} - {self.descrição} >"

    def to_dict(self):
        data_dict = self.__dict__.copy()
        data_dict['recursos'] = { key: value.to_dict() for key, value in self.recursos.items() }
        return data_dict
    
    @staticmethod
    def traduzir(item: dict) -> dict:
        return {
            'id': item['id'],
            'wbs': item['wbsCode'],
            'descrição': item['description'],
            'unidade': item['unitOfMeasure'],
            'quantidade': item['quantity'],
            'preçoUnitário': item['unitPrice'],
            'preçoTotal': item['totalPrice'],
            'preçoPorCategoria': [{"categoria": preço['category'], "preçoUnitário": preço['unitPrice'], "preçoTotal": preço['totalPrice']} for preço in item['pricesByCategory']],
            'recursos': {}
        }
    
class Recurso:

    def __init__(self, insumos: dict, recurso: dict) -> None:
        self.planilha = recurso['planilha']
        self.wbs = recurso['wbs']
        self.itemId = recurso['itemId']
        self.insumo = insumos[recurso['insumo']]
        self.quantidade = recurso['quantidade']
        self.preçoUnitário = recurso['preçoUnitário']
        self.preçoTotal = recurso['preçoTotal']
        self.data = recurso['data']

    def to_dict(self) -> dict:
        data_dict = self.__dict__.copy()
        data_dict['wbs'] = self.wbs.id
        data_dict['planilha'] = self.planilha
        data_dict['insumo'] = self.insumo.id

    @staticmethod
    def traduzir(resource) -> dict:
        return {
            'planilha': resource['buildingUnitId'],
            'wbs': resource['sheetItemWbsCode'],
            'itemId': resource['sheetItemId'],
            'insumo': resource['id'],
            'quantidade': resource['quantity'],
            'preçoUnitário': resource['unitPrice'],
            'preçoTotal': resource['totalPrice'],
            'data': resource['priceDate']
        }