from os import listdir, remove
from os.path import isfile, join
from shared_info import file_pdf_directory
from crawler_file_paths import file_id_path, file_id_temp_path

perform_remedy = False

filename_dict = {}
with open(file_id_path, "r", encoding='UTF-8') as file_object:
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

print(str(len(ids_to_delete)) + " ids to be deleted")
print(ids_to_delete)
print(duplicity_pairs)

if not perform_remedy:
    exit()

if len(ids_to_delete) > 0:
    file_count = 1
    with open(file_id_path, "r", encoding='UTF-8') as file_object,\
         open(file_id_temp_path, "w+", encoding='UTF-8') as file_object_temp:
        for line in file_object:
            print("Checking file number " + str(file_count))
            file_count = file_count + 1

            tokens = line.replace('\n', '').split(' ')
            file_id = tokens[0]
            if file_id not in ids_to_delete:
                file_object_temp.write(line)

    file_count = 0
    with open(file_id_path, "w+", encoding='UTF-8') as file_object,\
         open(file_id_temp_path, "r", encoding='UTF-8') as file_object_temp:
        for line in file_object_temp:
            file_object.write(line)
            file_count = file_count + 1
            print("Restored file number " + str(file_count))


with open(file_id_temp_path, "w+", encoding='UTF-8') as file_object_temp:
    file_object_temp.write('')

good_id_list = []
file_count = 1
with open(file_id_path, "r", encoding='UTF-8') as file_object:
    for line in file_object:
        tokens = line.replace('\n', '').split(' ')
        file_id = tokens[0]
        good_id_list.append(file_id)

        print("Counting file number " + str(file_count))
        file_count = file_count + 1


all_id_list = [f.replace('.pdf', '') for f in listdir(file_pdf_directory) if isfile(join(file_pdf_directory, f))]
bad_id_list = list(set(all_id_list) - set(good_id_list))
print(bad_id_list)
file_count = 1

for file_id in bad_id_list:
    print("Deleting file number " + str(file_count))
    file_count = file_count + 1

    remove(file_pdf_directory + "/" + file_id + ".pdf")




