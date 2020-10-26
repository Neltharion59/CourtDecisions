from shared_info import file_txt_directory

file_ids = [1490,4298,4478,6705,7830,11863,13054,13273,8]

for file_id in file_ids:
    try:
        with open(file_txt_directory + "/{}.txt".format(file_id), "r") as file:
            print(file.read())
    except FileNotFoundError:
        pass
