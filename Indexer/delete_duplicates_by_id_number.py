from create_index_id_number import index_name
from Util.file_deleting import delete_pdf_and_txt_files
from shared_info import index_directory

perform_remedy = True

bad_ids = []
lines = []
with open(index_directory + "/index_{}.txt".format(index_name), "r") as file:
    for line in file:
        ids = line.replace("\n", "").split(":")[1].split(",")
        if len(ids) <= 1:
            lines.append(line.replace("\n", ""))
            continue
        else:
            bad_ids = bad_ids + ids[1:]
            lines.append(line.split(":")[0] + ":" + ids[0])

print(len(bad_ids))
print(bad_ids)

if not perform_remedy:
    exit()

delete_pdf_and_txt_files(bad_ids)
with open(index_directory + "/index_{}.txt".format(index_name), "w+") as file:
    for line in lines:
        file.write(line + "\n")
