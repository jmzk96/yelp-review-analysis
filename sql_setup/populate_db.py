import os
import sys
from pathlib import Path
import re
import pandas as pd
import numpy as np

module_path = os.path.abspath(os.path.join('.'))
if module_path not in sys.path:
    sys.path.append(module_path)
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from src.database_handler import DatabaseHandler  # wrong-import-position: ignore
from src.utils import timer  # wrong-import-position: ignore

#############################################
# For station Files
#############################################
station_col_specs = [
    (0, 12),
    (12, 21),
    (21, 31),
    (31, 38),
    (38, 41),
    (41, 72),
    (72, 76),
    (76, 80),
    (80, 86)
]

station_names = [
    "ID",
    "LATITUDE",
    "LONGITUDE",
    "ELEVATION",
    "STATE",
    "NAME",
    "GSN FLAG",
    "HCN/CRN FLAG",
    "WMO ID"]

station_dtype = {
    "ID": str,
    "STATE": str,
    "NAME": str,
    "GSN FLAG": str,
    "HCN/CRN FLAG": str,
    "WMO ID": str
}
#############################################
# For Weather files
#############################################
data_header_names = [
    "ID",
    "YEAR",
    "MONTH",
    "ELEMENT"]

data_header_col_specs = [
    (0, 11),
    (11, 15),
    (15, 17),
    (17, 21)]

data_header_dtypes = {
    "ID": str,
    "YEAR": int,
    "MONTH": int,
    "ELEMENT": str}

# create nested list and expand to list
data_col_names = [[
    f"VALUE{i + 1}",
    f"MFLAG{i + 1}",
    f"QFLAG{i + 1}",
    f"SFLAG{i + 1}"]
    for i in range(31)]
data_col_names = sum(data_col_names, [])

data_replacement_col_names = [[
    ("VALUE", i + 1),
    ("MFLAG", i + 1),
    ("QFLAG", i + 1),
    ("SFLAG", i + 1)]
    for i in range(31)]
data_replacement_col_names = sum(data_replacement_col_names, [])
data_replacement_col_names = pd.MultiIndex.from_tuples(
    data_replacement_col_names,
    names=['VAR_TYPE', 'DAY'])

data_col_specs = [[
    (21 + i * 8, 26 + i * 8),
    (26 + i * 8, 27 + i * 8),
    (27 + i * 8, 28 + i * 8),
    (28 + i * 8, 29 + i * 8)]
    for i in range(31)]
data_col_specs = sum(data_col_specs, [])

data_col_dtypes = [{
    f"VALUE{i + 1}": int,
    f"MFLAG{i + 1}": str,
    f"QFLAG{i + 1}": str,
    f"SFLAG{i + 1}": str}
    for i in range(31)]
# unpacks each dict in the list to key value in the main dict
data_header_dtypes.update({k: v for d in data_col_dtypes for k, v in d.items()})

#############################################
# Helper to read in and format the .dly files
#############################################


def read_ghcn_data_file(filename="ACW00011604.dly",
                        variables=None, include_flags=False,
                        dropna='all'):
    """read in all data of a .dly file

    Args:
        filename (str, optional): Name or path of file. Defaults to "ACW00011604.dly".
        variables (list, optional): List of variables to include. For example ['TMIN', 'TMAX', 'TOBS']. Defaults to None.
        include_flags (bool, optional): Keep multiindex / Flags. Defaults to False.
        dropna (str, optional): How to use the dropna command. Defaults to 'all'.

    Returns:
        df: cleaned up Dataframe
    """
    df = pd.read_fwf(
        filename,
        colspecs=data_header_col_specs + data_col_specs,
        names=data_header_names + data_col_names,
        index_col=data_header_names,
        dtype=data_header_dtypes
    )

    # Drops all values not included in list
    if variables is not None:
        df = df[df.index.get_level_values('ELEMENT').isin(variables)]

    df.columns = data_replacement_col_names

    # drops every column exept the value (other ones are flag values, see readme of the data, often NaN anyway)
    if not include_flags:
        df = df.loc[:, ('VALUE', slice(None))]
        df.columns = df.columns.droplevel('VAR_TYPE')

    # to row by day, spread TMIN, TMAX, ... into columns
    df = df.stack(level='DAY').unstack(level='ELEMENT')

    # drop the NaN values (-9999 are also missing values in the data set)
    if dropna:
        df.replace(-9999.0, np.nan, inplace=True)
        df.replace(-9999, np.nan, inplace=True)
        df.dropna(how=dropna, inplace=True)

    # see https://pandas.pydata.org/docs/user_guide/timeseries.html also for more info
    # it's an int 64 repr you can quick forward on the side if you search "int64 based YYYYMMDD"
    df.index = pd.to_datetime(
        df.index.get_level_values('YEAR') * 10000 +
        df.index.get_level_values('MONTH') * 100 +
        df.index.get_level_values('DAY'),
        format='%Y%m%d')

    return df

#############################################
# Section for some helper functions for the class
#############################################


def df_from_json(json_file_path):
    df_json_file = pd.read_json(json_file_path, lines=True)
    return df_json_file


def read_and_clean_business():
    print("Starting to read business data to dataframe")
    df = df_from_json("yelp_academic_dataset_business.json")
    df.categories = df.categories.str.split(", ")
    return df


def read_and_clean_users(sliced_file):
    print(f"Starting to read user data to dataframe for {sliced_file}")
    df = df_from_json(sliced_file)
    df.elite = df.elite.str.split(",")
    df.friends = df.friends.str.split(", ")
    return df


def read_and_clean_reviews(sliced_file):
    print(f"Starting to read review data to dataframe for {sliced_file}")
    df = df_from_json(sliced_file)
    df.date = df.date.dt.strftime("%Y-%m-%d")
    return df


def read_and_clean_tips():
    print("Starting to read tip data to dataframe")
    df = df_from_json("yelp_academic_dataset_tip.json")
    df.date = df.date.dt.strftime('%Y-%m-%d')
    return df


def generate_day_feq(x):
    dates = x["date"]
    onlydates = []
    for entry in dates:
        dat, _ = entry.split(" ")
        onlydates.append(dat)
    ser = pd.Series(onlydates)
    return [[d, v] for (d, v) in ser.value_counts().iteritems()]


def read_and_clean_checkins():
    print("Starting to read checkin data to dataframe")
    df = df_from_json("yelp_academic_dataset_checkin.json")
    df.date = df.date.str.split(", ")
    df["date"] = df.apply(generate_day_feq, axis=1)
    return df

# For business


def generate_category_dict(category_column):
    allcats = []
    for val in category_column:
        if val is not None:
            allcats.extend(val)
    setcat = set(allcats)
    dictcat = {x: i + 1 for i, x in enumerate(setcat)}
    return dictcat


def generate_categories(dictcat: dict):
    return [(cid, cat) for cat, cid in dictcat.items()]


def generate_category_info(business_id: str, dictcat: dict, categories: list):
    datalist = []
    if categories is None:
        return datalist
    # in some cases there can be the same cat entered twice.
    for cat in list(set(categories)):
        datalist.append((business_id, dictcat[cat]))
    return datalist


def map_dow(day: str):
    mapping = {
        "Monday": 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6,
    }
    return mapping.get(day, None)


def generate_time_info(business_id: str, timedict: dict):
    datalist = []
    if timedict is None:
        return datalist
    for day, timestring in timedict.items():
        start, end = timestring.split("-")
        start_1, start_2 = start.split(":")
        start_1 = start_1.rjust(2, "0")
        start_2 = start_2.ljust(2, "0")
        end_1, end_2 = end.split(":")
        end_1 = end_1.rjust(2, "0")
        end_2 = end_2.ljust(2, "0")
        data = (business_id, map_dow(day), f"{start_1}:{start_2}", f"{end_1}:{end_2}")
        datalist.append(data)
    return datalist


def generate_attribute_list(dict_categories, bid):
    data_list = []
    important_key_names = [
        "BusinessParking",
        "RestaurantsTableService",
        "Open24Hours",
        "RestaurantsCounterService",
        "DriveThru",
        "HappyHour",
        "OutdoorSeating",
        "RestaurantsGoodForGroups",
        "RestaurantsReservations",
        "Caters",
    ]
    if dict_categories is None:
        return []
    for key, value in dict_categories.items():
        if key in important_key_names:
            if value is None or value == "None":
                continue
            if "True" in value:
                data_list.append((bid, key))
    return data_list

# for user


def count_compliments(data):
    columns_to_include = [
        "compliment_hot",
        "compliment_more",
        "compliment_profile",
        "compliment_cute",
        "compliment_list",
        "compliment_note",
        "compliment_plain",
        "compliment_cool",
        "compliment_funny",
        "compliment_writer",
        "compliment_photos",
    ]
    return data[columns_to_include].sum()


def count_evaluations(data):
    columns_to_include = [
        "useful",
        "funny",
        "cool",
    ]
    return data[columns_to_include].sum()


def count_friends(data):
    return len(data["friends"])


def count_elite_years(data):
    return len(data["elite"])


def get_yelping_start(data):
    full_ts = data["yelping_since"]
    day, _ = full_ts.split(" ")
    return day

# for reviews
# we can use count_evaluations here as well :)

# for checkins


def generate_checkin_data(data):
    list_of_dates = data["date"]
    if list_of_dates is None:
        return []
    business_id = data["business_id"]
    data_list = [(business_id, x[0], x[1]) for x in list_of_dates]
    return data_list

#############################################
# The big player here
#############################################


class DataPreparator():
    """Class to contain all the transforming and inserting code for the weather and yelp data to move from file to database
    """

    def __init__(self):
        self.__handler = DatabaseHandler()
        self.__querry = self.__handler.querry_database
        self.__insert_many = self.__handler.insert_many
        print("Ready to go!")

    @timer
    def insert_stations(self, filename="ghcnd-stations.txt"):
        """Loads in the file with the station data.
        Transform it to a unified table and insert it as one bulk to the database

        Args:
            filename (str, optional): Path or filename for station data. Defaults to "ghcnd-stations.txt".
        """
        print(f"Inserting stations from {filename}. Please be patient....")
        datalist = []
        sql = "INSERT INTO STATIONDATA(SID, LON, LAT, ELE, STATE, NAME) VALUES %s"
        df = pd.read_fwf(filename, station_col_specs, names=station_names, dtype=station_dtype)

        for _, row in df.iterrows():
            used_state = ""
            if pd.notna(row["STATE"]):
                used_state = row["STATE"]
            data = (
                row["ID"],
                row["LONGITUDE"],
                row["LATITUDE"],
                row["ELEVATION"],
                used_state,
                row["NAME"]
            )
            datalist.append(data)
        self.__insert_many(sql, datalist)

    @timer
    def insert_weather(self, folderpath="./ghcnd_hcn"):
        """Load in each weather .dly file, transform it and bulk insert the data into the database

        Args:
            folderpath (str, optional): Path to the folder of data. Defaults to ./ghcnd_hcn.
        """
        start_date = "2000-01-01"
        filefolder = folderpath
        if folderpath == "./ghcnd_hcn":
            try:
                dirpath = os.path.dirname(__file__)
                filefolder = os.path.join(dirpath, "ghcnd_hcn")
            except NameError:
                filefolder = "ghcnd_hcn"

        print(f"Extracting data from: {filefolder} to get weather data. This may take a while.")
        filelist = Path(filefolder).rglob('*.dly')
        selected_vars = ["TMIN", "TMAX", "TOBS", "PRCP", "SNOW", "SNWD"]
        error_files = []
        sql = "INSERT INTO WEATHER(SID, DATE, TMIN, TMAX, PERCEPTION, SNOW, SNOWDEPTH) VALUES %s"

        # iterate over each file in folder, generate datalist and finally make one big insert for each file to be time efficient
        for i, path in enumerate(filelist):
            try:
                str_path = str(path)
                find = re.search(r"(\w{11}).dly", str_path)
                station_id = find.group(1)
                print(f"Reading in {i+1}th file at: {str_path} | station: {station_id}")
                weather = read_ghcn_data_file(filename=str_path, variables=selected_vars)

                try:
                    weather.TMIN = weather.TMIN / 10
                    weather.TMAX = weather.TMAX / 10
                    weather.PRCP = weather.PRCP / 10
                except AttributeError:
                    print(f"Could not convert the TMIN/TMAX od PRCP of {station_id}")
                    continue

                weather.fillna(np.nan).replace([np.nan], [None])
                mask = (weather.index >= start_date)
                datalist = []

                for index, row in weather[mask].iterrows():
                    data = (
                        station_id,
                        index,
                        row["TMIN"],
                        row["TMAX"],
                        row["PRCP"],
                        row["SNOW"],
                        row["SNWD"]
                    )
                    datalist.append(data)
                self.__insert_many(sql, datalist)
            except KeyError:
                print(f"ERROR: There was an error getting one of the values at: {station_id}.")
                error_files.append(station_id)
        print("Done processing all files.")
        if len(error_files) > 0:
            print("Problem in following files:")
            print(error_files)

    @timer
    def insert_business(self):
        """Load in the default business.json yelp data and transform all relations to insert them into the according tables.
        The tables are: business, category, categories, hours (and maybe later also attribute[s])
        """
        df = read_and_clean_business()
        # generate all unique categories and sql data
        dictcat = generate_category_dict(df.categories)
        sql_cat = "INSERT INTO CATEGORIES(CID, CAT) VALUES %s"
        cat_data = generate_categories(dictcat)

        # generate all business data: business row, according hours and categories and now attributes as well
        sql_attributes = "INSERT INTO attribute(BID, ATTR) VALUES %s"
        attributes_data = []

        sql_business = "INSERT INTO BUSINESS(BID, CITY, STATE, PCODE, LON, LAT, STARS, REVCOUNT, NAME) VALUES %s"
        business_data = []

        sql_category_link = "INSERT INTO CATEGORY(BID, CID) VALUES %s"
        category_link_data = []

        sql_hour = "INSERT INTO HOURS(BID, DOW, OPEN, CLOSE) VALUES %s"
        hour_data = []

        print("Start preparing all business related data to insert to database ...")
        for _, row in df.iterrows():
            b_data = (
                row["business_id"],
                row["city"],
                row["state"],
                row["postal_code"],
                row["longitude"],
                row["latitude"],
                row["stars"],
                row["review_count"],
                row["name"]
            )
            business_data.append(b_data)
            category_link_data.extend(generate_category_info(row["business_id"], dictcat, row["categories"]))
            attributes_data.extend(generate_attribute_list(row["attributes"], row["business_id"]))
            hour_data.extend(generate_time_info(row["business_id"], row["hours"]))
        # first insert all businesses, then cats, then the links and the hour data
        print("Done preparing, starting inserts")
        print("Inserting all business data ...")
        self.__insert_many(sql_business, business_data)

        print("Inserting all category data ...")
        self.__insert_many(sql_cat, cat_data)

        print("Inserting all links betweeen categories and business data ...")
        self.__insert_many(sql_category_link, category_link_data)

        print("Inserting all hour data of business ...")
        self.__insert_many(sql_hour, hour_data)

        print("Insertting all attribute data of business ...")
        self.__insert_many(sql_attributes, attributes_data)

    @timer
    def insert_users(self):
        """Load in each previously chunked user file (use the slice_... shell script for it), extracts the needed data
        and then insert them into the database. Some list as well as evaluation and compliment data are condensed
        to one numerical value.
        """
        # The VM prob cant handle this big chunk eiter, so split this file as well
        filelist = Path('.').rglob('user_*')
        for user_file in filelist:
            str_path = str(user_file)
            df = read_and_clean_users(str_path)
            sql_user = "INSERT INTO USERS(UID, REVCOUNT, SINCE, FRIENDS, EVALCOUNT, FANS, ELITE, AVGSTARS, INTERACTION) VALUES %s"
            user_data = []

            print(f"Start preparing all user related data to insert to database from file {str_path} ...")
            for _, row in df.iterrows():
                data = (
                    row["user_id"],
                    row["review_count"],
                    get_yelping_start(row),
                    count_friends(row),
                    count_evaluations(row),
                    row["fans"],
                    count_elite_years(row),
                    row["average_stars"],
                    count_compliments(row),
                )
                user_data.append(data)
            print(f"Inserting all data of user from file {str_path} ...")
            self.__insert_many(sql_user, user_data)

    @timer
    def insert_reviews(self):
        """Load in each previously chunked review file (use the slice_... shell script for it), extracts the needed data
        and then insert them into the database. Condenses the evaluation to one numerical value.
        """
        # reviews are too big, so they got split in separate files ^-^
        filelist = Path('.').rglob('review_*')
        for review_file in filelist:
            str_path = str(review_file)
            df = read_and_clean_reviews(str_path)
            sql_reviews = "INSERT INTO REVIEWS(RID, UID, BID, STAR, DATE, INTERACTIONS, TEXT) VALUES %s"
            review_data = []

            print(f"Start preparing all review related data to insert to database from file {str_path} ...")
            for _, row in df.iterrows():
                data = (
                    row["review_id"],
                    row["user_id"],
                    row["business_id"],
                    row["stars"],
                    row["date"],
                    count_evaluations(row),
                    row["text"],
                )
                review_data.append(data)
            print(f"Inserting all data of reviews from file {str_path} ...")
            self.__insert_many(sql_reviews, review_data)

    @timer
    def insert_tips(self):
        """Insert all tips from the default yelp json for tips and insert as one batch to the database.
        """
        df = read_and_clean_tips()
        sql_tips = "INSERT INTO TIPS(TID, BID, UID, COMPLIMENTS, DATE, TEXT) VALUES %s"
        tips_data = []

        print("Start preparing all tips related data to insert to database ...")
        for index, row in df.iterrows():
            data = (
                index,
                row["business_id"],
                row["user_id"],
                row["compliment_count"],
                row["date"],
                row["text"],
            )
            tips_data.append(data)
        print("Inserting all data of tips ...")
        self.__insert_many(sql_tips, tips_data)

    @timer
    def insert_checkins(self):
        """ Aggregates the checkin data for each business by day and business to get the daily checkin count.
        Enters the data as one batch into the database.
        """
        df = read_and_clean_checkins()
        sql_checkins = "INSERT INTO CHECKINS(BID, DATE, AMOUNT) VALUES %s"
        checkins_data = []

        print("Start preparing all checkin related data to insert to database ...")
        for _, row in df.iterrows():
            checkins_data.extend(generate_checkin_data(row))
        print("Inserting all data of checkin ...")
        self.__insert_many(sql_checkins, checkins_data)


if __name__ == "__main__":
    data_prep = DataPreparator()
    data_prep.insert_stations()
    data_prep.insert_weather()
    data_prep.insert_business()
    data_prep.insert_users()
    data_prep.insert_reviews()
    data_prep.insert_tips()
    data_prep.insert_checkins()
