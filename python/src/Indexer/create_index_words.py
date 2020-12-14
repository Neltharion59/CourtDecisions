####################################################################################################################
# This script creates positional index of decisition text.                                                    ######
####################################################################################################################

from os import getcwd
import sys

# Mandatory if we want to run this script from windows cmd. Must precede all imports from this project
conf_path = getcwd()
sys.path.append(conf_path)
sys.path.append(conf_path + '..')
sys.path.append(conf_path + '../..')

# Custom imports from other folders of this project
# Let's use the algorithm to create positional index
from Indexer.core_algorithms_index_positional import create_attribute_index

# Let's define the name if this index.
index_name = "words"

# Let's create this index using the positional index creation algorithm.
create_attribute_index(index_name)
