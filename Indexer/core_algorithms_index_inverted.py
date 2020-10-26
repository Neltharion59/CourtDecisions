from os import listdir
from os.path import isfile, join
import re
from shared_info import file_txt_directory, index_directory


def write_into_index_file(indexed_file_id, indexed_value, index_file_path, sort_lambda, reverse_order):
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

    if not sort_lambda:
        contents.sort(reverse=reverse_order)
    else:
        contents.sort(key=sort_lambda, reverse=reverse_order)

    f = open(index_file_path, "w+", encoding='utf-8')
    contents = "\n".join(contents)
    f.write(contents)
    f.close()


def create_attribute_index(index_name, attribute_regex, ignore_blacklist=True, regex_group_index=[0], sort_lambda=None, reverse_order=False):
    index_file_path = "./../Resources/Indexes/index_{}.txt".format(index_name)
    blacklist_file_path = "Blacklists/blacklist_index_{}.txt".format(index_name)

    all_id_list = [f.replace('.txt', '') for f in listdir(file_txt_directory) if isfile(join(file_txt_directory, f))]

    existing_id_list = []
    try:
        f = open(index_file_path, "r", encoding='utf-8')
        for line in f:
            existing_id_list = existing_id_list + line.replace("\n", "").split(':')[1].split(',')
        f.close()
    except FileNotFoundError:
        pass

    new_id_list = list(set(all_id_list) - set(existing_id_list))

    if ignore_blacklist:
        try:
            with open(blacklist_file_path, "r") as file:
                blacklist_ids = []
                for line in file:
                    blacklist_ids.append(line.replace("\n", ""))
            new_id_list = list(set(new_id_list) - set(blacklist_ids))
        except FileNotFoundError:
            pass

    i = 1
    text = ""
    for file_id in new_id_list:
        print('Processing file {}/{} - {:.2%}'.format(i, len(new_id_list), i/len(new_id_list)))

        with open(file_txt_directory + "/" + file_id + ".txt", "r") as file:
            text = file.read()

        regex = re.compile(attribute_regex, re.MULTILINE)
        matches = regex.findall(text)

        i = i + 1
        if len(matches) <= 0:
            with open(blacklist_file_path, "a+") as file:
                file.write(file_id + "\n")
            continue
        if len(matches) > 1:
            matches = list(matches[0])

        match = matches[0]
        if type(match) is tuple:
            for index in regex_group_index:
                if len(match[index]) > 0:
                    match = match[index]
                    break
            if type(match) is tuple:
                match = ""

        write_into_index_file(file_id, match, index_file_path, sort_lambda, reverse_order)


