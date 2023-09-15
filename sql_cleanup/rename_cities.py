import os
import sys
import json
import requests
import pandas as pd

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
module_path = os.path.abspath(os.path.join('.'))
if module_path not in sys.path:
    sys.path.append(module_path)
from src.database_handler import DatabaseHandler  # wrong-import-position: ignore
from sql_cleanup.closest_station import WeatherLinker  # wrong-import-position: ignore

NAMELIST_CITIES = [
    ("avon", "Avon",),
    ("Bath", "Bath Township",),
    ("Brimfield", "Brimfield Township"),
    ("Bedford (Ville)", "Bedford"),
    ("Boulder City NV", "Boulder City",),
    ("Boulder City, NV", "Boulder City",),
    ("Buckeye - Shaker", "Buckeye"),
    ("Calagry", "Calgary"),
    ("calgary", "Calgary",),
    ("canonsburg", "Canonsburg",),
    ("cave creek", "Cave Creek",),
    ("cave Creek", "Cave Creek",),
    ("Cecil", "Cecil Township"),
    ("Chardom", "Chardon",),
    ("Chardon Township", "Chardon",),
    ("CHARLOTTE", "Charlotte",),
    ("Charlote", "Charlotte",),
    ("Charlotte, NC", "Charlotte",),
    ("cleveland", "Cleveland"),
    ("Cleveland OH", "Cleveland"),
    ("Cleveland OH", "Cleveland"),
    ("Cleveland (Westlake)", "Cleveland"),
    ("Clevland", "Cleveland"),
    ("Cleveland heights", "Cleveland Heights"),
    ("1000", "Cleveland"),
    ("1100", "Cleveland"),
    ("CONCORD", "Concord"),
    ("Concord Mills", "Concord"),
    ("Concord Township", "Concord"),
    ("Copley", "Copley Township"),
    ("De Forest", "DeForest"),
    ("Dollard-Des Ormeaux", "Dollard-Des-Ormeaux"),
    ("Etobicoke, ON", "Etobicoke"),
    ("Etoicoke", "Etobicoke"),
    ("Fairview", "Fairview Park"),
    ("Fort Mcdowell", "Fort McDowell"),
    ("Fort mill", "Fort Mill"),
    ("Fort  Mill", "Fort Mill"),
    ("Fort MIll", "Fort Mill"),
    ("Ft. Mill", "Fort Mill"),
    ("glendale", "Glendale"),
    ("Glendale;Peoria", "Glendale"),
    ("hudson", "Hudson"),
    ("Hiram Township", "Hiram"),
    ("Highland Hts", "Highland Heights"),
    ("Hinckley", "Hinckley Township"),
    ("Kennedy Township", "Kennedy"),
    ("Indian Land,", "Indian Land"),
    ("Indian Land, South Carolina", "Indian Land"),
    ("Kahnawake", "Kahnawá:ke"),
    ("Lagrange", "LaGrange"),
    ("LaGrange Township", "LaGrange"),
    ("LaSalle", "Lasalle"),
    ("Las vegas", "Las Vegas"),
    ("Las  Vegas", "Las Vegas"),
    ("Las Vegas ", "Las Vegas"),
    ("LAS VEGAS", "Las Vegas"),
    ("Las Vegas NV", "Las Vegas"),
    ("Las Vegas, NV", "Las Vegas"),
    ("Laval (13)", "Laval"),
    ("Laveen Village", "Laveen"),
    ("L'ile-Perrot", "L'Île-Perrot"),
    ("LITCHFIELD PK", "Litchfield Park"),
    ("Litchfield park", "Litchfield Park"),
    ("Litchfield", "Litchfield Park"),
    ("Madison WI", "Madison"),
    ("Marshall", "Marshall Township"),
    ("Mayfield Hts", "Mayfield Heights"),
    ("Mcfarland", "McFarland"),
    ("Mc Farland", "McFarland"),
    ("Mckees Rocks", "McKees Rocks"),
    ("Mc Kees Rocks", "McKees Rocks"),
    ("Mc Murray", "McMurray"),
    ("Mcmurray", "McMurray"),
    ("mentor", "Mentor"),
    ("Middleburgh Heights", "Middleburg Heights"),
    ("Middleburg Hts", "Middleburg Heights"),
    ("Middleburg Hts.", "Middleburg Heights"),
    ("monroeville", "Monroeville"),
    ("Montréa", "Montréal"),
    ("montreal", "Montréal"),
    ("Montreal", "Montréal"),
    ("Montréal-Est", "Montréal"),
    ("Montréal-Nord", "Montréal"),
    ("Montréal-Ouest", "Montréal"),
    ("Montville", "Montville Township"),
    ("Moon Townshop", "Moon Township"),
    ("Moon", "Moon Township"),
    ("moon", "Moon Township"),
    ("N E Las Vegas", "Las Vegas"),
    ("Nellis Afb", "Nellis AFB"),
    ("NELLIS AFB", "Nellis AFB"),
    ("Nellis Air Force Base", "Nellis AFB"),
    ("Neville Township", "Neville"),
    ("Notre-Dame-de-l'Ile-Perrot", "Notre-Dame-de-l'Île-Perrot"),
    ("Olmsted Tiownship", "Olmsted Township"),
    ("Orange Village", "Orange"),
    ("Parradise Valley", "Paradise Valley"),
    ("Peoria, AZ", "Peoria"),
    ("PeoriaPeoria", "Peoria"),
    ("Perry Twp", "Perry"),
    ("phoenix", "Phoenix"),
    ("Phonenix", "Phoenix"),
    ("pickering", "Pickering"),
    ("Pittsburgh;Upper St. Clair", "Pittsburgh"),
    ("plum", "Plum"),
    ("Richfield Township", "Richfield"),
    ("Richmond Hill (Oak Ridges)", "Richmond Hill"),
    ("Robinson", "Robinson Townshipy"),
    ("Rocky river", "Rocky River"),
    ("Rockyview", "Rocky View"),
    ("Rockyview County", "Rocky View"),
    ("Rocky View County", "Rocky View"),
    ("Rocky View No. 44", "Rocky View"),
    ("Saint-Bruno", "Saint-Bruno-de-Montarville"),
    ("Saint Laurent", "Saint-Laurent"),
    ("Sheffield Village", "Sheffield Township"),
    ("South Park", "South Park Township"),
    ("St Joseph", "St. Joseph"),
    ("Sun", "Sun City"),
    ("surprise", "Surprise"),
    ("Tempe, AZ", "Tempe"),
    ("toronto", "Toronto"),
    ("Torontoitalian", "Toronto"),
    ("Toronto;Scarborough", "Toronto"),
    ("Toronto;Torornto", "Toronto"),
    ("Upper St Clair", "Upper St. Clair"),
    ("Vaughan (Maple)", "Vaughan"),
    ("York, Toronto", "York"),
    ("York Township", "York"),
]


class CityCorrector:
    def __init__(self):
        self.__handler = DatabaseHandler()
        self.__query = self.__handler.querry_database
        self.__insert_many = self.__handler.insert_many
        self.city_df = self.__get_station_data()
        self.new_information = []

    def __get_station_data(self) -> pd.DataFrame:
        sql = "SELECT bid, lon, lat, city from business"
        col = ["bid", "lon", "lat", "city"]
        data = self.__query(sql)
        return pd.DataFrame(data, columns=col)

    def create_city_data(self):
        """Fetch all cities to lon/lat and saves not identical city names"""
        print("Starting to get all city data")
        total_data = len(self.city_df)
        steps = int(total_data / 100)
        for number, (_, row) in enumerate(self.city_df.iterrows()):
            if number % steps == 0:
                print(f"{number/total_data:.0%}", end=" ")
            lon = row["lon"]
            lat = row["lat"]
            saved_city = row["city"]
            payload = {"lon": lon, "lat": lat}
            try:
                r = requests.get("https://photon.ljansen.net/reverse", params=payload, auth=('api', 'apiuser'))
                resp = json.loads(r.text)
                city = None
                try:
                    city = resp["features"][0]["properties"]["city"]
                except (KeyError, IndexError):
                    pass
                if city is not None and city != saved_city:
                    self.new_information.append((row["bid"], city))
            except requests.exceptions.RequestException as exep:
                print(f"\n{exep}")

    def update_fetched_cities(self):
        """Updates the DB data with the newly fetched city information"""
        sql = """
        UPDATE business
        set city = data.city
        from (values %s) as data (bid, city)
        where business.bid = data.bid
        """
        self.__insert_many(sql, self.new_information)

    def rename_remaining_douplicates(self):
        """Rename cities in DB according to list"""
        for (old, new) in NAMELIST_CITIES:
            sql = "UPDATE business set city = %(newcity)s where city = %(oldcity)s"
            dat = {"newcity": new, "oldcity": old}
            self.__query(sql, dat)


if __name__ == "__main__":
    cc = CityCorrector()
    cc.create_city_data()
    cc.update_fetched_cities()
    cc.rename_remaining_douplicates()
