####################################################################################################################
# This script creates description index for all files indexed by inverse indexers                             ######
# Description index is a separate file for each document, where values of all attributes of that document are ######
# Description index is useful when retrieving info of a document we only know id of.                          ######
####################################################################################################################

from os import listdir, makedirs
from os.path import isfile, join

# Custom imports from other folders of this project
# All paths to directories within project are held in one play, to be able to change them easily.
from shared_info import file_description_directory, file_pdf_directory, index_directory
# Index names are stored at corresponding indexers, so that they are unified across the project
from Indexer.create_index_court import index_name as index_name_court
from Indexer.create_index_date import index_name as index_name_date
from Indexer.create_index_id_number import index_name as index_name_id_number
from Indexer.create_index_judge import index_name as index_name_judge
from Indexer.create_index_reference_number import index_name as index_name_reference_number

# If the directory for description index does not exist, let's create it
makedirs(file_description_directory, exist_ok=True)
# Let's output progress to console.
print('Loading file ids')

# Let's retrieve list of ids of all documents in pdf form on the disk.
all_id_list = [f.replace('.pdf', '') for f in listdir(file_pdf_directory) if isfile(join(file_pdf_directory, f))]
# Let's retrieve list of ids of all documents already processed by this script on the disk.
existing_id_list = [f.replace('.txt', '') for f in listdir(file_description_directory) if isfile(join(file_description_directory, f))]
# Let's determine which documents need to be processed (were not previously processed).
new_id_list = list(set(all_id_list) - set(existing_id_list))
# Let's output progress to console.
print('Loaded file ids. {}/{} - {:.2%} - are already processed. Need to index {} more.'
      .format(len(existing_id_list), len(all_id_list), len(existing_id_list)/len(all_id_list), len(new_id_list)))

# If there are no ids to be processed, let's quit.
# This code is nicer than wrapping the rest of this script to 'if' block.
if len(new_id_list) <= 0:
    print("No ids to process. Finishing job.")
    exit()

# Let's prepare list of names of all existing inverse indexes.
inverted_index_names = [index_name_court, index_name_date, index_name_id_number, index_name_judge, index_name_reference_number]

# Each document will be represented as dictionary of pairs  attribute_name  -   attribute_value
# These documents are stored in dictionary of pairs         document_id     -   document_attribute_dict
output_dict = {}
for file_id in new_id_list:
    output_dict[file_id] = {}

# Let's loop over all existing inverted indexes.
# For each index, we will retrieve attribute value of all indexed documents and store them in corresponding dictionaries
for inverted_index_name in inverted_index_names:
    # Let's output progress to console.
    print("Processing " + inverted_index_name + " index.")

    # Let's prepare index file path to be read from
    file_name = index_directory + "/index_" + inverted_index_name + ".txt"
    try:
        # Let's read the index file.
        with open(file_name, 'r', encoding='utf-8') as index_file:
            # Let's output progress to console.
            print("Index file found and loaded.")
            i = 1
            # Let's read all lines of the index file.
            lines = index_file.readlines()
            # Let's loop over all the lines of index file.
            for line in lines:
                # Let's remove useless artifacts from the line.
                line = line.replace('\n', '')
                # Let's output progress to console.
                print("Procesing {} index line {}/{}".format(inverted_index_name, i, len(lines)))
                # Let's retrieve attribute value and all document ids that have it from the line.
                value = line.split(':')[0]
                ids = line.split(':')[1].split(',')
                # Let's store the retrieved info into dictionaries
                for file_id in ids:
                    if file_id not in output_dict:
                        continue
                    output_dict[file_id][inverted_index_name] = value
                # Increase processed file counter
                i = i + 1
    except FileNotFoundError:
        # Let's output problem to console. We cannot do anything better if index file does not exist.
        print("Index " + file_name + " does not exist")

# Let's loop over all document ids in the dictionary.
for file_id in output_dict:
    # Let's prepare index file path to write into.
    output_file_name = file_description_directory + "/" + file_id + ".txt"
    # Let's write info of this document to disk.
    with open(output_file_name, 'w+', encoding='utf-8') as output_file:
        # Let's loop over all attribute values in this document's dictionary.
        for attribute in output_dict[file_id]:
            # Write attribute value to index file of this document to disk.
            output_file.write("{}:{}\n".format(attribute, output_dict[file_id][attribute]))
