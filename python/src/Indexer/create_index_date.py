####################################################################################################################
# This script creates inverse index of date when the decision was ruled.                                      ######
####################################################################################################################

from datetime import datetime

from os import getcwd
import sys

# Mandatory if we want to run this script from windows cmd. Must precede all imports from this project
conf_path = getcwd()
sys.path.append(conf_path)
sys.path.append(conf_path + '..')
sys.path.append(conf_path + '../..')

# Custom imports from other folders of this project
# Let's use the algorithm to create inverted index
from Indexer.core_algorithms_index_inverted import create_attribute_index

# Let's define the name if this index.
index_name = "dates"
# Let's define the regex to find the value of this index in each file.
attribute_regex = "Dátum vydania rozhodnutia:\n(([0-2][0-9]|3[0-1])\. ?(0[0-9]|1[0-2])\. ?[0-9]{4})"

# Let's create this index using the inverted index creation algorithm.
# In this case, we additionally specify sorting order of lines in index - we do not want to order alphabetically,
# we want to order by the date.
# We also want index lines to be sorted in descending order (more recent decisions might be queries for more often)
create_attribute_index(index_name, attribute_regex,
                       sort_lambda=lambda date: datetime.strptime(date.split(':')[0], '%d. %m. %Y'),
                       reverse_order=True
                       )
