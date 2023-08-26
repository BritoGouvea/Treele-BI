import json
import requests
from requests.auth import HTTPBasicAuth
import os

from sienge_classes.DadosLogin import company
from sienge_classes.Obras import Obra
from sienge_classes.Insumos import Insumo
from sienge_classes.SolicitaçãoDeCompras import SolicitaçãoDeCompras, Item_SolicitaçãoDeCompras
from sienge_classes.OrçamentoDeObra import Orçamento

raiz = os.getcwd()
bases = os.path.join(raiz, f'dados/bases')
caminho_obras = os.path.join(bases, 'Obras.json')

obras = Obra.abrir() if os.path.exists(caminho_obras) else Obra.carregar()