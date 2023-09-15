import pandas as pd
import json

class weitere_daten_prepper:
    
    def __init__(self):
        """
        These methods for preparing data would be used after the data is downloaded with the help of the
        Weitere_datenquellen.sh Bash script from sql_setup folder
        """
        self.__states:list=["AZ","IL","NV","NC","OH","PA","WI"]
        self.__ipcd_2018:pd.DataFrame = self.ipcd_reader()
        self.__counties_raw:json = self.counties_reader()
        self.__counties_df:pd.DataFrame = self.counties_data_cleaner()
        self.ipcd_data_cleaner()
        
    
    def ipcd_reader(self):
        """
        Function:
            Data from Intermodal Passenger Connectivity Database from 2018 would be loaded with this method
        
        Returns:
            Pandas Dataframe of Intermodal Passenger Connectivity Database from 2028
        """
        self.__ipcd_2018 = pd.read_csv("Intermodal_Passenger_Connectivity_Database_IPCD.csv",delimiter=",")
        return self.__ipcd_2018
    
    def counties_reader(self):
        """
        Functions:
            json file from counties.json would be loaded into __counties_raw with this method
        
        Returns:
            json of counties
        """
        with open('counties.json') as json_file:
            self.__counties_raw = json.load(json_file)
        return self.__counties_raw

    def ipcd_data_cleaner(self):
        
        """
        Functions:
            Drops unwanted columns
            Filters Data by important cities ( we have 10 Clusters and 7 of those lie in th US )
            Replaces 1 and 0s form modes of transport with boolean values
            Replaces wrongly inserted zipcodes
        """
        unwanted = ["near_id_1","near_id_2","near_id_3","air_code","air_code2","bike_id","fac_id","amtrakcode","ferry_code","website"
           ,"point_lat","point_lon","cbsa_code","cbsa_type","source","notes","bike_sys_id","ferry_code","rail_id","bike_id","longitude","latitude","point_id","metro_area"]
        self.__ipcd_2018.drop(columns=unwanted,inplace =True)
        #Take cities of importance

        important_states_data = []

        for i in self.__ipcd_2018.values.tolist():
            for j in self.__states:
                if j in i :
                    important_states_data.append(i)

        self.__ipcd_2018 = pd.DataFrame(important_states_data,columns = self.__ipcd_2018.columns)

        #Replace 1 and 0s in modes with Boolean values
        for i in ["mode_bus","mode_air","mode_rail","mode_ferry","mode_bike"]:
            self.__ipcd_2018.replace({i:1},True,inplace=True)
            self.__ipcd_2018.replace({i:0},False,inplace=True)

        self.__ipcd_2018["bus_t"] = self.__ipcd_2018["bus_t"].apply(lambda x:int(x))
        #Change date_updte from string to datetime
        self.__ipcd_2018["date_updte"] =pd.to_datetime(arg=self.__ipcd_2018["date_updte"],errors="ignore")
        self.__ipcd_2018.replace({"zipcode":{60210:60201,43602:43604,85222:85122,85239:85138,20804:60804,60019:60119,
                                             60983:60938,62595:62959,98201:60021,19042:19041,19065:19063,51466:54166,60092:60048}},inplace=True)
        self.__ipcd_2018=self.__ipcd_2018[~((self.__ipcd_2018["zipcode"]==19703)|(self.__ipcd_2018["zipcode"]==19801))]



    def counties_data_cleaner(self):
        """
        Functions:
            Filters by important states for counties dataframe
            Replace state names with abbreveations

        Returns:
            Cleaned/Filtered counties data frame
        """
        attributes = ["state", "county"]
        for attribute in self.__counties_raw["Nebraska"]["cuming county"]:
            attributes.append(attribute)

        county_info = []
        for state in self.__counties_raw:
            for county in self.__counties_raw[state]:
                self.__counties_raw[state][county]["state"] = state
                self.__counties_raw[state][county]["county"] = county
                county_info.append(self.__counties_raw[state][county])

        self.__counties_df = pd.DataFrame(county_info, columns=attributes)
        
        self.__counties_df.replace({"state":{'Nebraska':"NE",'Washington':"WA",'New Mexico':"NM",'South Dakota':"SD",'Texas':"TX",'California':"CA",'Kentucky':"KY",'Ohio':"OH",'Alabama':"AL", 
                                             'Georgia':"GA", 'Wisconsin':"WI", 'Arkansas':"AR", 'Oregon':"OR", 'Pennsylvania':"PA", 'Mississippi':"MS", 'Missouri':"MO", 'Colorado':"CO",
                                             'North Carolina':"NC",'Utah':"UT", 'Oklahoma':"OK", 'Virginia':"VA", 'Tennessee':"TN", 'Wyoming':"WY", 'West Virginia':"WV", 'Louisiana':"LA", 
                                             'New York':"NY", 'Michigan':"MI", 'Indiana':"IN",'Massachusetts':"MA", 'Kansas':"KS", 'Idaho':"ID", 'Florida':"FL", 'Alaska':"AK", 'Nevada':"NV",
                                             'Illinois':"IL", 'Vermont':"VT", 'Connecticut':"CT", 'Montana':"MT", 'New Jersey':"NJ",'Minnesota':"MN", 'North Dakota':"ND", 'Maryland':"MD",
                                             'Iowa':"IA", 'South Carolina':"SC", 'Maine':"ME", 'Hawaii':"HI", 'New Hampshire':"NH", 'Arizona':"AZ", 'Delaware':"DE", 'District of Columbia':"DC",
                                             'Rhode Island':"RI"}},inplace=True)
        
        return self.__counties_df


    def ipcd_csv_file_creator(self):
        """
        Functions:
            Transforms ipcd data into locations of facilities (locations_fac) and their respective facilities database upload
        """
        #Create 2 csv files for data to be loaded into databank
        locations_fac = self.__ipcd_2018[['objectid','zipcode','fac_type', 'fac_name',"x", 'y', 'date_updte', 'address', 'city', 'state' ]]
        facilities = self.__ipcd_2018[['objectid','ferry_t', 'ferry_i', 'bus_t', 'bus_i',
               'bus_code_s', 'bus_supp', 'rail_i', 'rail_c', 'rail_h', 'rail_light',
               'air_serve', 'bike_share', 'bike_sys', 'i_service', 't_service',
               'modes_serv', 'mode_bus', 'mode_air', 'mode_rail', 'mode_ferry',
               'mode_bike']]
        locations_fac.to_csv(path_or_buf="locations_fac.csv",index=False)
        facilities.to_csv(path_or_buf="facilities.csv",index=False)


    def fipzip_csv_creator(self):
        """
        Functions:
            Creates csv file for fip and zip codes for database
        """
        # Erstelle FipZip Dataframe
        fip_to_zip = []
        zip_code_list = []
        for fips, zips in self.__counties_df[['fips', 'zip-codes']].values.tolist():
            for i in zips:
                if i not in zip_code_list:
                    zip_code_list.append(i)
                    fip_to_zip.append((fips, i))
        fip_zip_df = pd.DataFrame(fip_to_zip, columns=['fip-code', 'zip-code'])

        fip_zip_df = fip_zip_df.rename({'fip-code': 'fcode', 'zip-code': 'pcode'}, axis=1)
        fip_zip_df=fip_zip_df.append({"fcode":"39061","pcode":"45221"},ignore_index=True)
        fip_zip_df["fcode"]=fip_zip_df["fcode"].apply(lambda x:str(x))
        fip_zip_df.to_csv('fip_zip.csv',index=False)

    def fip_population_year_csv_creator(self):
        """
        Functions:
            Creates csv file for annual population statistics for each county 
        """
        # Erstelle Dataframe für Population nach Jahren
        year_demographics = self.__counties_df['population'].values.tolist()
        df_year = pd.DataFrame(year_demographics)
        df_year = pd.concat([self.__counties_df["fips"], df_year], ignore_index=True, axis=1)

        df_year = df_year.rename({0: 'fcode'}, axis=1)
        for i in range(1, 11):
            df_year = df_year.rename({i: 'pop_' + str(2009 + i)}, axis=1)
        df_year= pd.melt(df_year,id_vars=["fcode"],
                         value_name="population",
                         var_name="year",
                         ignore_index=True)
        df_year["year"]=df_year["year"].apply(lambda x:int(x.strip("pop_")))
        df_year.sort_values(by=["fcode","year"],inplace=True)
        df_year.to_csv("fip_population_year.csv",index=False)

    def fip_population_race_csv_creator(self):
        """
        Functions:
            Creates csv file for percentage of population for each race
        """
        # Erstelle Dataframe für ethnische Anteile der Population
        race_demographics = self.__counties_df['race_demographics'].values.tolist()
        df_race = pd.DataFrame(race_demographics)
        df_race = pd.concat([self.__counties_df["fips"], df_race], ignore_index=True, axis=1)

        df_race = df_race.rename(
            {0: 'fcode', 1: 'white_male', 2: 'white_female', 3: 'black_male', 4: 'black_female', 5: 'asian_male',
             6: 'asian_female', 7: 'hispanic_male', 8: 'hispanic_female'}, axis=1)
        df_race = pd.melt(df_race, id_vars=["fcode"], value_name="percentage", var_name="race", ignore_index=True)
        df_race.sort_values(by=["fcode"],inplace=True)
        df_race.to_csv("fip_population_race.csv", index=False)

    def fip_population_age_csv_creator(self):
        """
        Functions:
            Creates csv file for percentage of population for each age group
        """
        # Erstelle Dataframe für Anteile verschiedener Altersgruppen
        age_demographics = self.__counties_df['age_demographics'].values.tolist()
        df_age = pd.DataFrame(age_demographics)
        df_age = pd.concat([self.__counties_df["fips"], df_age], ignore_index=True, axis=1)

        df_age = df_age.rename({0: 'fcode'}, axis=1)
        i = 1
        for key in self.__counties_df["age_demographics"][0]:
            df_age = df_age.rename({i: 'age_' + key.replace('-', '_')}, axis=1)
            i += 1
        df_age=pd.melt(df_age, id_vars=["fcode"], value_name="percentage", var_name="age_range", ignore_index=True)
        df_age.sort_values(by=["fcode"], inplace=True)
        df_age.to_csv("fip_population_age.csv", index=False)

    def counties_csv_creator(self):
        """
        Functions:
            Creates csv file for each countie's information
        """
        # Entferne unnötige Spalten bzw. Umbennenung des Dataframes
        self.__counties_df = self.__counties_df.rename({'fips': 'fcode'}, axis=1)
        self.__counties_df.drop(
            columns=['zip-codes', 'male', 'female', 'population', 'race_demographics', 'age_demographics', 'noaa',
                     'deaths', 'bls', 'num_police', 'police_deaths', 'fatal_police_shootings', 'covid-deaths',
                     'covid-confirmed', 'elections'], axis=1, inplace=True)
        self.__counties_df.to_csv("counties.csv",index=False)

    def get_ipcd_2018(self):
        return self.__ipcd_2018

    def get_counties_df(self):
        return self.__counties_df

    def get_counties_raw(self):
        return self.__counties_raw

    def get_states(self):
        return self.__states
    
if __name__ == "__main__":
    weitere_daten = weitere_daten_prepper()
    weitere_daten.ipcd_csv_file_creator()
    weitere_daten.fipzip_csv_creator()
    weitere_daten.fip_population_age_csv_creator()
    weitere_daten.fip_population_race_csv_creator()
    weitere_daten.fip_population_year_csv_creator()
    weitere_daten.counties_csv_creator()