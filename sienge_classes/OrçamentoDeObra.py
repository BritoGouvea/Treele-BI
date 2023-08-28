import json
import requests
import os
from sienge_classes import Caminho, get_lists_from_sienge, baseURL, auth
from sienge_classes.Insumos import Insumo

class Orçamento:

    def __init__(self, obra) -> None:
        self.obra = obra
        self.caminho = Caminho(self.obra.id)
        self.insumos = Insumo.abrir(self.obra) if os.path.exists(self.caminho.insumos) else Insumo.carregar(self.obra)
        self.planilhas = Planilha.abrir(self.obra) if os.path.exists(self.caminho.planilhas) else Planilha.carregar(self.obra)

    def __repr__(self) -> str:
        return f"< Orçamento da obra: {self.obra.id} - {self.obra.nome} >" 

    def to_dict(self) -> dict:
        data_dict = self.__dict__.copy()
        data_dict['obra'] = self.obra.id
        data_dict['planilhas'] = { key: planilha.to_dict() for key, planilha in self.planilhas.items() }
        data_dict['insumos'] = { key: insumo.to_dict() for key, insumo in self.insumos.items() }
        return data_dict

class Planilha:

    def __init__(self, obra, planilha: dict) -> None:
        self.obra = obra
        self.id = int(planilha['id'])
        self.descrição = planilha['descrição']
        self.status = planilha['status']
        self.itens = {}
        # self.itens = { key: Itens_Planilha(insumos, item) for key, item in planilha['itens'].items() } if planilha['itens'] else Planilha.pegar_itens(self.obra, insumos, self.id)
        # Planilha.pegar_recursos(self.obra, insumos, self.id, self.itens)

    def __repr__(self) -> str:
        return f"< Planilha: {self.id} - {self.descrição} >"

    def to_dict(self) -> dict:
        data_dict = self.__dict__.copy()
        data_dict.pop('obra')
        data_dict['itens'] = { key: item.to_dict() for key, item in self.itens.items() }
        return data_dict

    @staticmethod
    def abrir(obra) -> dict:
        planilhas = json.load(open(f'./dados/obras/obra_{obra.id}/Insumos.json'))
        return { int(key): Planilha(planilha) for key, planilha in planilhas.items() }

    @staticmethod
    def carregar(obra) -> dict:
        url = baseURL + f"/building-cost-estimations/{obra.id}/sheets"
        planilhas = []
        get_lists_from_sienge(planilhas, url)
        planilhas_dict = { planilha['id']: Planilha(obra, Planilha.traduzir(planilha)) for planilha in planilhas }
        Planilha.salvar(obra , { key: insumo.to_dict() for key, insumo in planilhas_dict.items() })
        return planilhas_dict
    
    @staticmethod
    def salvar(obra, planilhas: dict):
        with open(f'./dados/obras/obra_{obra.id}/Planilhas.json', 'w') as outfile:
            json.dump(planilhas, outfile, ensure_ascii=False, indent=4)
    
    @staticmethod
    def pegar_recursos(obra, insumos: dict, id_planilha: int, itens: dict) -> None:

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