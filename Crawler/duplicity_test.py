perform_remedy = True

filename_dict = {}
with open("./file_ids.txt", "r", encoding='UTF-8') as file_object:
    for line in file_object:
        filename = line.split(' ')[1].replace('\n', '')
        if filename not in filename_dict:
            filename_dict[filename] = {
                'ids': [],
                'count': 0
            }
        filename_dict[filename]['count']  = filename_dict[filename]['count'] + 1
        filename_dict[filename]['ids'].append(line.split(' ')[0])

ids_to_delete = []
for key in filename_dict:
    if filename_dict[key]['count'] > 1:
        ids_to_delete = ids_to_delete + filename_dict[key]['ids'][1:]

print(ids_to_delete)


with open("./file_ids_temp.txt", "w+", encoding='UTF-8') as file_object_temp:
    file_object_temp.write('')
if not perform_remedy or len(ids_to_delete) == 0:
    exit()

with open("./file_ids.txt", "r", encoding='UTF-8') as file_object, open("./file_ids_temp.txt", "w+", encoding='UTF-8') as file_object_temp:
    for line in file_object:
        tokens = line.replace('\n', '').split(' ')
        file_id = tokens[0]
        if file_id not in ids_to_delete:
            file_object_temp.write(line)

file_count = 0
with open("./file_ids.txt", "w+", encoding='UTF-8') as file_object, open("./file_ids_temp.txt", "r", encoding='UTF-8') as file_object_temp:
    for line in file_object_temp:
        file_object.write(line)
        file_count = file_count + 1

with open("./count.txt", 'w+') as curr_file:
    curr_file.write(str(file_count))

with open("./file_ids_temp.txt", "w+", encoding='UTF-8') as file_object_temp:
    file_object_temp.write('')


