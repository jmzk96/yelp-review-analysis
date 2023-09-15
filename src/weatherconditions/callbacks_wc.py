"""Callbacks for the weathercondition view. Needs to be imported in index.py"""

from dash.dependencies import Input, Output  # type: ignore
import plotly.express as px  # type: ignore
from src.database_handler import DatabaseExecutor
from app import app


db_exec = DatabaseExecutor()


@app.callback(
    Output(component_id='extreme-cat-stars', component_property='figure'),
    [Input(component_id='extreme-cat-select', component_property='value')]
)
def display_dow_cat_plot(cat):
    """Return barplots faceted by clustername, grouped by stars and condition.
    Rerenders every time the category is changed.

    Args:
        cat (str): Name of the category

    Returns:
        px.bar: Plotly express Bar Figure
    """
    extreme_data = db_exec.get_extreme_weather_condition_stars(cat)

    fig = px.bar(
        extreme_data,
        x="star",
        y="rel_occurrence",
        color="condition",
        hover_data=["starcount"],
        hover_name="condition",
        facet_col='clustername',
        facet_col_wrap=3,
        facet_row_spacing=0.03,
        height=1500,
        text="rel_occurrence",
        barmode="group",
        title=f"Distribution for {cat} Grouped by Cluster and Condition",
        labels={
            "star": "Review Star value",
            "rel_occurrence": "Fraction of cluster reviews",
        }
    )
    fig.update_xaxes(showticklabels=True)
    fig.update_yaxes(showticklabels=True)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    return fig
