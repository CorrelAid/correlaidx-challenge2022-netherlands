from flask import Flask
from dash import Dash, dcc, html, Input, Output, dash_table
import dash_leaflet as dl
import pandas as pd
import os

server = Flask(__name__)
app = Dash(__name__, server=server)

#load data
nl_data = pd.read_csv(os.path.join(os.path.dirname(__file__),"data", "addresses_nl.csv"))
nl_data = nl_data.dropna(subset=['longitude'])

#define dashboard elements
app.layout = html.Div([
    html.H4('Dutch Addresses in the Offshore Leaks datasets'),
    html.P("Select a data leak"),
    dcc.RadioItems(
        id='nl-map-leak',
        options=["All", "Paradise Papers", "Offshore Leaks", "Bahamas Leaks", "Pandora Papers ", 'Panama Papers'],
        value="All",
        inline=True
    ),
    dash_table.DataTable(data=nl_data.to_dict('records'), id='summary-table', fill_width=False),
    dl.Map(id="leaflet-map", style={'width': '1000px', 'height': '500px'}, center=[52, 4.88], zoom=10,
           children=[dl.TileLayer()]),
])

#define dashboard control actions
@app.callback(
    Output("leaflet-map", "children"),
    Output("summary-table", "data"),
    Input("nl-map-leak", "value"))
def display_map(leak):
    nl_data_selection = nl_data
    if leak != "All":
        nl_data_selection = nl_data_selection[nl_data_selection['leak'] == leak]
    nl_data_summary = [{'label':'Found addresses', 'total' :nl_data_selection.shape[0]}]
    markers = [dl.Marker(dl.Tooltip(row["address"]), position=[row["latitude"], row["longitude"]]) for i, row in nl_data_selection.iterrows()]
    return [dl.TileLayer(), dl.LayerGroup(markers)], nl_data_summary


if __name__ == "__main__":
    app.run_server(debug=True)
