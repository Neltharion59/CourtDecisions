from os import listdir, remove
from os.path import isfile, join, getsize
from shared_info import file_pdf_directory
from Util.file_deleting import delete_pdf_and_txt_files

perform_remedy = True
min_size = 40000

all_id_list = [f.replace('.pdf', '') for f in listdir(file_pdf_directory) if isfile(join(file_pdf_directory, f))]
bad_id_list = []
for file_id in all_id_list:
    if getsize(file_pdf_directory + "/" + file_id + ".pdf") < min_size:
        bad_id_list.append(file_id)

print(str(len(bad_id_list)) + " ids to be deleted")
print(bad_id_list)

if not perform_remedy:
    exit()

delete_pdf_and_txt_files(bad_id_list)
