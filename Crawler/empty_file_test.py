####################################################################################################################
# This script is file validity tester. Sometimes, only part of file arrives, resulting in erroneous file.   ########
# Heuristically, we found threshold of file size, which indicates faulty file which worked well,            ########
# so we do not need more sophisticated method.                                                              ########
####################################################################################################################

from os import listdir
from os.path import isfile, join, getsize

# Custom imports from other folders of this project
# Utility folder has scripts for dealing with common tasks, such as deleting pdf files from disk in this case
from Util.file_deleting import delete_pdf_and_txt_files
# All paths to directories within project are held in one play, to be able to change them easily.
from shared_info import file_pdf_directory

# Important parameter. If set True, will physically remove the files from the disk, otherwise it will just print
# duplicates in console.
perform_remedy = True
# Threshold of minimum file size. Smaller files are considered faulty and will be removed from disk.
min_size = 40000

# Let's obtain list of all documents
all_id_list = [f.replace('.pdf', '') for f in listdir(file_pdf_directory) if isfile(join(file_pdf_directory, f))]
bad_id_list = []
# Let's loop over all files and check, if they are faulty or not
for file_id in all_id_list:
    # THe check is based on their size. If it is lower than the threshold, they are added to list of files to be deleted
    if getsize(file_pdf_directory + "/" + file_id + ".pdf") < min_size:
        bad_id_list.append(file_id)

# Print the results to console
print(str(len(bad_id_list)) + " ids to be deleted")
print(bad_id_list)

# If we aren't supposed to remove faulty files from the disk, let's quit now
if not perform_remedy:
    exit()

# If we haven't quit yet, it means we are supposed to delete files from disk. Let's do it using our utility function
# designed for this special occasion
delete_pdf_and_txt_files(bad_id_list)
