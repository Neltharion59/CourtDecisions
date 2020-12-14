####################################################################################################################
# This script converts raw text files (created by conversion of pdf to text) to cleared tokenized texts       ######
####################################################################################################################

from os import listdir
from os.path import isfile, join

from os import getcwd
import sys

# Mandatory if we want to run this script from windows cmd. Must precede all imports from this project
conf_path = getcwd()
sys.path.append(conf_path)
sys.path.append(conf_path + '..')
sys.path.append(conf_path + '../..')

# Custom imports from other folders of this project
# All paths to directories within project are held in one play, to be able to change them easily.
from shared_info import file_word_directory, file_txt_directory
# All sorts of util functions are going to be used here.
from Util.tokenizer import clear_string

# Let's retrieve list of ids of all documents in text form on the disk.
all_txt_files_id_list = [f.replace('.txt', '') for f in listdir(file_txt_directory) if isfile(join(file_txt_directory, f))]
# Let's retrieve list of ids of all documents in processed text form on the disk -
# - that have already been processed by this script
all_word_files_id_list = [f.replace('.txt', '') for f in listdir(file_word_directory) if isfile(join(file_word_directory, f))]
# Let's determine which documents need to be processed (were not previously processed).
only_txt_id_list = list(set(all_txt_files_id_list) - set(all_word_files_id_list))

counter = 1
# Let's loop over all file ids that are supposed to be processed.
# Each file will be loaded and processed.
for file_id in only_txt_id_list:
    # Let's output progress to console.
    print("Converting file {}/{} - {:.2%}".format(counter, len(only_txt_id_list), counter/len(only_txt_id_list)))

    # Let's read the file to be processed from disk
    with open(file_txt_directory + '/' + file_id + '.txt', 'r') as text_file:
        text = text_file.read()

    # Let's process the file using our handy util function
    text = clear_string(text)

    # Let's write the processed file to disk
    with open(file_word_directory + '/' + file_id + '.txt', 'w+') as text_file:
        text_file.write(text)

    # Let's output progress to console.
    print("Converted file {}/{} - {:.2%}".format(counter, len(only_txt_id_list), counter/len(only_txt_id_list)))

    # Increase processed file counter
    counter = counter + 1
