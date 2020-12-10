from os import listdir, makedirs
from os.path import isfile, join
import re
from shared_info import file_description_directory, file_pdf_directory, index_directory
from Indexer.create_index_court import index_name as index_name_court
from Indexer.create_index_date import index_name as index_name_date
from Indexer.create_index_id_number import index_name as index_name_id_number
from Indexer.create_index_judge import index_name as index_name_judge
from Indexer.create_index_reference_number import index_name as index_name_reference_number
from Util.tokenizer import all_lowercase_chars

makedirs(file_description_directory, exist_ok=True)
print('Loading file ids')
all_id_list = [f.replace('.pdf', '') for f in listdir(file_pdf_directory) if isfile(join(file_pdf_directory, f))]
existing_id_list = [f.replace('.txt', '') for f in listdir(file_description_directory) if isfile(join(file_description_directory, f))]
new_id_list = list(set(all_id_list) - set(existing_id_list))
print('Loaded file ids. {}/{} - {:.2%} - are already processed. Need to index {} more.'
      .format(len(existing_id_list), len(all_id_list), len(existing_id_list)/len(all_id_list), len(new_id_list)))

if len(new_id_list) <= 0:
    print("No ids to process. Finishing job.")
    exit()

inverted_index_names = [index_name_court, index_name_date, index_name_id_number, index_name_judge, index_name_reference_number]
word_index_suffixes = list(all_lowercase_chars) + ["misc"]

output_dict = {}
for file_id in new_id_list:
    output_dict[file_id] = {}

for inverted_index_name in inverted_index_names:
    print("Processing " + inverted_index_name + " index.")
    file_name = index_directory + "/index_" + inverted_index_name + ".txt"
    try:
        with open(file_name, 'r', encoding='utf-8') as index_file:
            print("Index file found and loaded.")
            i = 1
            lines = index_file.readlines()
            for line in lines:
                line = line.replace('\n', '')
                print("Procesing {} index line {}/{}".format(inverted_index_name, i, len(lines)))
                value = line.split(':')[0]
                ids = line.split(':')[1].split(',')
                for file_id in ids:
                    if file_id not in output_dict:
                        continue
                    output_dict[file_id][inverted_index_name] = value
                i = i + 1
    except FileNotFoundError:
        print("Index " + file_name + " does not exist")

for file_id in output_dict:
    output_file_name = file_description_directory + "/" + file_id + ".txt"
    with open(output_file_name, 'w+', encoding='utf-8') as output_file:
        for attribute in output_dict[file_id]:
            output_file.write("{}:{}\n".format(attribute, output_dict[file_id][attribute]))
