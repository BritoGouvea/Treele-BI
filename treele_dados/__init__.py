import json
import requests
from requests.auth import HTTPBasicAuth

from sienge_classes.Obras import Obra
from sienge_classes.CustosUnitários import Insumo
from sienge_classes.SolicitaçãoDeCompras import SolicitaçãoDeCompras, Item_SolicitaçãoDeCompras

Obra.criar_obras()
Insumo.criar_insumos()
SolicitaçãoDeCompras.criar_solicitações()
Item_SolicitaçãoDeCompras.criar_itens()