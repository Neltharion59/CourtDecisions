from shared_info import file_txt_directory

file_ids = [4478,
12694,
5932,
10264,
6705]

for file_id in file_ids:
    try:
        with open(file_txt_directory + "/{}.txt".format(file_id), "r") as file:
            print(file.read())
    except FileNotFoundError:
        pass
