import math
from datetime import datetime, date
from functools import reduce
from operator import add
from statistics import median

from shared_info import index_directory
from Indexer.create_index_judge import index_name as index_name_judge
from Indexer.create_index_court import index_name as index_name_court
from Indexer.create_index_date import index_name as index_name_date
from Indexer.create_index_reference_number import index_name as index_name_reference_number
from Indexer.create_index_id_number import index_name as index_name_id_number


def create_cardinality_dict(in_index_name):
    value_dict = {}
    index_file_name = index_directory + "\index_" + in_index_name + ".txt"
    with open(index_file_name, 'r', encoding='utf-8') as input_file:
        for line in input_file:
            tokens = line.split(':')
            value = tokens[0]
            cardinality = len(tokens[1].split(','))
            value_dict[value] = cardinality

    return value_dict


def convert_cardinality_dict_2_list(in_value_dict):
    values = [{'value': key, 'cardinality': in_value_dict[key]} for key in in_value_dict]
    values.sort(key=lambda x: x['cardinality'])
    values.reverse()
    return  values


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


index_names_nominal_value = [index_name_judge, index_name_court, index_name_reference_number, index_name_date]
for index_name in index_names_nominal_value:
    value_dict = create_cardinality_dict(index_name)
    print(index_name)
    values = convert_cardinality_dict_2_list(value_dict)
    # Get attribute value with max cardinality
    print("Max cardinality: {}".format(values[0]['cardinality']))
    print("Values with max cardinality: {}".format(list(filter(lambda x: x['cardinality'] == values[0]['cardinality'], values))))
    for i in range(min(len(values), 20)):
        print(values[i]['value'])
    for i in range(min(len(values), 20)):
        print(values[i]['cardinality'])

    if index_name == index_name_court:
        cities = [{'value': convert_court_name_2_city(x['value']), 'cardinality': x['cardinality']} for x in values]
        new_value_dict = {}
        for city in cities:
            if city['value'] not in new_value_dict:
                new_value_dict[city['value']] = city['cardinality']
            else:
                new_value_dict[city['value']] += city['cardinality']
        new_values = convert_cardinality_dict_2_list(new_value_dict)
        print("Cities")
        for i in range(len(new_values)):
            print(new_values[i]['value'])
        for i in range(len(new_values)):
            print(new_values[i]['cardinality'])
        print(cities)
        print("Cities")

        districts = [{'value': convert_city_name_2_district_name(x['value']), 'cardinality': x['cardinality']} for x in cities]
        print(districts)
        new_value_dict = {}
        for district in districts:
            if district['value'] not in new_value_dict:
                new_value_dict[district['value']] = district['cardinality']
            else:
                new_value_dict[district['value']] += district['cardinality']
        print(new_value_dict)
        new_values = convert_cardinality_dict_2_list(new_value_dict)
        print("Districts")
        for i in range(len(new_values)):
            print(new_values[i]['value'])
        for i in range(len(new_values)):
            print(new_values[i]['cardinality'])
        print(districts)
        print("Districts")
    if index_name == index_name_reference_number:
        print("____________")
        new_value_dict = {}
        for entry in values:
            if entry['cardinality'] not in new_value_dict:
                new_value_dict[entry['cardinality']] = 1
            else:
                new_value_dict[entry['cardinality']] += 1
        new_values = convert_cardinality_dict_2_list(new_value_dict)
        for i in range(len(new_values)):
            print(new_values[i]['value'])
        for i in range(len(new_values)):
            print(new_values[i]['cardinality'])
        print("log")
        for i in range(len(new_values)):
            print(int(round(math.log(new_values[i]['cardinality']), 3) * 1000))
        print("____________")
    if index_name == index_name_date:
        #new_values = list(map(lambda x: datetime.strptime(x['value'], "%d. %m. %Y"), values))
        new_values = []
        for value in values:
            for i in range(value['cardinality']):
                new_values.append(datetime.strptime(value['value'], "%d. %m. %Y"))
        times_only = list(map(lambda x: x.timestamp(), new_values))

        average_time = reduce(add, times_only) / len(times_only)
        modus_time = max(set(times_only), key=times_only.count)
        median_time = median(times_only)

        print("Average is {}".format(average_time))
        print("Modus is {}".format(modus_time))
        print("Median is {}".format(median_time))

        average = datetime.fromtimestamp(average_time)
        modus = datetime.fromtimestamp(modus_time)
        median = datetime.fromtimestamp(median_time)

        print("Average is {}".format(average))
        print("Modus is {}".format(modus))
        print("Median is {}".format(median))
    print("-------------------------------------")



