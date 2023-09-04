import os

from sienge_classes import Obras
from sienge_classes.Insumos import InsumoGeral
from sienge_classes.SolicitaçãoDeCompras import SolicitaçãoDeCompras, Item_Solicitação

raiz = os.getcwd()
bases = os.path.join(raiz, f'dados/bases')
if not os.path.exists(bases):
    os.mkdir(bases)

caminho_insumos = os.path.join(bases, 'Insumos.json')
insumos = InsumoGeral.abrir() if os.path.exists(caminho_insumos) else InsumoGeral.carregar()

caminho_obras = os.path.join(bases, 'Obras.json')
obras = Obras.abrir() if os.path.exists(caminho_obras) else Obras.carregar()
for obra in obras.values():
    print(obra)
    obra.criar_orçamento()

caminho_solicitações = os.path.join(bases, 'SolicitaçõesDeCompras.json')
solicitações = SolicitaçãoDeCompras.abrir(obras) if os.path.exists(caminho_solicitações) else {}
if solicitações:
    última_data = max(( solicitação.data for solicitação in solicitações.values() ))
else:
    última_data = None

itens_solicitações = Item_Solicitação.carregar(solicitações, obras, insumos, última_data)