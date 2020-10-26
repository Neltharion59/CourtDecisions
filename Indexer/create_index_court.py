from os import listdir
from os.path import isfile, join
import re

from shared_info import file_directory, index_directory

index_file_path = "./../Resources/Indexes/index_courts.txt"
blacklist_file_path = "Blacklists/blacklist_index_courts.txt"


def write_into_index_file(indexed_file_id, indexed_value):
    contents = []
    try:
        f = open(index_file_path, "r", encoding='utf-8')
        contents = f.read().splitlines()
        f.close()
    except FileNotFoundError:
        pass

    values = [x.split(':')[0] for x in contents]
    try:
        value_index = values.index(indexed_value)
        id_list = [int(y) for y in contents[value_index].split(':')[1].split(',')]
        id_list.append(int(indexed_file_id))
        id_list.sort()

        contents[value_index] = contents[value_index].split(':')[0] + ":" + ",".join([str(x) for x in id_list])
    except ValueError:
        contents.append(indexed_value + ":" + indexed_file_id)
        pass

    f = open(index_file_path, "w+", encoding='utf-8')
    contents = "\n".join(contents)
    f.write(contents)
    f.close()
    pass


attribute_regex = "(.*súd.*)[\na-zA-Z\/0-9]*Súd\:\n"

all_id_list = [f.replace('.txt', '') for f in listdir(file_directory) if isfile(join(file_directory, f))]

existing_id_list = []
try:
    f = open(index_file_path, "r", encoding='utf-8')
    for line in f:
        existing_id_list = existing_id_list + line.split(':')[1].split(',')
    f.close()
except FileNotFoundError:
    pass

new_id_list = list(set(all_id_list) - set(existing_id_list))
blacklist_ids = []
with open(blacklist_file_path, "r") as file:
    for line in file:
        blacklist_ids.append(line.replace("\n", ""))

new_id_list = list(set(new_id_list) - set(blacklist_ids))

i = 1
text = ""
for file_id in new_id_list:
    print('Processing file {}/{} - {:.2%}'.format(i, len(new_id_list), i/len(new_id_list)))

    with open(file_directory + "/" + file_id + ".txt", "r") as file:
        text = file.read()

    matches = re.findall(attribute_regex, text)

    if len(matches) != 1:
        with open(blacklist_file_path, "a+") as file:
            file.write(file_id + "\n")
        continue

    match = matches[0]
    write_into_index_file(file_id, match)

    i = i + 1
