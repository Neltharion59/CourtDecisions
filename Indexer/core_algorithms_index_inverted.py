####################################################################################################################
# This script contains core algorithms for creating inverted index. Should not be called as stand-alone       ######
####################################################################################################################

from os import listdir
from os.path import isfile, join
import re

# Custom imports from other folders of this project
# All paths to directories within project are held in one play, to be able to change them easily.
from shared_info import file_txt_directory, index_directory


# Function for storing given value for given pdf file into given index file
# Is called from another function below
# Otherwise there is probably no use case for calling it from anywhere else
def write_into_index_file(indexed_file_id, indexed_value, index_file_path, sort_lambda, reverse_order):
    # First, let's see if the index file already exists. If it does, new info should me merged to it
    # If it doesn't, it's really easy - we just create it
    contents = []
    try:
        f = open(index_file_path, "r", encoding='utf-8')
        contents = f.read().splitlines()
        f.close()
    except FileNotFoundError:
        pass

    values = [x.split(':')[0] for x in contents]
    # Let's assume that the value we are trying to index already has some files associated with it.
    # If it doesn't, we'll have an exception and handle it in 'catch' block below
    try:
        # Let's find the value we are trying to index
        value_index = values.index(indexed_value)
        # For the value we are trying to index, create list of ids of ducument associated with it
        id_list = [int(y) for y in contents[value_index].split(':')[1].split(',')]
        # Append the new id to this list
        id_list.append(int(indexed_file_id))
        # Sort the list of ids for better readability of the index file
        id_list.sort()
        # Modify the line we added the id to
        contents[value_index] = contents[value_index].split(':')[0] + ":" + ",".join([str(x) for x in id_list])
    except ValueError:
        # If we are here, the value is new, so we must create new entry
        contents.append(indexed_value + ":" + indexed_file_id)
        pass

    # Let's sort the lines of file by indexed values
    # Sometimes custom ordering key is passed in as parameter, so we may or may not use it
    if not sort_lambda:
        contents.sort(reverse=reverse_order)
    else:
        contents.sort(key=sort_lambda, reverse=reverse_order)

    # We have modified the file content in transient way, let's write the modified content to disk now
    f = open(index_file_path, "w+", encoding='utf-8')
    contents = "\n".join(contents)
    f.write(contents)
    f.close()


# This is the function to be called to create arbitrary inverse index
# You need to specify
# param index_name:         str         How to name the index - will affect name of index file
# param attribute_regex:    str         Regex to find value of the attribute in pdf files
# param ignore_blacklist:   bool        Whether or not try to index files from blacklist of this attribute
#                                       (if previous indexing attempts failed for some files)
# param regex_group_index:  list of int List of indexes into rexeg matching result, where value of this attribute
#                                       will be looked for in each pdf file. The indexes are checked in order as they
#                                       appear in list. First existing non-empty index will be considered desired value.
# opt param sort_lambda:        lamda   Function to sort index file lines by. Is not mandatory to specify.
# opt param reverse_order:      bool    Whether to order index file lines in reverse order. Is not mandatory to specify
def create_attribute_index(index_name, attribute_regex, ignore_blacklist=True, regex_group_index=[0], sort_lambda=None, reverse_order=False):
    # Let's prepare paths to index file and to blacklist file for this attribute.
    index_file_path = "{}/index_{}.txt".format(index_directory, index_name)
    blacklist_file_path = "Blacklists/blacklist_index_{}.txt".format(index_name)

    # Let's retrieve list of ids of all documents on the disk.
    all_id_list = [f.replace('.txt', '') for f in listdir(file_txt_directory) if isfile(join(file_txt_directory, f))]

    # Let's retrieve list of all document ids that have been previously indexed by this index,
    # so that we do not try to index them again.
    existing_id_list = []
    try:
        f = open(index_file_path, "r", encoding='utf-8')
        for line in f:
            existing_id_list = existing_id_list + line.replace("\n", "").split(':')[1].split(',')
        f.close()
    except FileNotFoundError:
        pass

    # Let's determine which documents need to be indexed (were not previously indexed).
    new_id_list = list(set(all_id_list) - set(existing_id_list))

    # If we are supposed to ignore ids from blacklist-the ones that were previously attempted to index, but it failed-,
    # let's remove them from list of files that are supposed to be indexed.
    if ignore_blacklist:
        try:
            with open(blacklist_file_path, "r") as file:
                blacklist_ids = []
                for line in file:
                    blacklist_ids.append(line.replace("\n", ""))
            new_id_list = list(set(new_id_list) - set(blacklist_ids))
        except FileNotFoundError:
            pass

    i = 1
    text = ""
    # Let's loop over all file ids that are supposed to be indexed.
    # Each file will be loaded and searched by specified regex.
    # If match is found, file will be indexed, otherwise its id will be added to blacklist.
    for file_id in new_id_list:
        # Let's output progress to console.
        print('Processing file {}/{} - {:.2%}'.format(i, len(new_id_list), i/len(new_id_list)))

        # Let's read content of pdf file (from its txt form)
        with open(file_txt_directory + "/" + file_id + ".txt", "r") as file:
            text = file.read()

        # Let's try to match the regex
        regex = re.compile(attribute_regex, re.MULTILINE)
        matches = regex.findall(text)

        # Increase processed file counter
        i = i + 1

        # Let's check if there are any matches
        # If there are none, add the file id to blacklist, and move on to the next file
        if len(matches) <= 0:
            with open(blacklist_file_path, "a+") as file:
                file.write(file_id + "\n")
            continue
        # If there are matches, let's proceed them further
        if len(matches) > 1:
            matches = list(matches[0])

        match = matches[0]
        # Let's try to find the desired value in specified group indexes of the match.
        # They are specified by this function's parameter.
        if type(match) is tuple:
            for index in regex_group_index:
                if len(match[index]) > 0:
                    match = match[index]
                    break
            if type(match) is tuple:
                match = ""

        # Now we have the value for this documents, so let's write it to disk using the function above.
        write_into_index_file(file_id, match, index_file_path, sort_lambda, reverse_order)
