import dash
from dash import html, dcc
from dash.dependencies import Input, Output

from dados import obras

# app = dash.Dash(__name__)

# app.layout = html.Div(id="div1",
#     children=[
#         html.H1("Treèle", id="header")
#     ]
# )

# if __name__ == '__main__':
#     app.run_server(debug=True)

# orçamento_tjm = Orçamento({
#     'obra': 8,
#     'insumos': [],
#     'planilhas': []
# })

# orçamento_tjm.salvar()

tjm = obras[8]

tjm.criar_orçamento()