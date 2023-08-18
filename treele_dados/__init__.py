import json
from sienge_classes.Obras import Obra
from sienge_classes.CustosUnitários import Insumo
from sienge_classes.SolicitaçãoDeCompras import SolicitaçãoDeCompras, Item_SolicitaçãoDeCompras

Obra.criar_obras()
Insumo.criar_insumos()
SolicitaçãoDeCompras.criar_solicitações()
Item_SolicitaçãoDeCompras.criar_itens()



# def carregar_dados(nome_arquivo):
#     return json.load(open(f"./treele_dados/bases/{nome_arquivo}"))

# def pegar_obra(obras: [Obra], propriedade: str, valor) -> Obra or None:
#     for obra in obras:
#         if obra.to_dict()[propriedade] == valor:
#             return obra
#     return None

# def criar_obra(obra) -> Obra:
#     id = obra['id']
#     nome = obra['nome']
#     cnpj = obra['cnpj']
#     endereço = obra['endereço']
#     coordenadas = Coordenadas(obra['coordenadas'])
#     data = obra['data']
#     return Obra(id, nome, cnpj, endereço, coordenadas, data)

# def criar_solicitação_de_compra(solicitação: dict, obras: [Obra]) -> SolicitaçãoDeCompras:
#     id = solicitação['id']
#     obra = pegar_obra(obras, solicitação['obra'])
#     data = solicitação['data']
#     status = solicitação['status']
#     criado_por = solicitação['criado_por']
#     return SolicitaçãoDeCompras(id, obra, data, status, criado_por)

# def criar_item_de_solicitação_de_compra(item: dict) -> Item_SolicitaçãoDeCompras:
#     id = item['id']
#     produto = item['produto']
#     quantidade = item['quantidade']
#     unidade = item['unidade']
#     autorizado = item['autorizado']
#     data_autorização = item['data_autorização']
#     return Item_SolicitaçãoDeCompras(id, produto, quantidade, unidade, autorizado, data_autorização)

# sienge_insumos = json.load(open(root_sienge_consultas + 'CustosUnitários.json'))
# insumos_traduzidos = [ traduzir_json_sienge_insumos(insumo) for insumo in sienge_insumos ]


# # obras = [ criar_obra(obra) for obra in carregar_dados('Obras.json') ]
# insumos = [ Insumo(insumo) for insumo in insumos_traduzidos ]
# # solicitações_de_compra = [ criar_solicitação_de_compra(solicitação, obras) for solicitação in carregar_dados('SolicitaçõesDeCompras.json') ]

# # class Datamodel:
        
# #     def __init__(self, obras, solicitações_de_compra) -> None:
# #         self.obras = obras
# #         self.solicitações_de_compra = solicitações_de_compra

# # datamodel = Datamodel(obras, solicitações_de_compra)