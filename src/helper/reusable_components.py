"""Module to contain all dash core component logic of elements which will be either used at multiple places
or are quite complex to take a lot of lines of code to leave within the view"""

import calendar
import dash_core_components as dcc  # type: ignore
from src.database_handler import DatabaseExecutor

db_exec = DatabaseExecutor()
cat_data = db_exec.get_category_data_ordered_count()
cluster_data = db_exec.get_cluster_name_id()


def generate_radio_dow(identifier: str) -> dcc.RadioItems:
    """Creates a Radio Button view of all day of the weeks.
    Display label is the name, value is dow (0-6)

    Args:
        identifier (str): unique identifier for the object

    Returns:
        dcc.RadioItems: Dash Core Component Radio Item
    """
    item = dcc.RadioItems(
        id=identifier,
        options=[
            {'label': f'{calendar.day_name[i]}',
             'value': i}
            for i in range(7)
        ],
        persistence=True, persistence_type='session',
        value=0,
        labelStyle={'display': 'inline-block'}
    )
    return item


def generate_dropdow_all_categories(identifier: str) -> dcc.Dropdown:
    """Generate a Dropdown with all categories
    Display label is category combined with the count, value is the category name

    Args:
        identifier (str): unique identifier for the object

    Returns:
        dcc.Dropdown: Dash Core Component Dropdown
    """
    item = dcc.Dropdown(
        id=identifier,
        options=[
            {'label': row["display"], 'value': row["category"]}
            for _, row in cat_data.iterrows()
        ],
        persistence=True, persistence_type='session',
        clearable=False,
        value='Restaurants'
    )
    return item


def generate_checklist_cluster(identifier: str) -> dcc.Checklist:
    """Creates a multiselect checklist of all cluster names
    Display label is the clustername, value is the clusterid

    Args:
        identifier (str): unique identifier for the object

    Returns:
        dcc.Checklist: Dash Core Component Checklist
    """
    item = dcc.Checklist(
        id=identifier,
        options=[
            {'label': row["clustername"], 'value': row["clusterid"]}
            for _, row in cluster_data.iterrows()
        ],
        persistence=True, persistence_type='session',
        value=[row["clusterid"] for _, row in cluster_data.iterrows()],
        labelStyle={'display': 'inline-block'}
    )
    return item
