import dash
from dash import html

app = dash.Dash(__name__)

app.layout = html.Div(id="div1",
    children=[
        html.H1("Treèle", id="header")
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
