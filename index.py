import dash  # type: ignore # pylint: disable=unused-import
import dash_core_components as dcc  # type: ignore
import dash_html_components as html  # type: ignore
from dash.dependencies import Input, Output  # type: ignore

# if you seperate your callbacks to own file, you need to import it here !!!!!
from src.opentimes import opentimes, callbacks_ot  # pylint: disable=unused-import
from src.weatherconditions import weatherconditions, callbacks_wc  # pylint: disable=unused-import
from src.population import population, callbacks_po  # pylint: disable=unused-import
from src.pop_cats import pop_cats, callbacks_popcats  # pylint: disable=unused-import
from src.categories import categories, callbacks_cats  # pylint: disable=unused-import
from src import weatherstation
from src import home
from app import app
from app import server  # pylint: disable=unused-import


# Connect to your app pages
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('Weatherstation', href='/apps/weatherstation'),
        "  |  ",
        dcc.Link('Open Times', href='/apps/opentimes'),
        "  |  ",
        dcc.Link('Weather Conditions', href='/apps/weatherconditions'),
        "  |  ",
        dcc.Link('Population Data', href='/apps/population'),
        "  |  ",
        dcc.Link('Population Analysis', href='/apps/pop_cats'),
        "  |  ",
        dcc.Link('Categories', href='/apps/categories'),
    ], className="row"),
    html.Div(id='page-content', children=[])
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    """Routes the path to the according page layout

    Args:
        pathname (str): name of the path

    Returns:
        dcc Layout: Layout of dash core / html elements
    """
    if pathname == '/apps/weatherstation':
        return weatherstation.layout
    if pathname == '/apps/opentimes':
        return opentimes.layout
    if pathname == '/apps/weatherconditions':
        return weatherconditions.layout
    if pathname == '/apps/population':
        return population.layout
    if pathname == '/apps/pop_cats':
        return pop_cats.layout
    if pathname == '/apps/categories':
        return categories.layout
    return home.layout


if __name__ == '__main__':
    # app.run_server(debug=True)
    print("access the server on http://127.0.0.1:8050/ http://127.0.0.1 or your defined address")
    app.run_server(host="0.0.0.0", debug=True, port=8050)
