"""Callbacks for the population view. Needs to be imported in index.py"""

import json
import pathlib
from dash.dependencies import Input, Output  # type: ignore
import plotly.express as px  # type: ignore
from src.database_handler import DatabaseExecutor
from app import app

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../geojson").resolve()

with open(DATA_PATH.joinpath("geojson-counties-fips.json")) as geo_file:
    counties = json.load(geo_file)

db_exec = DatabaseExecutor()

# Average Income
counties_df = db_exec.get_avg_income_counties()
states_df = db_exec.get_avg_income_states()
cluster_df = db_exec.get_avg_income_clusters()

cluster_df = cluster_df[cluster_df['clusterid'].isin([1, 2, 5, 6, 7, 9, 10])]
cluster_df['size'] = 600000
cluster_df["avg_income"] = cluster_df["avg_income"]\
    .apply(lambda x: round(x, 0))

# Age Distribution
counties_ages_df = db_exec.get_ages_counties()
states_ages_df = db_exec.get_ages_states()
cluster_ages_df = db_exec.get_ages_clusters()


@app.callback(
    Output(component_id='population-avg-income', component_property='figure'),
    [Input(component_id='county-or-state-income', component_property='value'),
     Input(component_id='show-clusters-income', component_property='value')]
)
def display_avg_income(scope, show_clusters):
    """Draw values for average income per county/state.

    Args:
        scope (str): Scope for average income

    Returns:
        px.choropleth: Plotly express choropleth figure
    """
    if scope == "counties":
        plotdata = counties_df
        loc = 'fcode'
        range_c = (min(plotdata['avg_income']), 150000)
        loc_mode = None

    else:
        plotdata = states_df
        loc = 'state'
        range_c = None
        loc_mode = "USA-states"

    plotdata["avg_income"] = plotdata["avg_income"]\
        .apply(lambda x: round(x, 0))

    fig = px.choropleth(plotdata,
                        geojson=counties,
                        locations=loc,
                        color='avg_income',
                        color_continuous_scale="Turbo",
                        scope="usa",
                        locationmode=loc_mode,
                        range_color=range_c,
                        title="Average Income",
                        hover_data=["state"],
                        height=700)
    fig.update_layout(margin={"r": 0, "l": 0, "b": 0})

    if show_clusters == 1:
        scat = px.scatter_geo(cluster_df,
                              lat=cluster_df.lat,
                              lon=cluster_df.lon,
                              color='avg_income',
                              color_continuous_scale="Turbo",
                              size="size",
                              hover_name="clustername",
                              hover_data={"avg_income": True, "size": False,
                                          "lat": False, "lon": False},
                              scope="usa",
                              locationmode="USA-states",
                              range_color=[plotdata['avg_income'].min(),
                                           plotdata['avg_income'].max()]
                              )

        scat.update_layout(
            title='Average Income for Clusters',
            geo_scope='usa',
        )

        fig.add_trace(scat.data[0])

    return fig


@app.callback(
    Output(component_id='population-age-dist', component_property='figure'),
    [Input(component_id='county-or-state-age', component_property='value'),
     Input(component_id='show-clusters-age', component_property='value'),
     Input(component_id='age-ranges', component_property='value')]
)
def display_ages_range(scope, show_clusters, agerange):
    """Draw values for ages per county/state.

    Args:
        scope (str): Scope for age range
        agerange (list): Age range to display

    Returns:
        px.choropleth: Plotly express choropleth figure
    """

    if scope == "counties":
        plotdata = counties_ages_df
        loc = 'fcode'
        loc_mode = None

    else:
        plotdata = states_ages_df
        loc = 'state'
        loc_mode = "USA-states"

    filtered_df = plotdata[plotdata['age_range'].isin(agerange)]\
        .groupby([loc], as_index=False)\
        .agg({'state': 'first', 'percentage': 'sum', 'avg_income': 'mean'})

    filtered_df["avg_income"] = filtered_df["avg_income"]\
        .apply(lambda x: round(x, 0))
    filtered_df["percentage"] = filtered_df["percentage"]\
        .apply(lambda x: round(x, 4))

    fig = px.choropleth(filtered_df,
                        geojson=counties,
                        locations=loc,
                        color='percentage',
                        color_continuous_scale="Turbo",
                        scope="usa",
                        locationmode=loc_mode,
                        title="Percentage Age Range",
                        hover_data=["state", "avg_income"],
                        height=700)
    fig.update_layout(margin={"r": 0, "l": 0, "b": 0})

    if show_clusters == 1:
        cluster_plot_df = cluster_ages_df[cluster_ages_df['clusterid']
                                          .isin([1, 2, 5, 6, 7, 9, 10])].copy()
        cluster_plot_df['size'] = 600000

        cluster_plot_df = cluster_plot_df[cluster_plot_df['age_range']
                                          .isin(agerange)]\
            .groupby(['clusterid'], as_index=False)\
            .agg({'percentage': 'sum', 'avg_income': 'first',
                  'clustername': 'first',
                  'lat': 'first', 'lon': 'first', 'size': 'first'})

        cluster_plot_df["avg_income"] = cluster_plot_df["avg_income"]\
            .apply(lambda x: round(x, 0))
        cluster_plot_df["percentage"] = cluster_plot_df["percentage"]\
            .apply(lambda x: round(x, 4))

        scat = px.scatter_geo(cluster_plot_df,
                              lat=cluster_plot_df.lat,
                              lon=cluster_plot_df.lon,
                              color='percentage',
                              color_continuous_scale="Turbo",
                              size="size",
                              hover_name="clustername",
                              hover_data={"avg_income": True,
                                          "percentage": True, "size": False,
                                          "lat": False, "lon": False},
                              scope="usa",
                              locationmode="USA-states",
                              range_color=[plotdata['percentage'].min(),
                                           plotdata['percentage'].max()]
                              )

        scat.update_layout(
            title='Percentage',
            geo_scope='usa',
        )

        fig.add_trace(scat.data[0])

    return fig
