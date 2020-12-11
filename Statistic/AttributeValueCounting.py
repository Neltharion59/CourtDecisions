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
    print("-------------------------------------")



