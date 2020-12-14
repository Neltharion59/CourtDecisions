####################################################################################################################
# This script contains core algorithms for creating positional index. Should not be called as stand-alone     ######
####################################################################################################################

from os import listdir
from os.path import isfile, join

# Custom imports from other folders of this project
# All paths to directories within project are held in one play, to be able to change them easily.
from shared_info import file_word_directory, index_directory
# All sorts of dictionaries and util functions are going to be used here.
from Util.tokenizer import tokenize_string, all_lowercase_chars
from Util.dict_util import split_dict_abc, single_letter_dict_2_string, single_letter_string_2_dict, merge_single_letter_dicts


# This is the function to be called to create positional index
# param index_name:         str     How to name the index - will affect name of index file
def create_attribute_index(index_name):
    # Let's prepare path to index file for this attribute.
    index_file_path_template = "{}/index_{}_letter_{}.txt".format(index_directory, index_name, '{}')

    # Let's retrieve list of ids of all documents on the disk.
    all_id_list = [f.replace('.txt', '') for f in listdir(file_word_directory) if isfile(join(file_word_directory, f))]

    existing_id_list = []
    # This time, index is split into multiple files - based on first letter of indexed word.
    # We also have 'misc' file for weird malformations.
    index_names = list(all_lowercase_chars) + ["misc"]
    # Let's loop over all existing index files for this index to retrieve ids of all documents
    # that have already been indexed for this index.
    for index_name in index_names:
        index_file_path = index_file_path_template.format(index_name)
        try:
            with open(index_file_path, "r", encoding='utf-8') as file:
                for line in file:
                    if ':' in line:
                        existing_id_list.append(line.split(":")[0])
        except FileNotFoundError:
            pass

    # Let's determine which documents need to be indexed (were not previously indexed).
    new_id_list = list(set(all_id_list) - set(existing_id_list))

    i = 1
    # Let's loop over all file ids that are supposed to be indexed.
    # Each file will be loaded and searched by specified regex.
    # If match is found, file will be indexed, otherwise its id will be added to blacklist.
    for file_id in new_id_list:
        # Let's output progress to console.
        print('Processing file {}/{} - {:.2%}'.format(i, len(new_id_list), i/len(new_id_list)))

        # Let's read content of pdf file (from its tokenized txt form)
        with open(file_word_directory + "/{}.txt".format(file_id), "r") as file:
            text = file.read()

        # Let's split the content of the file to list of words
        tokens = tokenize_string(text)
        # We shall create dictionary for this document, where keys are words and values are lists of indices
        # at which the given word is located within the document.
        word_dict = {}
        # Let's loop over the list of words and fill this dictionary.
        for index in range(len(tokens)):
            if tokens[index] not in word_dict:
                word_dict[tokens[index]] = []
            word_dict[tokens[index]].append(index)

        # Increase processed file counter
        i = i + 1

        # Now we have the value for this documents, so let's write it to disk using the function below.
        write_into_index_file(file_id, word_dict, index_file_path_template)


# Function for storing given value for given pdf file into given index file
# Is called from another function below
# Otherwise there is probably no use case for calling it from anywhere else
def write_into_index_file(indexed_file_id, indexed_value, index_file_path_template):
    # Let's group the dictionary of words and their occurences by starting letters - that will tell which index file
    # they belong to. We have nice utility function to do so.
    split_dict = split_dict_abc(indexed_value, indexed_file_id)

    # Let's loop over all letters in the grouped dictionary.
    # For each letter, we will open corresponding index file(if exists),
    # write the document info into it, and save it to disk.
    for letter in split_dict:
        # Let's prepare the path to index file
        index_file_path = index_file_path_template.format(letter)

        # If the index file already exists, let's read it
        contents = ""
        try:
            f = open(index_file_path, "r", encoding='utf-8')
            contents = f.read()
            f.close()
        except FileNotFoundError:
            pass

        # Let's merge dictionary of all already indexed files with dictionary of currently indexed file

        # Let's turn content of existing index file to dictionary
        letter_dict = single_letter_string_2_dict(contents)
        # Merge existing dictionary with current file's dictionary
        letter_dict = merge_single_letter_dicts(letter_dict, split_dict[letter])
        # Let's turn the merged dictionary to string that will be written to index file
        letter_dict_text = single_letter_dict_2_string(letter_dict)
        # Let's write the string into index file
        with open(index_file_path, 'w+', encoding='utf-8') as file:
            file.write(letter_dict_text)
