"""View for opentimes route. Use layout in index.py"""

import dash_core_components as dcc  # type: ignore
import dash_html_components as html  # type: ignore

from src.helper.reusable_components import (
    generate_radio_dow,
    generate_dropdow_all_categories,
    generate_checklist_cluster
)


# Use reusable components when some comment elements are used in multiple files
# just take care not to have the same identifier
# define the layout components
cat_dropdown = generate_dropdow_all_categories('cat-time-select')
day_radio = generate_radio_dow('day-time-select')
cluster_check = generate_checklist_cluster('cluster-time-select')


layout = html.Div([
    html.H1('Information about open Times / Length and Categories',
            style={"textAlign": "center"}),

    html.Div([
        html.Div([
            html.Label([
                "Choose Category",
                cat_dropdown,
            ]),
        ], className='three columns'),

        html.Div([
            html.Label([
                "Choose Day of Week",
                day_radio,
            ]),
        ], className='four columns'),

        html.Div([
            html.Label([
                "Choose Cluster to Include",
                cluster_check,
            ]),
        ], className='five columns'),

    ], className='row'),

    dcc.Graph(id='open-times-stars', figure={}),
    dcc.Graph(id='open-times-freq', figure={}),
    dcc.Graph(id='all-dow-stars', figure={}),
    dcc.Graph(id='all-dow-freq', figure={}),
])
