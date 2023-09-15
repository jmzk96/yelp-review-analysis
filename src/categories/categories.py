
"""View for opentimes route. Use layout in index.py"""

import dash_core_components as dcc  # type: ignore
import dash_html_components as html  # type: ignore

from src.helper.reusable_components import (
    generate_dropdow_all_categories
)


# Use reusable components when some comment elements are used in multiple files
# just take care not to have the same identifier

cats_dropdown1 = generate_dropdow_all_categories('cats-select')
cats_dropdown2 = dcc.Dropdown(id='subcats-select')

layout = html.Div([
    html.H1('Competitive Analysis of a Specific Business',
            style={"textAlign": "center"}),

    html.Div([
        html.Div([
            html.Label([
                "Choose Category",
                cats_dropdown1,
            ]),
        ], className='six columns'),
        html.Div([
            html.Label([
                "Choose Subcategory",
                cats_dropdown2,
            ]),
        ], className='six columns'),
    ], className='row'),

    html.Div([
        html.Div([
            dcc.Graph(id='subcat-cluster-star', figure={})],
            className='twelve columns'),
        html.Div([
            dcc.Graph(id='subcat-cluster-freq', figure={})],
            className='twelve columns'),
        html.Div([
            dcc.Graph(id='subcat-location', figure={})],
            className='twelve columns'),
    ])
], className='row')
