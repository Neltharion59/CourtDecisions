####################################################################################################################
# This script creates positional index of decisition text.                                                    ######
####################################################################################################################

# Custom imports from other folders of this project
# Let's use the algorithm to create positional index
from Indexer.core_algorithms_index_positional import create_attribute_index

# Let's define the name if this index.
index_name = "words"

# Let's create this index using the positional index creation algorithm.
create_attribute_index(index_name)
