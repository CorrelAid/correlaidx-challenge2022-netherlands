from dash import Dash, dcc, html, Input, Output
import dash_leaflet as dl
import pandas as pd
import os

app = Dash(__name__)


app.layout = html.Div([
    html.H4('Dutch Addresses in the Offshore Leaks datasets'),
    html.P("Select a data leak"),
    dcc.RadioItems(
        id='nl-map-leak',
        options=["All", "Paradise Papers", "Offshore Leaks", "Bahamas Leaks", "Pandora Papers ", 'Panama Papers'],
        value="All",
        inline=True
    ),
    dl.Map(id="leaflet-map", style={'width': '1000px', 'height': '500px'}, center=[52, 4.88], zoom=10,
           children=[dl.TileLayer()]),
])


@app.callback(
    Output("leaflet-map", "children"),
    Input("nl-map-leak", "value"))
def display_map(leak):
    nl_data = pd.read_csv(os.path.join("data", "addresses_nl.csv"))
    nl_data = nl_data.dropna()
    if leak != "All":
        nl_data = nl_data[nl_data['leak'] == leak]
    print(nl_data)
    markers = [dl.Marker(dl.Tooltip(row["address"]), position=[row["latitude"], row["longitude"]]) for i, row in nl_data.iterrows()]
    return dl.TileLayer(), dl.LayerGroup(markers)


if __name__ == "__main__":
    app.run_server(debug=True)
