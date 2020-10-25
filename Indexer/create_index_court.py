from os import listdir, remove
from os.path import isfile, join, getsize

from shared_info import file_directory, index_directory

index_file_name = "index_courts"

all_id_list = [f.replace('.pdf', '') for f in listdir(file_directory) if isfile(join(file_directory, f))]

