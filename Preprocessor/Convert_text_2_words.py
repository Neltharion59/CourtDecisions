from os import listdir
from os.path import isfile, join

from shared_info import file_word_directory, file_txt_directory
from Util.tokenizer import clear_string

all_txt_files_id_list = [f.replace('.txt', '') for f in listdir(file_txt_directory) if isfile(join(file_txt_directory, f))]
all_word_files_id_list = [f.replace('.txt', '') for f in listdir(file_word_directory) if isfile(join(file_word_directory, f))]
only_txt_id_list = list(set(all_txt_files_id_list) - set(all_word_files_id_list))

counter = 1
for file_id in only_txt_id_list:
    print("Converting file {}/{} - {:.2%}".format(counter, len(only_txt_id_list), counter/len(only_txt_id_list)))

    with open(file_txt_directory + '/' + file_id + '.txt', 'r') as text_file:
        text = text_file.read()

    text = clear_string(text)

    with open(file_word_directory + '/' + file_id + '.txt', 'w+') as text_file:
        text_file.write(text)

    print("Converted file {}/{} - {:.2%}".format(counter, len(only_txt_id_list), counter/len(only_txt_id_list)))
    counter = counter + 1
