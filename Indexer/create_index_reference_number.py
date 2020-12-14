####################################################################################################################
# This script creates inverse index of file reference number.                                                 ######
####################################################################################################################

# Custom imports from other folders of this project
# Let's use the algorithm to create inverted index
from Indexer.core_algorithms_index_inverted import create_attribute_index

# Let's define the name if this index.
index_name = "reference_numbers"
# Let's define the regex to find the value of this index in each file.
attribute_regex = "^[0-9]+[a-zA-ZěščřžýáíéóôúůďťňľĎŇŤŠČŘŽÝÁÍÉÚŮÓÔĽ]+\/[0-9]+\/[0-9]+$"

# Let's create this index using the inverted index creation algorithm.
create_attribute_index(index_name, attribute_regex)
