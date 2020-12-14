####################################################################################################################
# This script contains helpful algorithms for deleting files. Should not be called as stand-alone             ######
####################################################################################################################

from os import listdir, remove
from os.path import isfile, join

# Custom imports from other folders of this project
# All paths to directories within project are held in one play, to be able to change them easily.
from shared_info import file_pdf_directory, file_txt_directory, file_id_path, file_id_temp_path


# Function to delete pdf document and its textual versions
def delete_pdf_and_txt_files(ids_to_delete):
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

        try:
            remove(file_pdf_directory + "/" + file_id + ".pdf")
        except FileNotFoundError:
            pass
        try:
            remove(file_txt_directory + "/" + file_id + ".txt")
        except FileNotFoundError:
            pass
