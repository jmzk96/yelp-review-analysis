"""Callbacks for the opentimes view. Needs to be imported in index.py"""

from dash.dependencies import Input, Output  # type: ignore
import plotly.express as px  # type: ignore
from src.database_handler import DatabaseExecutor
from app import app


db_exec = DatabaseExecutor()

df_race = db_exec.get_pop_race_cluster()
df_age = db_exec.get_pop_age_cluster()


@app.callback(
    Output(component_id='pop-race', component_property='figure'),
    Output(component_id='pop-age', component_property='figure'),
    [Input(component_id='cluster-cats-select', component_property='value')]
)
def display_pop_cats_plot(clusters):
    clusterpop = db_exec.get_pop_cluster(tuple(clusters))

    erg = df_race.merge(clusterpop, on='fcode', how='inner')
    race = erg.groupby(['clustername', 'race'])['fip_race_pop'].sum().reset_index()
    race['popcluster'] = race["fip_race_pop"].groupby(race['clustername']).transform('sum')
    race["all_cluster"] = "all_cluster"

    # 1.PLOT
    fig = px.treemap(
        race,
        path=["all_cluster", 'clustername', 'race'],
        values='fip_race_pop',
        title="Population Race in each Cluster",
        labels={
            "fip_race_pop": "Total Population",
            "label": "Category",
        },
    )
    fig.update_layout(margin={"r": 0, "l": 0, "b": 0})
    fig.data[0].hovertemplate = 'Category: %{label}<br>Total Population: %{value:,.0f}'

    erg1 = df_age.merge(clusterpop, on='fcode', how='inner')
    age = erg1.groupby(['clustername', 'new_age_range'])['fip_age_pop'].sum().reset_index()
    age['popcluster'] = age["fip_age_pop"].groupby(age['clustername']).transform('sum')
    age["all_cluster"] = "all_cluster"

    # 2.PLOT
    fig1 = px.treemap(
        age,
        path=["all_cluster", 'clustername', 'new_age_range'],
        values='fip_age_pop',
        title="Population Age in each Cluster",
        labels={
            "fip_age_pop": "Total Population",
            "label": "Category",
        },
    )
    fig1.update_layout(margin={"r": 0, "l": 0, "b": 0})
    fig1.data[0].hovertemplate = 'Category: %{label}<br>Total Population: %{value:,.0f}'

    return [fig, fig1]
