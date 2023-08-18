import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from treele_dados import Obra, Insumo, SolicitaçãoDeCompras, Item_SolicitaçãoDeCompras

app = dash.Dash(__name__)

app.layout = html.Div(id="div1",
    children=[
        html.H1("Treèle", id="header")
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)