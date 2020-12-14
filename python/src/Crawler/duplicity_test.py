####################################################################################################################
# This script is duplicity tester. Ideally, should be ran after crawling session(s) before any further processing ##
# Probably not necessary, this test was needed especially with first versions of crawler before bugs were fixed   ##
####################################################################################################################

from os import getcwd
import sys

# Mandatory if we want to run this script from windows cmd. Must precede all imports from this project
conf_path = getcwd()
sys.path.append(conf_path)
sys.path.append(conf_path + '..')
sys.path.append(conf_path + '../..')

# Custom imports from other folders of this project
# Utility folder has scripts for dealing with common tasks, such as deleting pdf files from disk in this case
from Util.file_deleting import delete_pdf_and_txt_files
# All paths to directories within project are held in one play, to be able to change them easily.
from shared_info import file_id_path

# Important parameter. If set True, will physically remove the files from the disk, otherwise it will just print
# duplicates in console.
perform_remedy = False

# Set up the dictionary of existing URLs
filename_dict = {}
# All the file ids and their URLs are store in a text file.
with open(file_id_path, "r", encoding='UTF-8') as file_object:
    # Loop over all file records
    for line in file_object:
        # Retrieve current file's URL
        file_url = line.split(' ')[2].replace('\n', '')
        # If the URL is not in dictionary yet, let's create new entry
        if file_url not in filename_dict:
            filename_dict[file_url] = {
                'ids': [],
                'count': 0
            }
        # Record the file in dictionary
        filename_dict[file_url]['count'] = filename_dict[file_url]['count'] + 1 # Increase number of files with this id
        filename_dict[file_url]['ids'].append(line.split(' ')[0])               # Store id of current file

# Set up helpful variables
ids_to_delete = []      # This will hold ids of all files that need to be deleted
duplicity_pairs = []    # This will hold all tupples of files that are duplicit

# Let's loop over all URLs in helpful dict
for key in filename_dict:
    # If there are more files than one with this URL, let's delete (add to list of files to be deleted)
    # all except the first one of them
    if filename_dict[key]['count'] > 1:
        ids_to_delete = ids_to_delete + filename_dict[key]['ids'][1:]
        duplicity_pairs.append(filename_dict[key]['ids'])

# Print the results to console
print(str(len(ids_to_delete)) + " ids to be deleted")
print(ids_to_delete)
print(duplicity_pairs)

# If we aren't supposed to remove duplicate files from the disk, let's quit now
if not perform_remedy:
    exit()

# If we haven't quit yet, it means we are supposed to delete files from disk. Let's do it using our utility function
# designed for this special occasion
delete_pdf_and_txt_files(ids_to_delete)
