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

for file_id in bad_id_list:
    remove(file_directory + "/" + file_id + ".pdf")
