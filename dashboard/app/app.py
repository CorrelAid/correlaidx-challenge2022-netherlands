from flask import Flask
from dash import Dash, dcc, html, Input, Output, dash_table
import dash_leaflet as dl
from dash_extensions.javascript import assign
import pandas as pd
import os

server = Flask(__name__)
app = Dash(__name__, server=server)

# create javascript function that filters on leak
geojson_filter = assign("function(feature, context){return context.props.hideout.includes(feature.properties.leak);}")
filter_options = ["All", "Paradise Papers", "Offshore Leaks", "Bahamas Leaks", "Pandora Papers ", 'Panama Papers']


# load data
nl_data = pd.read_csv(os.path.join(os.path.dirname(__file__), "assets", "addresses_nl.csv"))

#define dashboard elements
app.layout = html.Div([
    html.H4('Dutch Addresses in the Offshore Leaks datasets'),
    html.P("Select a data leak"),
    dcc.RadioItems(
        id='nl-map-leak',
        options=filter_options,
        value="All",
        inline=True
    ),
    dash_table.DataTable(data=[], id='summary-table', fill_width=False),
    html.Div(children=[
        dl.Map(id="leaflet-map", style={'width': '1000px', 'height': '500px'}, center=[52, 4.88], zoom=10,
           children=[dl.TileLayer(),
                     dl.GeoJSON(url="/assets/addresses_nl.json", options=dict(filter=geojson_filter),
                                hideout=filter_options, children=[dl.Tooltip(id="tooltip")],
                                id='address-markers')]),
        html.H3(children="Text", id='marker-text')
    ], style={'display': 'flex', 'flex-direction': 'row'})
])

#define dashboard control actions
@app.callback(
    Output("address-markers", "hideout"),
    Output("summary-table", "data"),
    Input("nl-map-leak", "value"))
def display_map(leak):
    nl_data_selection = nl_data
    chosen_filter = filter_options
    if leak != "All":
        nl_data_selection = nl_data_selection[nl_data_selection['leak'] == leak]
        chosen_filter = leak
    nl_data_summary = [{leak: 'NLD addresses', 'total': nl_data_selection.shape[0]}]
    nl_data_selection = nl_data_selection.dropna(subset=['longitude'])
    nl_data_summary = nl_data_summary + [{leak: 'Coordinates found', 'total': nl_data_selection.shape[0]}]
    return chosen_filter, nl_data_summary

@app.callback(
    Output("marker-text", "children"),
    Input("address-markers", "click_feature"))
def marker_text(feature):
    if feature is not None:
        return str(feature['properties']['name'])


@app.callback(
    Output("tooltip", "children"),
    Input("address-markers", "hover_feature"))
def marker_text(feature):
    if feature is None:
        return None
    else:
        return str(feature['properties']['name'])


if __name__ == "__main__":
    app.run_server(debug=False)
# note a bug in dash_leaflet means the hideout property will give an error if run in debug mode
