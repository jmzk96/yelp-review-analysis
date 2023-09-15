"""View for pop_cats route. Use layout in index.py"""

import dash_core_components as dcc  # type: ignore
import dash_html_components as html  # type: ignore

from src.helper.reusable_components import generate_checklist_cluster


# Use reusable components when some comment elements are used in multiple files
# just take care not to have the same identifier

cluster_checklist = generate_checklist_cluster('cluster-cats-select')

layout = html.Div([
    html.H1('Customer Analysis Regarding Age & Race',
            style={"textAlign": "center"}),

    html.Div([
        html.Div([
            html.Label([
                "Choose Cluster to Include",
                cluster_checklist,
            ])
        ], className='six columns'),
    ], className='row'),

    html.Div([
        html.Div([
            dcc.Graph(id='pop-race', figure={})],
            className='twelve columns'),
        html.Div([
            dcc.Graph(id='pop-age', figure={})],
            className='twelve columns'),
    ], className='row'),

], className='row')
