import psycopg2
from psycopg2.extras import execute_values
from psycopg2.errors import DatabaseError,DataError,IntegrityError
import pandas as pd
import os
import sys

module_path = os.path.abspath(os.path.join('.'))
if module_path not in sys.path:
    sys.path.append(module_path)
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)


class FacilitiesCountiesPopulator():

    def __init__(self):
        self.conn = psycopg2.connect(user="sync3", host="141.100.70.97", dbname="sync3", password="sync3")

    def load_data_counties(self):
        df = pd.read_csv("counties.csv",dtype={"fcode":str})
        list_of_tup = []
        for index, row in df.iterrows():
            list_of_tup.append((
                row["fcode"],
                row["state"],
                row["county"],
                row["land_area"],
                row["area"],
                row["longitude"],
                row["latitude"],
                row["avg_income"]
            ))
        sql = """INSERT INTO counties (fcode ,state, county, land_area, area, lon,lat, avg_income) VALUES %s """
        try:
            print("Loading Data into Database...")
            with self.conn:
                with self.conn.cursor() as cur:
                    execute_values(cur, sql=sql, argslist=list_of_tup)
            print("Data loaded")
        except (DatabaseError, DataError, IntegrityError) as e:
            print("Loading of Data into database unsuccessful", e)

    def load_data_age(self):
        df = pd.read_csv("fip_population_age.csv",dtype={"fcode":str})
        list_of_tup = []
        for index, row in df.iterrows():
            list_of_tup.append((
                str(row["fcode"]),
                row["age_range"],
                row["percentage"]
            ))
        sql = """
        INSERT INTO fip_population_age (fcode, age_range,percentage) VALUES %s
        """
        try:
            print("Loading Data into Database...")
            with self.conn:
                with self.conn.cursor() as cur:
                    execute_values(cur, sql=sql, argslist=list_of_tup)
            print("Data loaded")
        except (DatabaseError, DataError, IntegrityError) as e:
            print("Loading of Data into database unsuccessful", e)

    def load_data_race(self):
        df = pd.read_csv("fip_population_race.csv",dtype={"fcode":str})
        list_of_tup = []
        for index, row in df.iterrows():
            list_of_tup.append((
                str(row["fcode"]),
                row["race"],
                row["percentage"]
            ))
        sql = """
        INSERT INTO fip_population_race (fcode,race,percentage) VALUES %s
        """
        try:
            print("Loading Data into Database...")
            with self.conn:
                with self.conn.cursor() as cur:
                    execute_values(cur, sql=sql, argslist=list_of_tup)
            print("Data loaded")
        except (DatabaseError, DataError, IntegrityError) as e:
            print("Loading of Data into database unsuccessful", e)

    def load_data_year(self):
        df = pd.read_csv("fip_population_year.csv",dtype={"fcode":str})
        import numpy
        from psycopg2.extensions import register_adapter, AsIs
        def addapt_numpy_float64(numpy_float64):
            return AsIs(numpy_float64)

        def addapt_numpy_int64(numpy_int64):
            return AsIs(numpy_int64)

        register_adapter(numpy.float64, addapt_numpy_float64)
        register_adapter(numpy.int64, addapt_numpy_int64)
        list_of_tup = []
        for index, row in df.iterrows():
            list_of_tup.append((
                row["fcode"],
                row["year"],
                row["population"]
            ))
        sql = """
        INSERT INTO fip_population_year (fcode, year,population) VALUES %s
        """
        try:
            print("Loading Data into Database...")
            with self.conn:
                with self.conn.cursor() as cur:
                    execute_values(cur, sql=sql, argslist=list_of_tup)
            print("Data loaded")
        except (DatabaseError, DataError, IntegrityError) as e:
            print("Loading of Data into database unsuccessful", e)

    def load_data_fipzip(self):
        df = pd.read_csv("fip_zip.csv",dtype={"fcode":str,"pcode":str})
        import numpy
        from psycopg2.extensions import register_adapter, AsIs
        def addapt_numpy_float64(numpy_float64):
            return AsIs(numpy_float64)

        def addapt_numpy_int64(numpy_int64):
            return AsIs(numpy_int64)

        #register_adapter(numpy.float64, addapt_numpy_float64)
        #register_adapter(numpy.int64, addapt_numpy_int64)
        list_of_tup = []
        for index, row in df.iterrows():
            list_of_tup.append((
                row["pcode"],
                row["fcode"]
            ))
        sql = """
        INSERT INTO fipzip (pcode,fcode) VALUES %s
        """
        try:
            print("Loading Data into Database...")
            with self.conn:
                with self.conn.cursor() as cur:
                    execute_values(cur, sql=sql, argslist=list_of_tup)
            print("Data loaded")
        except (DatabaseError, DataError, IntegrityError) as e:
            print("Loading of Data into database unsuccessful", e)

    def load_data_facilities_loc(self):
        df = pd.read_csv("locations_fac.csv",dtype={"zipcode":str})
        list_of_tup = []
        for index, row in df.iterrows():
            list_of_tup.append((
                row["objectid"],
                row["zipcode"],
                row["fac_type"],
                row["fac_name"],
                row["x"],
                row["y"],
                row["date_updte"],
                row["city"],
                row["state"],
            ))
        sql = """
        INSERT INTO facilities_location (objectid,pcode,fac_type,fac_name,lon,lat,date_updte,city,state) VALUES %s
        """
        try:
            print("Loading Data into Database...")
            with self.conn:
                with self.conn.cursor() as cur:
                    execute_values(cur, sql=sql, argslist=list_of_tup)
            print("Data loaded")
        except (DatabaseError, DataError, IntegrityError) as e:
            print("Loading of Data into database unsuccessful", e)

    def load_data_facilities(self):
        df = pd.read_csv("facilities.csv")
        list_of_tup = []
        for index, row in df.iterrows():
            list_of_tup.append((
                row["objectid"],
                row["ferry_t"],
                row["ferry_i"],
                row["bus_t"],
                row["bus_i"],
                row["bus_code_s"],
                row["bus_supp"],
                row["rail_i"],
                row["rail_c"],
                row["rail_h"],
                row["rail_light"],
                row["air_serve"],
                row["bike_share"],
                row["bike_sys"],
                row["i_service"],
                row["t_service"],
                row["modes_serv"],
                row["mode_bus"],
                row["mode_air"],
                row["mode_rail"],
                row["mode_ferry"],
                row["mode_bike"],
            ))
        sql = """
        INSERT INTO facilities (objectid, ferry_t, ferry_i, bus_t, bus_i, bus_code_s,
       bus_supp, rail_i, rail_c, rail_h, rail_light, air_serve,
       bike_share, bike_sys, i_service, t_service, modes_serv,
       mode_bus, mode_air, mode_rail, mode_ferry, mode_bike) VALUES %s
        """
        try:
            print("Loading Data into Database...")
            with self.conn:
                with self.conn.cursor() as cur:
                    execute_values(cur, sql=sql, argslist=list_of_tup)
            print("Data loaded")
        except (DatabaseError, DataError, IntegrityError) as e:
            print("Loading of Data into database unsuccessful", e)

if __name__ =="__main__":
    FacilitiesCountiesPopulator().load_data_counties()
    FacilitiesCountiesPopulator().load_data_age()
    FacilitiesCountiesPopulator().load_data_race()
    FacilitiesCountiesPopulator().load_data_year()
    FacilitiesCountiesPopulator().load_data_fipzip()
    FacilitiesCountiesPopulator().load_data_facilities_loc()
    FacilitiesCountiesPopulator().load_data_facilities()