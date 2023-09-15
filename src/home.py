"""View for welcome screen. Use layout in index.py"""

import dash_html_components as html  # type: ignore


layout = html.Div([
    html.H1('Welcome to the Project of the Sync Info Module',
            style={"textAlign": "center"}),
    html.H3('Data explorer Dash App | Group 3',
            style={"textAlign": "center"}),
    html.P("App to have insight into business, weather and population data of 10 clusters in America and Canada."),
    html.P(
        "Compare between business categories, best opening times and specific locations for your commercial desires."
    ),
    html.Br(),
    html.Div([
        html.H5("Group Members:"),
        html.Li("Joschka Deters"),
        html.Li("Sara El-Beit Shawish"),
        html.Li("Melanie Hartmann"),
        html.Li("Jeremy Mah Zhee Kein"),
        html.Li("Thi Nhat Le Pham"),
        html.Li("Julian Ueberbach"),
        html.Li("Andre Wohnsland"),
    ], style={"textAlign": "left", "padding-left": "30%", "float": "left"}),
    html.Div([
        html.H5("Datasets used:"),
        html.Li("NOAA Weatherdata"),
        html.Li("Yelp Dataset"),
        html.Li("County Data USA"),
    ], style={"textAlign": "left", "padding-right": "30%", "float": "right"}),


], style={"textAlign": "center"})
