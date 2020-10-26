from shared_info import file_txt_directory

file_ids = [1763, 10996, 11005, 12123]

for file_id in file_ids:
    with open(file_txt_directory + "/{}.txt".format(file_id), "r") as file:
        print(file.read())
