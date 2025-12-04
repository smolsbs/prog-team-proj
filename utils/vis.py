import json
import plotly.express as px
import pandas as pd
from dash import Dash, html, Input, Output, dcc, callback
import parser as parser


@callback(
    Output('dump-json', 'children'),
    Input('map3D-view', 'clickData')
)
def display_clicked_content(clickData):
    return json.dumps(clickData, indent=2)

def update_map(clickData):
    return 

df = parser.parse("dados.txt")

map2D = px.scatter_map(df, lat="Latitude", lon="Longitude", map_style="satellite")
map3D = px.scatter_3d(df, x="Longitude", y="Latitude", z="Profundidade")
map3D.update_scenes(zaxis_autorange="reversed")

app = Dash()
app.layout = html.Div(children=[
    dcc.Graph(
        id="map3D-view",
        figure=map3D
    ),
    dcc.Graph(
        id="map2D-view",
        figure=map2D
    ),
    html.Div(children=[html.Pre(id='dump-json', style={'overflowX': 'scroll'}, children="1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\n13\n14\n15")
])])

if __name__ == '__main__':
    app.run(debug=True)