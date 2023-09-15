"""Script to create all materialized views for categories filtered by condition, stars, location"""

import os
import sys
import re

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
module_path = os.path.abspath(os.path.join('.'))
if module_path not in sys.path:
    sys.path.append(module_path)
from src.database_handler import DatabaseHandler, DatabaseExecutor  # wrong-import-position: ignore
from src.utils import timer  # wrong-import-position: ignore


def create_view(handler: DatabaseHandler, cat: str):
    """Creates a viel in matview.catname for the given category.
    Cleans the category of not valid chars, only leaving characters.

    Args:
        handler (DatabaseHandler): Initialized DatabaseHandler
        cat (str): Name of the category
    """
    # First generates the template to reuse later with bot (0,1) inputs
    base_sql = """select star, cl.clustername, count(*), '{0}' as cond from
                reviews inner join business as b
                on b.bid=reviews.bid
                inner join cluster_weather as cw
                on b.clusterid = cw.clusterid and cw.date = reviews.date
                inner join cluster as cl on  b.clusterid = cl.clusterid
                where {1} and b.bid in (select bid from category
                where cid = (select cid from categories where cat = %(category)s))
                group by star, cl.clustername"""

    # now puts the input into the template and combines to one sql
    sql1 = base_sql.format("< 0 °C", "cw.tmin<0")
    sql2 = base_sql.format("> 30 °C", "cw.tmax>30")
    sql3 = base_sql.format("No Rain", "cw.perception=0")
    combined_sql = f"{sql1} union {sql2} union {sql3}"

    # removes invalid chars from category name, create view
    cleaned_cat = re.sub('[^a-zA-Z]', '', cat)
    final_sql = f"create materialized view matview.{cleaned_cat} as {combined_sql}"
    opt = {"category": cat}

    handler.querry_database(final_sql, opt)


@timer
def create_all_views():
    """Creates all materialized views of the categories.
    """
    print("Starting to create all materialized views for cat - weather aggregation")
    print("The name format of the views will be matview.categoryname")
    print("The categoryname will be stripped of all characters other than [a-zA-Z]")
    db_handler = DatabaseHandler()
    db_exec = DatabaseExecutor()
    cat_df = db_exec.get_category_data_ordered_count()

    # only creates if not exists
    try:
        db_handler.querry_database("create schema matview;")
        print("Schema matview was created")
    except Exception as exep:  # pylint: disable=broad-except
        print(f"Schema matview already exists: {exep}")

    for _, row in cat_df.iterrows():
        print(f"Creating view for category: {row['category']} |\t", end=' ')
        create_view(db_handler, row["category"])
    print("Done creating all views")


if __name__ == "__main__":
    create_all_views()
