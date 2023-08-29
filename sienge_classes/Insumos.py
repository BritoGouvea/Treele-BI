import json
from sienge_classes import get_lists_from_sienge, baseURL

class GrupoDeRecursos:

    def __init__(self, grupo_de_recursos) -> None:
        self.id = grupo_de_recursos['id']
        self.descrição = grupo_de_recursos['descrição']
        self.id_referência = grupo_de_recursos['id_referência']

class CategoriaFinanceira:

    def __init__(self, categoria_financeira) -> None:
        self.id = categoria_financeira['id']
        self.descrição = categoria_financeira['descrição']

class Opção:

    def __init__(self, opção) -> None:
        self.id = opção['id']
        self.descrição = opção['descrição']

class Marca:

    def __init__(self, marca) -> None:
        self.id = marca['id']
        self.descrição = marca['descrição']

class Insumo:

    def __init__(self, insumo: dict) -> None:
        self.id = insumo['id']
        self.descrição = insumo['descrição']
        self.unidade = insumo['unidade']
        self.categoria = insumo['categoria']
        self.código_do_recurso = insumo['código_do_recurso']
        self.opções = [ Opção(opção) for opção in insumo['opções'] ]
        self.marcas = [ Marca(marca) for marca in insumo['marcas'] ]

    def to_dict(self):
        data_dict = self.__dict__.copy()
        data_dict['opções'] = [ opção.__dict__ for opção in self.opções ]
        data_dict['marcas'] = [ marca.__dict__ for marca in self.marcas ]
        return data_dict

    @staticmethod
    def traduzir(insumo: dict) -> dict:
        return {
            "id": insumo["id"],
            "descrição": insumo['description'],
            "unidade": insumo['unitOfMeasure'],
            "categoria": insumo['category'],
            "código_do_recurso": insumo['resourceCode'],
            "opções": [ {"id": opção['id'], "descrição": opção['description']} for opção in insumo['details'] ],
            "marcas": [ {"id": marca['id'], "descrição": marca['description']} for marca in insumo['trademarks'] ]
        }
    
    @staticmethod
    def abrir(obra):
        lista_insumos = json.load(open(f'./dados/obras/obra_{obra.id}/Insumos.json'))
        return { int(key): Insumo(insumo) for key, insumo in lista_insumos.items() }

    @staticmethod
    def carregar(obra) -> dict:
        url = baseURL + f"/building-cost-estimations/{obra.id}/resources"
        insumos = []
        get_lists_from_sienge(insumos, url)
        insumosDaObra = { insumo['id']: Insumo(Insumo.traduzir(insumo)) for insumo in insumos }
        Insumo.salvar_insumos(obra, { key: insumo.to_dict() for key, insumo in insumosDaObra.items() })
        return insumosDaObra

    @staticmethod
    def salvar_insumos(obra, insumos: dict):
        with open(f'./dados/obras/obra_{obra.id}/Insumos.json', 'w') as outfile:
            json.dump(insumos, outfile, ensure_ascii=False, indent=4)

class InsumoGeral(Insumo):

    def __init__(self, insumo: dict) -> None:
        super().__init__(insumo)
        self.grupo_de_recursos = GrupoDeRecursos(insumo['grupo_de_recursos'])
        self.categoria_financeira = CategoriaFinanceira(insumo['categoria_financeira'])
        self.status = insumo['status']

    def to_dict(self):
        data_dict = self.__dict__.copy()
        data_dict['grupo_de_recursos'] = self.grupo_de_recursos.__dict__
        data_dict['categoria_financeira'] = self.categoria_financeira.__dict__
        data_dict['opções'] = [ opção.__dict__ for opção in self.opções ]
        data_dict['marcas'] = [ marca.__dict__ for marca in self.marcas ]
        return data_dict

    @staticmethod
    def traduzir(insumo: dict) -> dict:
        return {
            "id": insumo["id"],
            "descrição": insumo['description'],
            "unidade": insumo['unitOfMeasure'],
            "categoria": insumo['category'],
            "código_do_recurso": insumo['resourceCode'],
            "grupo_de_recursos": {
                "id": insumo['resourceGroup']['id'],
                "descrição": insumo['resourceGroup']['description'],
                "id_referência": insumo['resourceGroup']['referenceId']
            },
            "categoria_financeira": {
                "id": insumo['financialCategory']['id'],
                "descrição": insumo['financialCategory']['description']
            },
            "status": insumo['status'],
            "opções": [ {"id": opção['id'], "descrição": opção['description']} for opção in insumo['details'] ],
            "marcas": [ {"id": marca['id'], "descrição": marca['description']} for marca in insumo['trademarks'] ]
        }
    
    @staticmethod
    def abrir() -> dict:
        lista_insumos = json.load(open('./dados/bases/Insumos.json'))
        return { int(key): InsumoGeral(insumo) for key, insumo in lista_insumos.items() }

    @staticmethod
    def carregar() -> dict:
        url = baseURL + f"/enterprises"
        insumos = []
        get_lists_from_sienge(insumos, url)
        insumos_dict = { insumo['id']: InsumoGeral(InsumoGeral.traduzir(insumo)) for insumo in insumos }
        InsumoGeral.salvar(insumos_dict)
        return insumos_dict
    
    @staticmethod
    def salvar(lista_insumos: dict):
        with open('./dados/bases/Insumos.json', 'w') as outfile:
            json.dump(lista_insumos, outfile, ensure_ascii=False, indent=4)