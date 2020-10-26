from os import listdir
from os.path import isfile, join
from shared_info import file_word_directory, index_directory
from Util.tokenizer import tokenize_string
from Util.dict_util import split_dict_abc, single_letter_dict_2_string


def create_attribute_index(index_name):
    index_file_path_template = "{}/index_{}_letter_{}.txt".format(index_directory, index_name, '{}')

    all_id_list = [f.replace('.txt', '') for f in listdir(file_word_directory) if isfile(join(file_word_directory, f))]

    existing_id_list = []

    new_id_list = list(set(all_id_list) - set(existing_id_list))

    i = 1
    for file_id in new_id_list:
        print('Processing file {}/{} - {:.2%}'.format(i, len(new_id_list), i/len(new_id_list)))

        with open(file_word_directory + "/{}.txt".format(file_id), "r") as file:
            text = file.read()

        tokens = tokenize_string(text)
        word_dict = {}
        index = 0
        for index in range(len(tokens)):
            if tokens[index] not in word_dict:
                word_dict[tokens[index]] = []
            word_dict[tokens[index]].append(index)

        i = i + 1

        write_into_index_file(file_id, word_dict, index_file_path_template)


def write_into_index_file(indexed_file_id, indexed_value, index_file_path_template):
    split_dict = split_dict_abc(indexed_value, indexed_file_id)

    for key in split_dict:
        split_dict[key] = single_letter_dict_2_string(split_dict[key])

    for letter in split_dict:
        index_file_path = index_file_path_template.format(letter)
        with open(index_file_path, 'w+', encoding='utf-8') as file:
            file.write(split_dict[letter])

    exit()
    contents = []
    try:
        f = open(index_file_path, "r", encoding='utf-8')
        contents = f.read().splitlines()
        f.close()
    except FileNotFoundError:
        pass

    f = open(index_file_path, "w+", encoding='utf-8')
    contents = "\n".join(contents)
    f.write(contents)
    f.close()

