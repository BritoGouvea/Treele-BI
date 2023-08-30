import os

from sienge_classes import Obras
from sienge_classes.Insumos import InsumoGeral
from sienge_classes.SolicitaçãoDeCompras import SolicitaçãoDeCompras, Item_SolicitaçãoDeCompras

raiz = os.getcwd()
bases = os.path.join(raiz, f'dados/bases')
if not os.path.exists(bases):
    os.mkdir(bases)

caminho_obras = os.path.join(bases, 'Obras.json')
obras = Obras.abrir() if os.path.exists(caminho_obras) else Obras.carregar()
for obra in obras.values():
    print(obra)
    obra.criar_orçamento()

caminho_insumos = os.path.join(bases, 'Insumos.json')
insumos = InsumoGeral.abrir() if os.path.exists(caminho_insumos) else InsumoGeral.carregar()

caminho_solicitações = os.path.join(bases + 'SolicitaçõesDeCompras.json')
solicitações = 1