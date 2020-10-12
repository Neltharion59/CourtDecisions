from os import listdir, remove
from os.path import isfile, join

perform_remedy = False
file_directory = "D:/Rozsudky"

filename_dict = {}
with open("./file_ids.txt", "r", encoding='UTF-8') as file_object:
    for line in file_object:
        file_url = line.split(' ')[2].replace('\n', '')
        if file_url not in filename_dict:
            filename_dict[file_url] = {
                'ids': [],
                'count': 0
            }
        filename_dict[file_url]['count'] = filename_dict[file_url]['count'] + 1
        filename_dict[file_url]['ids'].append(line.split(' ')[0])

ids_to_delete = []
duplicity_pairs = []
for key in filename_dict:
    if filename_dict[key]['count'] > 1:
        ids_to_delete = ids_to_delete + filename_dict[key]['ids'][1:]
        duplicity_pairs.append(filename_dict[key]['ids'])

ids_to_delete = sorted((int(x) for x in ids_to_delete))

print(ids_to_delete)
print(duplicity_pairs)

if not perform_remedy:
    exit()

if len(ids_to_delete) > 0:
    with open("./file_ids.txt", "r", encoding='UTF-8') as file_object,\
         open("./file_ids_temp.txt", "w+", encoding='UTF-8') as file_object_temp:
        for line in file_object:
            tokens = line.replace('\n', '').split(' ')
            file_id = tokens[0]
            if file_id not in ids_to_delete:
                file_object_temp.write(line)

    file_count = 0
    with open("./file_ids.txt", "w+", encoding='UTF-8') as file_object,\
         open("./file_ids_temp.txt", "r", encoding='UTF-8') as file_object_temp:
        for line in file_object_temp:
            file_object.write(line)
            file_count = file_count + 1

    with open("./count.txt", 'w+') as curr_file:
        curr_file.write(str(file_count))

with open("./file_ids_temp.txt", "w+", encoding='UTF-8') as file_object_temp:
    file_object_temp.write('')

good_id_list = []
with open("./file_ids.txt", "r", encoding='UTF-8') as file_object:
    for line in file_object:
        tokens = line.replace('\n', '').split(' ')
        file_id = tokens[0]
        good_id_list.append(file_id)


all_id_list = [f.replace('.pdf', '') for f in listdir(file_directory) if isfile(join(file_directory, f))]
bad_id_list = list(set(all_id_list) - set(good_id_list))
for file_id in bad_id_list:
    remove(file_directory + "/" + file_id + ".pdf")




