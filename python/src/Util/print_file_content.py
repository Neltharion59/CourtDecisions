####################################################################################################################
# This script prints content of a few random files for testing purposes.                                      ######
####################################################################################################################

from os import getcwd
import sys

# Mandatory if we want to run this script from windows cmd. Must precede all imports from this project
conf_path = getcwd()
sys.path.append(conf_path)
sys.path.append(conf_path + '..')
sys.path.append(conf_path + '../..')

# Custom imports from other folders of this project
# All paths to directories within project are held in one play, to be able to change them easily.
from shared_info import file_word_directory

# Let's generate list of file ids.
file_ids = range(30)

# Let's loop over all file ids and print content of corresponding documents to console.
for file_id in file_ids:
    try:
        with open(file_word_directory + "/{}.txt".format(file_id), "r") as file:
            print(file.read())
    except FileNotFoundError:
        pass
