import json
import os
from sienge_classes import Caminho, get_lists_from_sienge, baseURL
from sienge_classes.Insumos import Insumo, InsumoGeral

class Orçamento:

    def __init__(self, obra) -> None:
        self.obra = obra
        self.caminho = Caminho(self.obra.id)
        self.insumos = Insumo.abrir(self.obra) if os.path.exists(self.caminho.insumos) else Insumo.carregar(self.obra)
        self.planilhas = Planilha.abrir(self.obra) if os.path.exists(self.caminho.planilhas) else Planilha.carregar(self.obra)
        self.itens_eap = ItemEAP.abrir(self.obra, self.planilhas) if os.path.exists(self.caminho.eap) else ItemEAP.carregar(self.obra, self.planilhas)
        self.recursos = Recurso.abrir(self.obra, self.insumos, self.itens_eap) if os.path.exists(self.caminho.recursos) else Recurso.carregar(self.obra, self.insumos, self.itens_eap)

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
        data_dict.pop('eap')
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
            eaps_dict = json.load(open(f'./dados/obras/obra_{obra.id}/EAP.json'))
        todos_itens = {}
        for key, eap in eaps_dict.items():
            itens = { f"{key}.{item['eap']}": ItemEAP(item) for item in eap }
            todos_itens = todos_itens | itens
            planilhas[int(key)].eap = ItemEAP.hierarquizar(itens)
        return todos_itens

    @staticmethod
    def hierarquizar(eap_itens: dict) -> dict:
        def join_dicts_list(dict_list):
            return dict((key, value) for dictionary in dict_list for key, value in dictionary.items())
        def organizar(eaps: list, index: int = 0) -> None:
            if len(eaps) != index + 1:
                for key, eap in join_dicts_list(eaps[index]).items():
                    sub_dict = join_dicts_list(eaps[index + 1])
                    eap.subitens = { subitem_key: subitem for subitem_key, subitem in sub_dict.items() if subitem_key.startswith(key)}
                    organizar(eaps, index + 1)
        keys = [ key.split('.') for key in eap_itens.keys() ]
        níveis = (sorted(list(set([ len(key) for key in keys ]))))
        eaps = []
        for nível in níveis:
            eaps.append([ {eap_key: eap_item} for eap_key, eap_item in eap_itens.items() if len(eap_key.split('.')) == nível ])
        organizar(eaps)
        return { key: item for key, item in join_dicts_list(eaps[0]).items() }

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
        }
    
class Recurso:

    def __init__(self, insumos: dict, recurso: dict) -> None:
        self.planilha = int(recurso['planilha'])
        self.eap = recurso['eap']
        self.itemId = recurso['itemId']
        try:
            insumo = insumos[recurso['insumo']]
        except:
            insumos = InsumoGeral.abrir()
            insumo = insumos[recurso['insumo']]
        self.insumo = insumo
        self.quantidade = recurso['quantidade']
        self.preçoUnitário = recurso['preçoUnitário']
        self.preçoTotal = recurso['preçoTotal']
        self.data = recurso['data']

    def __repr__(self) -> str:
        return f"<{self.insumo.id} - {self.insumo.descrição}: {self.quantidade} {self.insumo.unidade}"

    def to_dict(self) -> dict:
        data_dict = self.__dict__.copy()
        data_dict['planilha'] = self.planilha
        data_dict['insumo'] = self.insumo.id
        return data_dict

    @staticmethod
    def abrir(obra, insumos: dict, itens_eap: dict, recursos: dict = None) -> dict:
        if not recursos:
            recursos = json.load(open(f'./dados/obras/obra_{obra.id}/Recursos.json'))
            recursos = { key: Recurso(insumos, recurso) for key, recurso in recursos.items() }
        for key, recurso in recursos.items():
            item_eap = itens_eap[f'{recurso.planilha}.{recurso.eap}']
            if not item_eap.recursos:
                item_eap.recursos = {key: recurso}
            else:
                item_eap.recursos = item_eap.recursos | {key: recurso}
        return recursos

    @staticmethod
    def carregar(obra, insumos: dict, itens_eap: dict):
        url = baseURL + f'/building-cost-estimations/{obra.id}/cost-estimate-resources'
        recursos = []
        get_lists_from_sienge(recursos, url)
        recursos = { f"{recurso['buildingUnitId']}.{recurso['sheetItemWbsCode']}.{recurso['id']}": Recurso(insumos, Recurso.traduzir(recurso)) for recurso in recursos }
        recursos_dict = { key: recurso.to_dict() for key, recurso in recursos.items() }
        Recurso.salvar(obra, recursos_dict)
        Recurso.abrir(obra, insumos, itens_eap, recursos = recursos_dict)

    @staticmethod
    def salvar(obra, recursos):
        with open(f'./dados/obras/obra_{obra.id}/Recursos.json', 'w') as outfile:
            json.dump(recursos, outfile, ensure_ascii=False, indent=4)

    @staticmethod
    def traduzir(resource) -> dict:
        return {
            'planilha': resource['buildingUnitId'],
            'eap': resource['sheetItemWbsCode'],
            'itemId': resource['sheetItemId'],
            'insumo': resource['id'],
            'quantidade': resource['quantity'],
            'preçoUnitário': resource['unitPrice'],
            'preçoTotal': resource['totalPrice'],
            'data': resource['priceDate']
        }