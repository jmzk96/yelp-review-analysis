"""Callbacks for the opentimes view. Needs to be imported in index.py"""

import calendar
from dash.dependencies import Input, Output  # type: ignore
import plotly.express as px  # type: ignore
from src.database_handler import DatabaseExecutor
from app import app


db_exec = DatabaseExecutor()


@app.callback(
    Output(component_id='open-times-stars', component_property='figure'),
    Output(component_id='open-times-freq', component_property='figure'),
    [Input(component_id='day-time-select', component_property='value'),
     Input(component_id='cat-time-select', component_property='value'),
     Input(component_id='cluster-time-select', component_property='value')]
)
def display_dow_cat_plot(dow, cat, clusters):
    """Changes the plots for the specific dow.
    Changes every time on of the inputs changes.

    Args:
        dow (int): Number for dow (1-6)
        cat (str): Name of the category
        clusters (list): List of cluster ids

    Returns:
        list: List of both plots
    """
    time_data = db_exec.get_aggregated_open_info(dow, cat, tuple(clusters))
    avg_stars = db_exec.get_avg_stars_cat(dow, cat, tuple(clusters))
    day = calendar.day_name[dow]
    total_sum = sum(time_data['business_count'])
    # Leave this code there, maybe its better in the future to aggregate over pandas to have more options
    # time_data.loc[time_data["open_span"] == 0, "open_span"] = 24
    # open_len_avgstars = time_data.groupby('open_span')['stars'].mean().reset_index(name='avgstars')
    # open_len_avgstars["avgstars"] = round(open_len_avgstars["avgstars"], 2)
    # open_freq = time_data.groupby('open_span').size().reset_index(name='freq')

    # First Barplot
    fig = px.bar(
        time_data,
        x="open_span",
        y="avgstars",
        height=500,
        text="avgstars",
        title=f"Average Stars of {cat} at {day} for all open lengths | avg: {avg_stars:.2f}",
        labels={
            "open_span": "Opening time span in hours",
            "avgstars": "Average Stars",
        }
    )
    fig.add_hline(
        y=avg_stars,
        line_dash="dash",
        line_color="red",
        # annotation_text="avg_all(stars)",
        # annotation_position="top left",
        # annotation_font_size=18,
        # annotation_font_color="red"
    )
    fig.update_xaxes(tickvals=list(range(1, 25)))

    # second Barplot
    fig2 = px.bar(
        time_data,
        x="open_span",
        y="business_count",
        height=500,
        text="business_count",
        log_y=True,
        title=f"Count of {cat} at {day} for all open lengths | total sum: {total_sum}",
        labels={
            "open_span": "Opening time span in hours",
            "business_count": "Number of businesses (log scale)",
        }
    )
    # fig2.update_traces(texttemplate='%{text:.2s}', textposition='inside')
    fig2.update_xaxes(tickvals=list(range(1, 25)))

    return [fig, fig2]


@app.callback(
    Output(component_id='all-dow-stars', component_property='figure'),
    Output(component_id='all-dow-freq', component_property='figure'),
    [Input(component_id='cat-time-select', component_property='value'),
     Input(component_id='cluster-time-select', component_property='value')]
)
def display_dow_cat(cat, clusters):
    """Display the plots for the information of every dow.
    Changes every time cat or cluster is changed.

    Args:
        cat (str): Name of the category
        clusters (list): List of cluster ids

    Returns:
        list: List of both plots
    """
    time_data = db_exec.get_aggregated_open_info_with_dow_grouping(cat, tuple(clusters))
    time_data["dow"] = time_data["dow"].map(lambda x: calendar.day_name[x])
    fig = px.bar(
        time_data,
        x="open_span",
        y="avgstars",
        color="dow",
        barmode="group",
        height=600,
        text="avgstars",
        title=f"Average Stars of {cat} for all open lengths",
        labels={
            "open_span": "Opening time span in hours",
            "avgstars": "Average Stars",
        }
    )
    fig.update_xaxes(tickvals=list(range(1, 25)))

    fig2 = px.bar(
        time_data,
        x="open_span",
        y="business_count",
        color="dow",
        barmode="group",
        height=600,
        text="business_count",
        log_y=True,
        title=f"Count of of {cat} for all open lengths",
        labels={
            "open_span": "Opening time span in hours",
            "business_count": "Number of businesses (log scale)",
        }
    )
    fig2.update_xaxes(tickvals=list(range(1, 25)))

    return [fig, fig2]
