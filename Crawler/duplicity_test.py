from os import listdir, remove
from os.path import isfile, join
from shared_info import file_pdf_directory
from Util.file_deleting import delete_pdf_and_txt_files
from shared_info import file_id_path


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

delete_pdf_and_txt_files(ids_to_delete)
