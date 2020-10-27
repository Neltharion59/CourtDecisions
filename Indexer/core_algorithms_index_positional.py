from os import listdir
from os.path import isfile, join
from shared_info import file_word_directory, index_directory
from Util.tokenizer import tokenize_string, all_lowercase_chars
from Util.dict_util import split_dict_abc, single_letter_dict_2_string, single_letter_string_2_dict, merge_single_letter_dicts


def create_attribute_index(index_name):
    index_file_path_template = "{}/index_{}_letter_{}.txt".format(index_directory, index_name, '{}')

    all_id_list = [f.replace('.txt', '') for f in listdir(file_word_directory) if isfile(join(file_word_directory, f))]

    existing_id_list = []
    index_names = list(all_lowercase_chars) + ["misc"]
    for index_name in index_names:
        index_file_path = index_file_path_template.format(index_name)
        try:
            with open(index_file_path, "r", encoding='utf-8') as file:
                for line in file:
                    if ':' in line:
                        existing_id_list.append(line.split(":")[0])
        except FileNotFoundError:
            pass
    new_id_list = list(set(all_id_list) - set(existing_id_list))

    i = 1
    for file_id in new_id_list:
        print('Processing file {}/{} - {:.2%}'.format(i, len(new_id_list), i/len(new_id_list)))

        with open(file_word_directory + "/{}.txt".format(file_id), "r") as file:
            text = file.read()

        tokens = tokenize_string(text)
        word_dict = {}
        for index in range(len(tokens)):
            if tokens[index] not in word_dict:
                word_dict[tokens[index]] = []
            word_dict[tokens[index]].append(index)

        i = i + 1

        write_into_index_file(file_id, word_dict, index_file_path_template)


def write_into_index_file(indexed_file_id, indexed_value, index_file_path_template):
    split_dict = split_dict_abc(indexed_value, indexed_file_id)

    for letter in split_dict:
        index_file_path = index_file_path_template.format(letter)

        contents = ""
        try:
            f = open(index_file_path, "r", encoding='utf-8')
            contents = f.read()
            f.close()
        except FileNotFoundError:
            pass

        letter_dict = single_letter_string_2_dict(contents)
        letter_dict = merge_single_letter_dicts(letter_dict, split_dict[letter])
        letter_dict_text = single_letter_dict_2_string(letter_dict)

        with open(index_file_path, 'w+', encoding='utf-8') as file:
            file.write(letter_dict_text)
