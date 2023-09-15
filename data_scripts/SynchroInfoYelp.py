import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import functools
# import simplejson as json
# import time

json_file_path = "C:/Users/X230/Documents/SharedVmHost/yelp_academic_dataset_business.json"

def open_json_file(json_file_path):
    """

    :param json_file_path:
    :return:
    """
    df_json_file = pd.read_json(json_file_path, lines= True)
    return df_json_file


#Gets Column Names of Pandas Dataframe of Yelp Json file and returns as list
def get_column_names(json_file_path):
    column_names = []
    df = open_json_file(json_file_path)
    for column in df.columns:
        column_names.append(column)
    return column_names

def get_opening_hours(df_yelp,day):
    df_yelp_hours = df_yelp["hours"]

    if df_yelp_hours is None:
        return None
    else:
        return df_yelp_hours.get(day,None)

def insert_opening_hours(df_yelp):
    days = "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday".split(",")
    for day in days:
        df_yelp[day] = df_yelp.apply(get_opening_hours, axis=1, args=(day,))
    df_yelp.drop(columns="hours",inplace=True)
    return df_yelp


def get_list_of_categories(df_yelp):
    all_categories = []
    for row in df_yelp["categories"]:
        row_cat = str(row).split(",")
        for s in row_cat:
            if s.strip() in all_categories:
                continue
            else:
                all_categories.append(s.strip())
    return all_categories

def list_important_cat(important_categories):
    important_categories_split = important_categories.split("\n")

    list_of_categories =[]
    for i in important_categories_split:
        str_list = i.split(" ")
        str_list.pop()
        str_list_joined = " ".join(str_list)
        list_of_categories.append(str_list_joined)
    return list_of_categories


def insert_important_business(df_yelp,list_of_categories):
    index_of_similar_cat =[]
    for index,i in df_yelp.categories.items():
        similarity = set(i).intersection(set(list_of_categories))
        if len(similarity) > 0:
            index_of_similar_cat.append(index)
    new_df = df.iloc[index_of_similar_cat,]
    return new_df.reset_index(drop=True,inplace=True)



important_categories = """Afghan (afghani)
African (african)
Senegalese (senegalese)
South African (southafrican)
American (New) (newamerican)
American (Traditional) (tradamerican)
Arabian (arabian)
Argentine (argentine)
Armenian (armenian)
Asian Fusion (asianfusion)
Australian (australian)
Austrian (austrian)
Bangladeshi (bangladeshi)
Barbeque (bbq)
Basque (basque)
Belgian (belgian)
Brasseries (brasseries)
Brazilian (brazilian)
Breakfast & Brunch (breakfast_brunch)
Pancakes (pancakes)
British (british)
Buffets (buffets)
Bulgarian (bulgarian)
Burgers (burgers)
Burmese (burmese)
Cafes (cafes)
Themed Cafes (themedcafes)
Cafeteria (cafeteria)
Cajun/Creole (cajun)
Cambodian (cambodian)
Caribbean (caribbean)
Dominican (dominican)
Haitian (haitian)
Puerto Rican (puertorican)
Trinidadian (trinidadian)
Catalan (catalan)
Cheesesteaks (cheesesteaks)
Chicken Shop (chickenshop)
Chicken Wings (chicken_wings)
Chinese (chinese)
Cantonese (cantonese)
Dim Sum (dimsum)
Hainan (hainan)
Shanghainese (shanghainese)
Szechuan (szechuan)
Comfort Food (comfortfood)
Creperies (creperies)
Cuban (cuban)
Czech (czech)
Delis (delis)
Diners (diners)
Dinner Theater (dinnertheater)
Eritrean (eritrean)
Ethiopian (ethiopian)
Fast Food (hotdogs)
Filipino (filipino)
Fish & Chips (fishnchips)
Fondue (fondue)
Food Court (food_court)
Food Stands (foodstands)
French (french)
Mauritius (mauritius)
Reunion (reunion)
Game Meat (gamemeat)
Gastropubs (gastropubs)
Georgian (georgian)
German (german)
Gluten-Free (gluten_free)
Greek (greek)
Guamanian (guamanian)
Halal (halal)
Hawaiian (hawaiian)
Himalayan/Nepalese (himalayan)
Honduran (honduran)
Hong Kong Style Cafe (hkcafe)
Hot Dogs (hotdog)
Hot Pot (hotpot)
Hungarian (hungarian)
Iberian (iberian)
Indian (indpak)
Indonesian (indonesian)
Irish (irish)
Italian (italian)
Calabrian (calabrian)
Sardinian (sardinian)
Sicilian (sicilian)
Tuscan (tuscan)
Japanese (japanese)
Conveyor Belt Sushi (conveyorsushi)
Izakaya (izakaya)
Japanese Curry (japacurry)
Ramen (ramen)
Teppanyaki (teppanyaki)
Kebab (kebab)
Korean (korean)
Kosher (kosher)
Laotian (laotian)
Latin American (latin)
Colombian (colombian)
Salvadoran (salvadoran)
Venezuelan (venezuelan)
Live/Raw Food (raw_food)
Malaysian (malaysian)
Mediterranean (mediterranean)
Falafel (falafel)
Mexican (mexican)
Tacos (tacos)
Middle Eastern (mideastern)
Egyptian (egyptian)
Lebanese (lebanese)
Modern European (modern_european)
Mongolian (mongolian)
Moroccan (moroccan)
New Mexican Cuisine (newmexican)
Nicaraguan (nicaraguan)
Noodles (noodles)
Pakistani (pakistani)
Pan Asian (panasian)
Persian/Iranian (persian)
Peruvian (peruvian)
Pizza (pizza)
Polish (polish)
Polynesian (polynesian)
Pop-Up Restaurants (popuprestaurants)
Portuguese (portuguese)
Poutineries (poutineries)
Russian (russian)
Salad (salad)
Sandwiches (sandwiches)
Scandinavian (scandinavian)
Scottish (scottish)
Seafood (seafood)
Singaporean (singaporean)
Slovakian (slovakian)
Somali (somali)
Soul Food (soulfood)
Soup (soup)
Southern (southern)
Spanish (spanish)
Sri Lankan (srilankan)
Steakhouses (steak)
Supper Clubs (supperclubs)
Sushi Bars (sushi)
Syrian (syrian)
Taiwanese (taiwanese)
Tapas Bars (tapas)
Tapas/Small Plates (tapasmallplates)
Tex-Mex (tex-mex)
Thai (thai)
Turkish (turkish)
Ukrainian (ukrainian)
Uzbek (uzbek)
Vegan (vegan)
Vegetarian (vegetarian)
Vietnamese (vietnamese)
Waffles (waffles)
Wraps (wraps)"""

if __name__ = "__name__":

    df_yelp_business = open_json_file(json_file_path)

    df_with_opening_hours = insert_opening_hours(df_yelp_business)
