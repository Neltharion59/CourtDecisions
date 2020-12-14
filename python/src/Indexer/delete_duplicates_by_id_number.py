####################################################################################################################
# This script removes all duplicate files based on identification number. Can only be done after indexing.    ######
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
from shared_info import index_directory
# Index names are stored at corresponding indexers, so that they are unified across the project
from Indexer.create_index_id_number import index_name
# All sorts of util functions are going to be used here.
from Util.file_deleting import delete_pdf_and_txt_files

# Important parameter. If set True, will physically remove the files from the disk, otherwise it will just print
# ids of files that sould be deleted in console.
perform_remedy = True

bad_ids = []
lines = []
# Let's open the index file of identification number index.
with open(index_directory + "/index_{}.txt".format(index_name), "r") as file:
    # Let's loop over lines of the index file
    for line in file:
        # Let's retrieve list of ids with given identification number
        ids = line.replace("\n", "").split(":")[1].split(",")
        # If there is only 1 id, it's okay and we may proceed to next line
        if len(ids) <= 1:
            lines.append(line.replace("\n", ""))
            continue
        # If there are more ids, let's consider all but the first one duplicates and add their ids to list of bad ids.
        else:
            bad_ids = bad_ids + ids[1:]
            lines.append(line.split(":")[0] + ":" + ids[0])

# Let's output progress to console.
print(len(bad_ids))
print(bad_ids)

# If we aren't supposed to remove duplicate files from the disk, let's quit now
if not perform_remedy:
    exit()

# If we haven't quit yet, it means we are supposed to delete files from disk. Let's do it using our utility function
# designed for this special occasion
delete_pdf_and_txt_files(bad_ids)

# Let's overwrite the index file so that duplicate files aren't indexed anymore.
with open(index_directory + "/index_{}.txt".format(index_name), "w+") as file:
    # Let's loop over lines of transient modified index file.
    for line in lines:
        # Let's write the current line to disk.
        file.write(line + "\n")
