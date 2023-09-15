"""Module to keep the main logic to interact with the specific database framework.
Also contains the Handler, where all the querries are stored.
Usually the querries should return Dataframes.
Some Exceptions may occour, when there is either a single value or a list of only one value each."""

import os
import re
from typing import Dict, List, Tuple
from dotenv import load_dotenv
import pandas as pd  # type: ignore
import psycopg2  # type: ignore
from psycopg2.extras import execute_values  # type: ignore
from src.utils import timer

load_dotenv()

dbname = os.getenv("DATABASE_NAME")
user = os.getenv("DATABASE_USER")
password = os.getenv("DATABASE_PASSWORD")
host = os.getenv("DATABASE_HOST")
port = os.getenv("DATABASE_PORT")

DEC2FLOAT = psycopg2.extensions.new_type(
    psycopg2.extensions.DECIMAL.values,
    'DEC2FLOAT',
    lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)


class DatabaseExecutor():
    """Class to interact with the database.
    Returns either arrays or objects converted from the database data
    """

    def __init__(self):
        self.__handler = DatabaseHandler()
        self.__querry = self.__handler.querry_database

    def get_weatherstation_data_where_hcn(self) -> pd.DataFrame:
        sql = """select lat, lon, name, a.sid, days
                from stationdata as a inner join
                (select sid, count(*) as days from weather
                where date >= '2004-01-01' group by sid) as b
                on a.sid = b.sid"""
        data = self.__querry(sql)
        cols = ["lat", "lon", "name", "sid", "days"]
        return pd.DataFrame(data, columns=cols)

    def get_weatherstation_data(self) -> pd.DataFrame:
        sql = """select lat, lon, name, sid
                from stationdata"""
        data = self.__querry(sql)
        cols = ["lat", "lon", "name", "sid"]
        return pd.DataFrame(data, columns=cols)

    def get_open_info(self, dow: int, cat: str) -> pd.DataFrame:
        sql = """SELECT stars, h.open, h.close, h.open_span
                FROM hours h
                INNER JOIN business b
                    ON h.bid = b.bid
                INNER JOIN category cat
                    ON b.bid = cat.bid
                INNER JOIN categories cats
                    ON cat.cid = cats.cid
                WHERE h.dow = %(dow)s AND cats.cat = %(category)s"""
        opt = {"dow": dow, "category": cat}
        data = self.__querry(sql, opt)
        cols = ["stars", "open_time", "close_time", "open_span"]
        return pd.DataFrame(data, columns=cols)

    def get_aggregated_open_info(self, dow: int, cat: str, clusters: Tuple) -> pd.DataFrame:
        sql = """SELECT h.open_span, count(*) as business_count, round(avg(stars),2) as avgstars
                FROM hours h
                INNER JOIN business b
                    ON h.bid = b.bid
                INNER JOIN category cat
                    ON b.bid = cat.bid
                INNER JOIN categories cats
                    ON cat.cid = cats.cid
                WHERE h.dow = %(dow)s AND cats.cat = %(category)s AND b.clusterid in %(clusters)s
                GROUP BY h.open_span"""
        opt = {"dow": dow, "category": cat, "clusters": clusters}
        data = self.__querry(sql, opt)
        cols = ["open_span", "business_count", "avgstars"]
        return pd.DataFrame(data, columns=cols)

    def get_aggregated_open_info_with_dow_grouping(self, cat: str, clusters: Tuple) -> pd.DataFrame:
        sql = """SELECT h.dow, h.open_span, count(*) as business_count, round(avg(stars),2) as avgstars
                FROM hours h
                INNER JOIN business b
                    ON h.bid = b.bid
                INNER JOIN category cat
                    ON b.bid = cat.bid
                INNER JOIN categories cats
                    ON cat.cid = cats.cid
                WHERE cats.cat = %(category)s AND b.clusterid in %(clusters)s
                GROUP BY h.open_span, h.dow"""
        opt = {"category": cat, "clusters": clusters}
        data = self.__querry(sql, opt)
        cols = ["dow", "open_span", "business_count", "avgstars"]
        return pd.DataFrame(data, columns=cols)

    def get_avg_stars_cat(self, dow: int, cat: str, clusters: Tuple) -> int:
        sql = """SELECT round(avg(stars),2)
                FROM hours h
                INNER JOIN business b
                    ON h.bid = b.bid
                INNER JOIN category cat
                    ON b.bid = cat.bid
                INNER JOIN categories cats
                    ON cat.cid = cats.cid
                WHERE h.dow = %(dow)s AND cats.cat = %(category)s AND b.clusterid in %(clusters)s"""
        opt = {"dow": dow, "category": cat, "clusters": clusters}
        data = self.__querry(sql, opt)
        return data[0][0]

    def get_category_data_ordered_count(self) -> pd.DataFrame:
        sql = """SELECT cat.cid, cats.cat, cats.cat || ' (' || count(*) || 'x)' as display
                FROM category cat
                INNER JOIN categories cats
                    ON cat.cid = cats.cid
                group by cat.cid, cats.cat
                Order By count(*) desc"""
        data = self.__querry(sql)
        cols = ["cid", "category", "display"]
        return pd.DataFrame(data, columns=cols)

    def get_cluster_name_id(self) -> pd.DataFrame:
        sql = """select clusterid, clustername from cluster"""
        data = self.__querry(sql)
        cols = ["clusterid", "clustername"]
        return pd.DataFrame(data, columns=cols)

    @timer
    def get_extreme_weather_condition_stars(self, cat: str) -> pd.DataFrame:
        # the views does only contains chars, everything else is stripped!
        cleaned_cat = re.sub('[^a-zA-Z]', '', cat)
        sql = f"SELECT * FROM matview.{cleaned_cat} order by cond;"
        data = self.__querry(sql)
        cols = ["star", "clustername", "starcount", "condition"]

        # also gets the total count of each condition - cluster combination and normalizes the number to 1
        df = pd.DataFrame(data, columns=cols)
        df["rel_occurrence"] = 0
        sum_data = df.groupby(["condition", "clustername"])["starcount"].sum()
        for row in sum_data.iteritems():
            (cond, state), number = row
            my_filter = (df["condition"] == cond) & (df["clustername"] == state)
            df.loc[my_filter, "rel_occurrence"] = round(df.loc[my_filter, "starcount"] / number, 2)
        return df

    def get_avg_income_counties(self) -> pd.DataFrame:
        sql = """select fcode, avg_income, state
                from counties"""
        data = self.__querry(sql)
        cols = ["fcode", "avg_income", "state"]
        return pd.DataFrame(data, columns=cols)

    def get_avg_income_states(self) -> pd.DataFrame:
        sql = """select state, avg(avg_income) as avg_income
                from counties
                group by state"""
        data = self.__querry(sql)
        cols = ["state", "avg_income"]
        return pd.DataFrame(data, columns=cols)

    def get_avg_income_clusters(self) -> pd.DataFrame:
        sql = """select business.clusterid, cluster.clustername, cluster.lat,
                 cluster.lon, avg(counties.avg_income) as avg_income
                 from business
                 inner join fipzip on business.pcode = fipzip.pcode
                 inner join counties on counties.fcode = fipzip.fcode
                 inner join cluster on cluster.clusterid = business.clusterid
                 group by business.clusterid, cluster.clustername,
                 cluster.lat, cluster.lon"""
        data = self.__querry(sql)
        cols = ["clusterid", "clustername", "lat", "lon", "avg_income"]
        return pd.DataFrame(data, columns=cols)

    def get_ages_counties(self) -> pd.DataFrame:
        sql = """select counties.fcode, counties.state, counties.avg_income as avg_income,
                fip_population_age.age_range, fip_population_age.percentage
                from counties
                inner join fip_population_age
                on fip_population_age.fcode = counties.fcode"""
        data = self.__querry(sql)
        cols = ["fcode", "state", "avg_income", "age_range", "percentage"]
        return pd.DataFrame(data, columns=cols)

    def get_ages_states(self) -> pd.DataFrame:
        sql = """select counties.state, avg(counties.avg_income) as avg_income,
                fip_population_age.age_range, avg(fip_population_age.percentage) as percentage
                from counties
                inner join fip_population_age
                on fip_population_age.fcode = counties.fcode
                group by counties.state, fip_population_age.age_range"""
        data = self.__querry(sql)
        cols = ["state", "avg_income", "age_range", "percentage"]
        return pd.DataFrame(data, columns=cols)

    def get_ages_clusters(self) -> pd.DataFrame:
        sql = """select business.clusterid, cluster.clustername, cluster.lat,
                 cluster.lon, fip_population_age.age_range,
                 avg(fip_population_age.percentage) as percentage,
                 avg(counties.avg_income) as avg_income
                 from business
                 inner join fipzip on business.pcode = fipzip.pcode
                 inner join counties on counties.fcode = fipzip.fcode
                 inner join fip_population_age on fip_population_age.fcode = fipzip.fcode
                 inner join cluster ON cluster.clusterid = business.clusterid
                 group by business.clusterid, cluster.clustername, cluster.lat,
                 cluster.lon, fip_population_age.age_range"""
        data = self.__querry(sql)
        cols = ["clusterid", "clustername", "lat", "lon", "age_range",
                "percentage", "avg_income"]
        return pd.DataFrame(data, columns=cols)

# neu eingefügte def
    def get_pop_cluster(self, clusters: Tuple) -> pd.DataFrame:
        sql = """ SELECT b.stars, b.clusterid, c.clustername, b.bid, b.pcode,b.city,
                fipzip.fcode, popyear.population, popyear.year
                FROM business b
                INNER JOIN fipzip
                ON b.pcode = fipzip.pcode
                INNER JOIN fip_population_year popyear
                ON fipzip.fcode = popyear.fcode
                INNER JOIN cluster c
                ON c.clusterid = b.clusterid
                WHERE popyear.year = 2019 AND b.clusterid in %(clusters)s
                """

        opt = {"clusters": clusters}
        clusterpop = self.__querry(sql, opt)
        cols = ["stars", "clusterid", "clustername", "bid", "pcode", "city", "fcode", "population", "year"]
        clusterpop = pd.DataFrame(clusterpop, columns=cols)
        clusterpop.drop_duplicates(subset=['fcode'], keep='first')
        return clusterpop

    def get_pop_race_cluster(self) -> pd.DataFrame:
        sql = """ SELECT poprace.fcode, poprace.race, poprace.percentage, popyear.population
                FROM fip_population_race poprace
                INNER JOIN fip_population_year popyear
                ON poprace.fcode = popyear.fcode
                WHERE popyear.year =2019"""

        df_race = self.__querry(sql)
        cols = ["fcode", "race", "percentage", "population"]
        df_race = pd.DataFrame(df_race, columns=cols)
        df_race['fip_race_pop'] = round(df_race.percentage * df_race.population)
        df_race = df_race.astype({'fip_race_pop': int})
        df_race = df_race.rename(columns={'population': 'fip_pop'})
        return df_race

    def get_pop_age_cluster(self) -> pd.DataFrame:
        sql = """ SELECT popage.fcode, popage.age_range, popage.percentage, popyear.population
                FROM fip_population_age popage
                INNER JOIN fip_population_year popyear
                ON popage.fcode = popyear.fcode
                WHERE popyear.year = 2019"""

        df_age = self.__querry(sql)
        cols = ["fcode", "age_range", "percentage", "population"]
        df_age = pd.DataFrame(df_age, columns=cols)
        df_age['new_age_range'] = df_age['age_range'].apply(generate_age_groups)
        df_age['fip_age_pop'] = round(df_age.percentage * df_age.population)
        df_age = df_age.astype({'fip_age_pop': int})
        df_age = df_age.rename(columns={'population': 'fip_pop'})
        return df_age

    def get_subcat_from_cat(self, category) -> pd.DataFrame:
        sql = """ SELECT * from categories WHERE cid in (
                    SELECT distinct cid from category WHERE bid in
                    (SELECT bid from category WHERE cid  = (
                    SELECT cid FROM categories WHERE cat= %(category)s))
                    )"""
        opt = {"category": category}
        df_subcat = self.__querry(sql, opt)
        cols = ["cid", "category"]
        return pd.DataFrame(df_subcat, columns=cols)

    def get_business_from_bothcat(self, category, subcategory) -> pd.DataFrame:
        sub_sql = """Select bid from
                    (SELECT bid, count(*) as amount from category
                    where cid in(
                    select cid from categories
                    where cat in (%(category)s,%(subcategory)s))
                    group by bid
                    order by count(*) desc) as pre
                    where amount >= 2"""
        sql = f"""SELECT cats.cat, b.stars, b.clusterid, cluster.clustername, b.bid, b.pcode, b.city
                    FROM categories cats
                    INNER JOIN category cat
                        ON cats.cid = cat.cid
                    INNER JOIN business b
                        ON b.bid = cat.bid
                    INNER JOIN  ({sub_sql}) as pre
                        ON b.bid = pre.bid
                    INNER JOIN cluster
                        ON b.clusterid = cluster.clusterid"""

        opt = {"category": category, "subcategory": subcategory}
        cat_subcat = self.__querry(sql, opt)
        cols = ["cat", "stars", "clusterid", "clustername", "bid", "pcode", "city"]
        cat_subcat = pd.DataFrame(cat_subcat, columns=cols)
        cat_subcat = cat_subcat.drop_duplicates(subset="bid", keep="first")

        cluster_cats = cat_subcat.groupby('clustername').agg({'stars': ['mean', 'max', 'min'], 'bid': ['count']})
        cluster_cats.columns = ['_'.join(col) for col in cluster_cats.columns.values]
        cluster_cats = cluster_cats.reset_index()
        cluster_cats.stars_mean = round(cluster_cats.stars_mean, 2)
        return cluster_cats

    def get_location_from_bothcat(self, category, subcategory) -> pd.DataFrame:
        sub_sql = """Select bid from
                        (SELECT bid, count(*) as amount from category
                         where cid in(
                         select cid from categories
                         where cat in (%(category)s,%(subcategory)s))
                         group by bid
                         order by count(*) desc) as pre
                            where amount >= 2"""

        sub_sql1 = f"""SELECT cats.cat, b.stars, b.clusterid, b.bid, b.pcode,b.city
                        FROM categories cats
                        INNER JOIN category cat
                            ON cats.cid = cat.cid
                        INNER JOIN business b
                            ON b.bid = cat.bid
                        INNER JOIN  ({sub_sql}) as pre
                            ON b.bid = pre.bid"""

        sql = f"""Select  business.lon, business.lat, business.stars, business.revcount,
                business.name, business.bid, business.clusterid, cluster.clustername
                from business
                inner join  ({sub_sql1}) as pre
                ON business.bid = pre.bid
                INNER JOIN cluster
                ON business.clusterid = cluster.clusterid"""

        opt = {"category": category, "subcategory": subcategory}
        loc_subcat = self.__querry(sql, opt)
        cols = ["lon", "lat", "stars", "revcount", "name", "bid", "clusterid", "clustername"]
        loc_subcat = pd.DataFrame(loc_subcat, columns=cols)
        loc_subcat = loc_subcat.drop_duplicates(subset='bid', keep='first')
        return loc_subcat


def generate_age_groups(x):
    age_mapping = {
        "age 0-4": ["age_0_4"],
        "age 5-9": ["age_5_9"],
        "age 10-14": ["age_10_14"],
        "age 15-19": ["age_15_19"],
        "age 20-29": ["age_20_24", "age_25_29"],
        "age 30-49": ["age_30_34", "age_35_39", "age_40_44", "age_45_49"],
        "age 50-64": ["age_50_54", "age_55_59", "age_60_64"],
        "age 65+": ["age_65_69", "age_70_74", "age_75_79", "age_80_84", "age_85+"],
    }
    for age_tag, age_groups in age_mapping.items():
        if x in age_groups:
            return age_tag
    return "unknown"


class DatabaseHandler:
    """Handler Class for Connecting and querring Databases"""

    def __init__(self):
        self.__con: psycopg2.extensions.connection = None
        self.connect_database()
        self.tmp_cursor: psycopg2.extensions.cursor = None

    def connect_database(self):
        """Try to generate a connection to the database"""
        try:
            self.__con = psycopg2.connect(database=dbname, user=user, password=password, host=host, port=port)
        except Exception as ex:  # pylint: disable=broad-except
            # Better raise an error here and stop application ? its useless going on without a DB
            print(f"Error: {ex}")

    def close_database(self):
        """Closes the connection to the database"""
        if self.__con:
            self.__con.close()
            self.__con = None

    @timer
    def querry_database(self, sql: str, options: Dict = None) -> List:
        """Executes the querry and returns the value as a list if there is a return value

        Args:
            sql (str): SQL Querry to execute
            options (Dict, optional): Arguments for the querry in psycopg style as dict. Defaults to None.

        Returns:
            List: Empty or filled list with the result tuples from the database
        """
        result = []
        with self.__con:
            with self.__con.cursor() as cur:
                cur.execute(sql, options)
                try:
                    result = cur.fetchall()
                except psycopg2.ProgrammingError:
                    pass
        return result

    @timer
    def pandas_querry(self, sql: str) -> pd.DataFrame:
        """Uses the pandas read_sql command to return a dataframe from the sql command.
        Can only be used with plain sql strings, not with psycopg2 variable placeholder.

        Args:
            sql (str): SQL Querry to execute

        Returns:
            pd.DataFrame: Pandas Dataframe with the view data
        """
        return pd.read_sql(sql, self.__con)

    @timer
    def insert_many(self, sql: str, values: List, template: str = None) -> None:
        """Executes the SQL Querry to insert many (all values) from the given list

        Args:
            sql (str): SQL Querry as String
            values (List): List of each tuple to enter into the database
        """
        with self.__con:
            with self.__con.cursor() as cur:
                execute_values(cur, sql, values, template)

    # CAREFULL, THIS CODE SEEMS TO LOCK THE DATABASE, RESULTING IN STRANGE BEHAVIOUR
    # IF NOT NECCECARY BETTER USE A QUERRY WITH LIMIT AND OFFSET COMBINATION!!!

    @timer
    def init_fetch_many_cursor(self, sql: str, options: Dict = None) -> None:
        """Sets up a temporary cursor to use the fetch cursor batch on after
        Also limits the itersize of the cursor to 100k to save RAM (RIP VM otherwise ...).
        EXPERIMENTAL, USE AT OWN RISK!!

        Args:
            sql (str): SQL Querry to execute
            options (Dict, optional): Arguments for the querry in psycopg style as dict. Defaults to None.
        """
        self.tmp_cursor = self.__con.cursor()
        self.tmp_cursor.itersize = 100000
        self.tmp_cursor.execute(sql, options)

    def fetch_cursor_batch(self, batch_size: int = 100000) -> List:
        """Executes the initialiezed cursor with a fetchmany at the given size.
        Returns empty array if no more data is left / no cursor initialized.
        Also closes the cursor if no more data is available.
        EXPERIMENTAL, USE AT OWN RISK!!

        Args:
            batch_size (int, optional): Rows to fetch at once. Defaults to 100000.

        Returns:
            List: List with the result tuples
        """
        if self.tmp_cursor is None:
            return []
        data = self.tmp_cursor.fetchmany(batch_size)
        if len(data) == 0:
            self.tmp_cursor.close()
            self.tmp_cursor = None
        return data
