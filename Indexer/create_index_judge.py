####################################################################################################################
# This script creates inverse index of judge who ruled the decision.                                          ######
####################################################################################################################

# Custom imports from other folders of this project
# Let's use the algorithm to create inverted index
from Indexer.core_algorithms_index_inverted import create_attribute_index

# Let's define the name if this index.
index_name = "judges"
# Let's define the regex to find the value of this index in each file.
attribute_regex = "(^(([[\.a-zA-Z]*\,? )?(\,?[[\.a-zA-Z]* )*([ĎŇŤŠČŘŽÝÁÍÉÚŮÓÔĽA-Z][ěščřžýáíéóôÖöőüúůďťňľa-z]+[ \-]?){2,}(,? [[\.a-zA-Z]*)?)\nMeno a priezvisko sudcu, VSÚ:\n)|(^Meno a priezvisko sudcu, VSÚ:\n(([[\.a-zA-Z]*\,? )?(\,?[[\.a-zA-Z]* )*([ĎŇŤŠČŘŽÝÁÍÉÚŮÓÔĽA-Z][ěščřžýáíéóôÖöőüúůďťňľa-z]+[ \-]?){2,}(,? [[\.a-zA-Z]*)?)\n)"

# Let's create this index using the inverted index creation algorithm.
# This time we additionally specify regex match group indices where to look for desired value of this attribute.
create_attribute_index(index_name, attribute_regex, regex_group_index=[1, 7])
