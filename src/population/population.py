"""View for population data. Use layout in index.py"""

import dash_core_components as dcc  # type: ignore
import dash_html_components as html  # type: ignore

# Radio Button
income_options = [
    {'label': 'View counties',
     'value': 'counties'},
    {'label': 'View states',
     'value': 'states'},
]

scope_radio1 = dcc.RadioItems(
    id='county-or-state-income',
    options=income_options,
    persistence=True, persistence_type='session',
    value='states',
    labelStyle={'display': 'inline-block'}
)

scope_radio2 = dcc.RadioItems(
    id='county-or-state-age',
    options=income_options,
    persistence=True, persistence_type='session',
    value='states',
    labelStyle={'display': 'inline-block'}
)

# Radio Button
cluster_options = [
    {'label': 'Yes',
     'value': 1},
    {'label': 'No',
     'value': 0},
]

cluster_radio1 = dcc.RadioItems(
    id='show-clusters-income',
    options=cluster_options,
    persistence=True, persistence_type='session',
    value=1,
    labelStyle={'display': 'inline-block'}
)

cluster_radio2 = dcc.RadioItems(
    id='show-clusters-age',
    options=cluster_options,
    persistence=True, persistence_type='session',
    value=1,
    labelStyle={'display': 'inline-block'}
)

# Checklist
age_options = [
    {'label': '0-4 years',
     'value': 'age_0_4'},
    {'label': '5-9 years',
     'value': 'age_5_9'},
    {'label': '10-14 years',
     'value': 'age_10_14'},
    {'label': '15-19 years',
     'value': 'age_15_19'},
    {'label': '20-24 years',
     'value': 'age_20_24'},
    {'label': '25-29 years',
     'value': 'age_25_29'},
    {'label': '30-34 years',
     'value': 'age_30_34'},
    {'label': '35-39 years',
     'value': 'age_35_39'},
    {'label': '40-44 years',
     'value': 'age_40_44'},
    {'label': '45-49 years',
     'value': 'age_45_49'},
    {'label': '50-54 years',
     'value': 'age_50_54'},
    {'label': '55-59 years',
     'value': 'age_55_59'},
    {'label': '60-64 years',
     'value': 'age_60_64'},
    {'label': '65-69 years',
     'value': 'age_65_69'},
    {'label': '70-74 years',
     'value': 'age_70_74'},
    {'label': '75-79 years',
     'value': 'age_75_79'},
    {'label': '80-84 years',
     'value': 'age_80_84'},
    {'label': '85+ years',
     'value': 'age_85+'},
]

age_checklist = dcc.Checklist(
    id='age-ranges',
    options=age_options,
    persistence=True, persistence_type='session',
    value=['age_30_34'],
    labelStyle={'display': 'inline-block'}
)

layout = html.Div([
    html.Div([
        html.H1('Information about Population',
                style={"textAlign": "center"}),
    ]),
    dcc.Tabs(
        children=[
            dcc.Tab(label='Average Income', children=[
                html.Div([
                    html.Div([
                        html.Label([
                            "Choose View",
                            scope_radio1,
                        ]),
                    ], className='four columns'),
                    html.Div([
                        html.Label([
                            "Show Clusters?",
                            cluster_radio1,
                        ]),
                    ], className='two columns'),
                ], className='row'),
                dcc.Graph(id='population-avg-income', figure={})
            ]),

            dcc.Tab(label='Age Ranges', children=[
                html.Div([
                    html.Div([
                        html.Label([
                            "Choose View",
                            scope_radio2,
                        ]),
                    ], className='two columns'),
                    html.Div([
                        html.Label([
                            "Show Clusters?",
                            cluster_radio2,
                        ]),
                    ], className='two columns'),
                    html.Div([
                        html.Label([
                            "Choose Age Ranges",
                            age_checklist,
                        ]),
                    ], className='eight columns'),
                ], className='row'),
                dcc.Graph(id='population-age-dist', figure={})
            ]),
        ])
])
