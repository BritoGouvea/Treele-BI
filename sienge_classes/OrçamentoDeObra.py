import json
import os
from sienge_classes import Caminho, get_lists_from_sienge, baseURL
from sienge_classes.Insumos import Insumo

class Orçamento:

    def __init__(self, obra) -> None:
        self.obra = obra
        self.caminho = Caminho(self.obra.id)
        self.insumos = Insumo.abrir(self.obra) if os.path.exists(self.caminho.insumos) else Insumo.carregar(self.obra)
        self.planilhas = Planilha.abrir(self.obra) if os.path.exists(self.caminho.planilhas) else Planilha.carregar(self.obra)
        ItemEAP.abrir(self.obra, self.planilhas)

    def __repr__(self) -> str:
        return f"< Orçamento da obra: {self.obra.id} - {self.obra.nome} >" 

    def to_dict(self) -> dict:
        data_dict = self.__dict__.copy()
        data_dict['obra'] = self.obra.id
        data_dict['planilhas'] = { key: planilha.to_dict() for key, planilha in self.planilhas.items() }
        data_dict['insumos'] = { key: insumo.to_dict() for key, insumo in self.insumos.items() }
        return data_dict

class Planilha:

    def __init__(self, planilha: dict) -> None:
        self.id = int(planilha['id'])
        self.descrição = planilha['descrição']
        self.status = planilha['status']
        self.eap = {}

    def __repr__(self) -> str:
        return f"< Planilha: {self.id} - {self.descrição} >"

    def to_dict(self) -> dict:
        data_dict = self.__dict__.copy()
        data_dict.pop('obra')
        data_dict.pop('eap')
        data_dict['itens'] = { key: item.to_dict() for key, item in self.itens.items() }
        return data_dict

    @staticmethod
    def abrir(obra) -> dict:
        planilhas = json.load(open(f'./dados/obras/obra_{obra.id}/Planilhas.json'))
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
    def traduzir(sheet: dict) -> dict:
        return {
            'id': sheet['id'], 
            'descrição': sheet['description'],
            'status': sheet['status'],
        }

class ItemEAP:

    def __init__(self, item: dict) -> None:
        self.id = int(item['id'])
        self.eap = item['eap']
        self.descrição = item['descrição']
        self.unidade = item['unidade']
        self.quantidade = item['quantidade']
        self.preçoUnitário = item['preçoUnitário']
        self.preçoTotal = item['preçoTotal']
        self.preçoPorCategoria = item['preçoPorCategoria']
        self.subitens = None
        self.recursos =  None

    def __repr__(self) -> str:
        return f"< {self.eap} - {self.descrição} >"

    def to_dict(self):
        data_dict = self.__dict__.copy()
        data_dict['recursos'] = { key: value.to_dict() for key, value in self.recursos.items() }
        return data_dict

    @staticmethod
    def abrir(obra, planilhas, eaps = None) -> dict:
        if not eaps:
            eaps = json.load(open(f'./dados/obras/obra_{obra.id}/EAP.json'))
        for key, eap in eaps.items():
            itens = { item['eap']: ItemEAP(item) for item in eap }
            planilhas[int(key)].eap = ItemEAP.hierarquizar(itens)

    @staticmethod
    def hierarquizar(eap_itens: dict) -> dict:
        def organizar_eap(item_eap: ItemEAP, eaps: list, index: int = 0):
            if not len(eaps) - 1 == index:
                item_eap.subitens = { item.eap: item for item in eaps[index + 1] if item.eap.startswith(item_eap.eap)}
                for item in item_eap.subitens.values():
                    organizar_eap(item, eaps, index + 1)
            return item_eap
        keys = eap_itens.keys()
        níveis = (sorted(list(set([ len(key) for key in keys ]))))
        eaps = []
        for nível in níveis:
            eaps.append([ eap_item for eap_item in eap_itens.values() if len(eap_item.eap) == nível ])
        return { item.eap: organizar_eap(item, eaps) for item in eaps[0] }

    
    @staticmethod
    def carregar(obra, planilhas: dict) -> dict:

        eaps = {}
        for planilha in planilhas:
            url = baseURL + f"/building-cost-estimations/{obra.id}/sheets/{planilha}/items"
            itens_wbs = []
            get_lists_from_sienge(itens_wbs, url)
            itens_eap = [ ItemEAP.traduzir(item) for item in itens_wbs ]
            eaps = eaps | {planilha: itens_eap}
        ItemEAP.salvar(obra, eaps)
        ItemEAP.abrir(obra, planilhas, eaps)

    @staticmethod
    def salvar(obra, itens) -> None:
        with open(f'./dados/obras/obra_{obra.id}/EAP.json', 'w') as outfile:
            json.dump(itens, outfile, ensure_ascii=False, indent=4)

    @staticmethod
    def traduzir(item: dict) -> dict:
        return {
            'id': item['id'],
            'eap': item['wbsCode'],
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