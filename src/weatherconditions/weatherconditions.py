"""View for weathercondition route. Use layout in index.py"""

import dash_core_components as dcc  # type: ignore
import dash_html_components as html  # type: ignore

from src.helper.reusable_components import generate_dropdow_all_categories

# Use reusable components when some comment elements are used in multiple files
# just take care not to have the same identifier
cat_dropdown = generate_dropdow_all_categories('extreme-cat-select')


layout = html.Div([
    html.H1('Information about Relation between Stars and Weather Conditions',
            style={"textAlign": "center"}),

    html.Div([
        html.Div([
            html.Label([
                "Choose Category",
                cat_dropdown,
            ]),
        ], className='three columns'),


    ], className='row'),

    dcc.Graph(id='extreme-cat-stars', figure={}),
])
