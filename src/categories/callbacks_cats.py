from statistics import mean
from dash.exceptions import PreventUpdate  # type: ignore
from dash.dependencies import Input, Output  # type: ignore
import plotly.express as px  # type: ignore
from src.database_handler import DatabaseExecutor
from app import app

db_exec = DatabaseExecutor()


@app.callback(
    Output(component_id='subcats-select', component_property='options'),
    [Input(component_id='cats-select', component_property='value')]
)
def update_subcat(category):
    df_subcat = db_exec.get_subcat_from_cat(category)
    opt = [{'label': row['category'], 'value':row['category']} for _, row in df_subcat.iterrows()
           if category != row['category']]
    return opt


@app.callback(
    Output(component_id='subcat-cluster-star', component_property='figure'),
    Output(component_id='subcat-cluster-freq', component_property='figure'),
    Output(component_id='subcat-location', component_property='figure'),
    [Input(component_id='cats-select', component_property='value'),
     Input(component_id='subcats-select', component_property='value'), ]
)
def display_subcat_cluster(category, subcategory):
    if subcategory is None:
        raise PreventUpdate
    cluster_cats = db_exec.get_business_from_bothcat(category, subcategory)
    avg_stars = mean(cluster_cats.stars_mean)
    fig = px.bar(
        cluster_cats,
        x='clustername',
        y='stars_mean',
        text="stars_mean",
        title=f"Average Stars of {category} & {subcategory} | avg: {avg_stars:.2f}",
        labels={
            "stars_mean": "Average Stars",
        }
    )
    fig.add_hline(y=avg_stars, line_dash="dash", line_color="red", )

    fig1 = px.bar(
        cluster_cats,
        x='clustername',
        y='bid_count',
        text="bid_count",
        title=f"Number of {category} & {subcategory} in each Cluster",
        labels={
            "bid_count": "Total amount of business",
        }
    )

    loc_subcat = db_exec.get_location_from_bothcat(category, subcategory)
    fig2 = px.scatter_mapbox(
        loc_subcat,
        lat="lat",
        lon="lon",
        color="clustername",
        hover_name="name",
        hover_data=["revcount", "bid", "clusterid"],
        mapbox_style="open-street-map",
        zoom=4,
        height=700,
        size_max=20,
        title=f"Location {category}: {subcategory} in each Cluster"
    )
    fig2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return[fig, fig1, fig2]
