####################################################################################################################
# This script calculates statistics of inverse indexes                                                        ######
####################################################################################################################

import math
from datetime import datetime
from functools import reduce
from operator import add
from statistics import median

from os import getcwd
import sys

# Mandatory if we want to run this script from windows cmd. Must precede all imports from this project
conf_path = getcwd()
sys.path.append(conf_path)
sys.path.append(conf_path + '..')
sys.path.append(conf_path + '../..')

# Custom imports from other folders of this project
# All paths to directories within project are held in one play, to be able to change them easily.
from shared_info import index_directory
# Index names are stored at corresponding indexers, so that they are unified across the project
from Indexer.create_index_judge import index_name as index_name_judge
from Indexer.create_index_court import index_name as index_name_court
from Indexer.create_index_date import index_name as index_name_date
from Indexer.create_index_reference_number import index_name as index_name_reference_number


# Function to create cardinality dictionary for values of given index
def create_cardinality_dict(in_index_name):
    value_dict = {}
    # Let's prepare path to index file of given index.
    index_file_name = index_directory + "\index_" + in_index_name + ".txt"
    # Open the index file
    with open(index_file_name, 'r', encoding='utf-8') as input_file:
        # Loop over lines of the index file and note every value in result dict
        for line in input_file:
            tokens = line.split(':')
            value = tokens[0]
            cardinality = len(tokens[1].split(','))
            value_dict[value] = cardinality

    return value_dict


# Function to turn cardinality dict of values to list of dicts -> so that they can be ordered by cardinality
def convert_cardinality_dict_2_list(in_value_dict):
    values = [{'value': key, 'cardinality': in_value_dict[key]} for key in in_value_dict]
    values.sort(key=lambda x: x['cardinality'])
    values.reverse()
    return  values


# Function to determine name of the city based on court name
def convert_court_name_2_city(court_name):
    if "Bratislava" in court_name or "Najvyšší súd" == court_name:
        return "Bratislava"
    if "Košice" in court_name:
        return "Košice"
    elif "Špecializovaný trestný súd" == court_name:
        return "Pezinok"
    else:
        start_index = court_name.find("súd") + 4
        return court_name[start_index:]


# Function to determine district name ('kraj') based on city name
def convert_city_name_2_district_name(city_name):
    if city_name in ["Bratislava", "Pezinok", "Malacky"]:
        return "Bratislava"
    if city_name in ["Banská Bystrica", "Lučenec", "Zvolen", "Rimavská Sobota", "Revúca", "Žiar nad Hronom", "Brezno", "Veľký Krtíš"]:
        return "Banská Bystrica"
    if city_name in ["Prešov", "Humenné", "Poprad", "Kežmarok", "Vranov nad Topľou", "Bardejov", "Svidník", "Stará Ľubovňa"]:
        return "Prešov"
    if city_name in ["Nitra", "Nové Zámky", "Komárno", "Levice", "Topoľčany"]:
        return "Nitra"
    if city_name in ["Trnava", "Dunajská Streda", "Galanta", "Piešťany", "Senica", "Skalica"]:
        return "Trnava"
    if city_name in ["Trenčín", "Prievidza", "Považská Bystrica", "Nové Mesto nad Váhom", "Partizánske", "Bánovce nad Bebravou"]:
        return "Trenčín"
    if city_name in ["Žilina", "Martin", "Čadca", "Liptovský Mikuláš", "Námestovo", "Dolný Kubín", "Ružomberok"]:
        return "Žilina"
    if city_name in ["Košice", "Spišská Nová Ves", "Rožňava", "Michalovce", "Trebišov"]:
        return "Košice"
    return "Unknown - " + city_name


# Let's prepare list of index names for unified processing
index_names_nominal_value = [index_name_judge, index_name_court, index_name_reference_number, index_name_date]
# Let's loop over all index names and calculate statistics for them
for index_name in index_names_nominal_value:
    # Let's create dict of cardinalities of values of current index
    value_dict = create_cardinality_dict(index_name)
    # Let's print name of current index
    print(index_name)
    # Let's convert dictionary to ordered list of dictionaries
    values = convert_cardinality_dict_2_list(value_dict)
    # Get attribute value with max cardinality
    print("Max cardinality: {}".format(values[0]['cardinality']))
    print("Values with max cardinality: {}".format(list(filter(lambda x: x['cardinality'] == values[0]['cardinality'], values))))
    # Let's print 20 most frequent values. Output format is convenient for copy-pasting into excel sheets
    for i in range(min(len(values), 20)):
        print(values[i]['value'])
    for i in range(min(len(values), 20)):
        print(values[i]['cardinality'])

    # Let's perform action specific for courts
    if index_name == index_name_court:
        # Let's turn courts into cities (group by city)
        cities = [{'value': convert_court_name_2_city(x['value']), 'cardinality': x['cardinality']} for x in values]
        # Calculate cardinalities for cities
        new_value_dict = {}
        for city in cities:
            if city['value'] not in new_value_dict:
                new_value_dict[city['value']] = city['cardinality']
            else:
                new_value_dict[city['value']] += city['cardinality']
        new_values = convert_cardinality_dict_2_list(new_value_dict)
        print("Cities")
        # Let's print 20 most frequent values. Output format is convenient for copy-pasting into excel sheets
        for i in range(len(new_values)):
            print(new_values[i]['value'])
        for i in range(len(new_values)):
            print(new_values[i]['cardinality'])
        print(cities)
        print("Cities")

        # Let's turn courts into districts (group by district)
        districts = [{'value': convert_city_name_2_district_name(x['value']), 'cardinality': x['cardinality']} for x in cities]
        print(districts)
        # Calculate cardinalities for cities
        new_value_dict = {}
        for district in districts:
            if district['value'] not in new_value_dict:
                new_value_dict[district['value']] = district['cardinality']
            else:
                new_value_dict[district['value']] += district['cardinality']
        print(new_value_dict)
        new_values = convert_cardinality_dict_2_list(new_value_dict)
        print("Districts")
        # Let's print 20 most frequent values. Output format is convenient for copy-pasting into excel sheets
        for i in range(len(new_values)):
            print(new_values[i]['value'])
        for i in range(len(new_values)):
            print(new_values[i]['cardinality'])
        print(districts)
        print("Districts")
    # Let's perform action specific for reference number
    if index_name == index_name_reference_number:
        print("____________")
        # Calculate cardinalities for counts of usage of reference number
        # (how many ref. numbers are used for 1,2,...9) documents
        new_value_dict = {}
        for entry in values:
            if entry['cardinality'] not in new_value_dict:
                new_value_dict[entry['cardinality']] = 1
            else:
                new_value_dict[entry['cardinality']] += 1
        new_values = convert_cardinality_dict_2_list(new_value_dict)
        # Let's print 20 most frequent values. Output format is convenient for copy-pasting into excel sheets
        for i in range(len(new_values)):
            print(new_values[i]['value'])
        for i in range(len(new_values)):
            print(new_values[i]['cardinality'])
        print("log")
        for i in range(len(new_values)):
            print(int(round(math.log(new_values[i]['cardinality']), 3) * 1000))
        print("____________")
    # Let's perform action specific for dates - the only ordinal attribute
    if index_name == index_name_date:
        new_values = []
        # Need to convert string to date
        for value in values:
            for i in range(value['cardinality']):
                new_values.append(datetime.strptime(value['value'], "%d. %m. %Y"))
        times_only = list(map(lambda x: x.timestamp(), new_values))

        # Determine Average, Modus, Median in computer-convenient format
        average_time = reduce(add, times_only) / len(times_only)
        modus_time = max(set(times_only), key=times_only.count)
        median_time = median(times_only)

        # Print in computer-convenient format
        print("Average is {}".format(average_time))
        print("Modus is {}".format(modus_time))
        print("Median is {}".format(median_time))

        # Determine Average, Modus, Median in human-readable format
        average = datetime.fromtimestamp(average_time)
        modus = datetime.fromtimestamp(modus_time)
        median = datetime.fromtimestamp(median_time)

        # Print in human-readable format
        print("Average is {}".format(average))
        print("Modus is {}".format(modus))
        print("Median is {}".format(median))

    # Let's separate current attribute's data from another
    print("-------------------------------------")



