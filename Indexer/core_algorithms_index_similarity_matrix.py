from os import listdir
from os.path import isfile, join
from shared_info import file_word_directory, index_directory
from Util.tokenizer import tokenize_string, all_lowercase_chars
from Util.dict_util import split_dict_abc, single_letter_dict_2_string, single_letter_string_2_dict, merge_single_letter_dicts


def create_attribute_index(index_name):
    index_file_path_template = "{}/index_{}.txt".format(index_directory, index_name)
    words_index_file_path_template = "{}/index_words_letter_{}.txt".format(index_directory, '{}')

    all_word_list = []
    index_names = list(all_lowercase_chars) + ["misc"]
    for letter in index_names:
        try:
            with open(words_index_file_path_template.format(letter), "r", encoding='utf-8') as f:
                for line in f:
                    if line.replace('\n', '') == '$' or ':' in line:
                        continue
                    else:
                        all_word_list.append(line.replace('\n', ''))
        except FileNotFoundError:
            pass

    print(len(all_word_list))
    print(all_word_list)
    exit()

    i = 1
    for file_id in new_id_list:
        print('Processing file {}/{} - {:.2%}'.format(i, len(new_id_list), i/len(new_id_list)))

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
