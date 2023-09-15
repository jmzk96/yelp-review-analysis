"""View for the weatherstation route with callbacks. Use layout in index.py"""

import dash_core_components as dcc  # type: ignore
import dash_html_components as html  # type: ignore
from dash.dependencies import Input, Output  # type: ignore
import plotly.express as px  # type: ignore
from app import app
from src.database_handler import DatabaseExecutor


db_exec = DatabaseExecutor()

w_df = db_exec.get_weatherstation_data_where_hcn()
w_df_all = db_exec.get_weatherstation_data()

station_options = [
    {'label': 'Only with hcn data',
     'value': 'limited'},
    {'label': 'All stations',
     'value': 'all'},
]
station_radio = dcc.RadioItems(
    id='station-scope',
    options=station_options,
    persistence=True, persistence_type='session',
    value='limited'
)

layout = html.Div([
    html.H1('Weather station within the GHCND_HCN weather data / All Station',
            style={"textAlign": "center"}),

    html.Div([
        html.Div([
            html.Label([
                "Choose scope",
                station_radio,
            ]),
        ], className='six columns'),
    ], className='row'),

    dcc.Graph(id='my-weatherstation', figure={}),
])


@app.callback(
    Output(component_id='my-weatherstation', component_property='figure'),
    [Input(component_id='station-scope', component_property='value')]
)
def display_value(scope):
    """Draw each weather station on a map.
    Either use only ones with existing data or all existing stations.

    Args:
        scope (str): Scope for weather stations

    Returns:
        px.scatter_mapbox: Plotly express scatter mapbox figure
    """
    if scope == "limited":
        plotdata = w_df
    else:
        plotdata = w_df_all
    fig = px.scatter_mapbox(
        plotdata, lat="lat",
        lon="lon",
        hover_name="name",
        hover_data=["sid"],
        mapbox_style="open-street-map", zoom=4,
        size_max=100,
        height=1000
    )

    return fig
