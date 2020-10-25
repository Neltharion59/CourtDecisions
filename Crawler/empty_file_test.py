from os import listdir, remove
from os.path import isfile, join, getsize

perform_remedy = False
file_directory = "D:/Rozsudky"
min_size = 40000

all_id_list = [f.replace('.pdf', '') for f in listdir(file_directory) if isfile(join(file_directory, f))]
bad_id_list = []
for file_id in all_id_list:
    if getsize(file_directory + "/" + file_id + ".pdf") < min_size:
        bad_id_list.append(file_id)

print(str(len(bad_id_list)) + " ids to be deleted")
print(bad_id_list)

if not perform_remedy:
    exit()

if len(bad_id_list) > 0:
    file_count = 1
    with open("./file_ids.txt", "r", encoding='UTF-8') as file_object, \
            open("./file_ids_temp.txt", "w+", encoding='UTF-8') as file_object_temp:
        for line in file_object:
            print("Checking file number " + str(file_count))
            file_count = file_count + 1

            tokens = line.replace('\n', '').split(' ')
            file_id = tokens[0]
            if file_id not in bad_id_list:
                file_object_temp.write(line)

    file_count = 0
    with open("./file_ids.txt", "w+", encoding='UTF-8') as file_object, \
            open("./file_ids_temp.txt", "r", encoding='UTF-8') as file_object_temp:
        for line in file_object_temp:
            file_object.write(line)
            file_count = file_count + 1
            print("Restored file number " + str(file_count))

    with open("./file_ids_temp.txt", "w+", encoding='UTF-8') as file_object_temp:
        file_object_temp.write('')

    file_count = 1
    for file_id in bad_id_list:
        print("Deleting file number " + str(file_count))
        file_count = file_count + 1

        remove(file_directory + "/" + file_id + ".pdf")
