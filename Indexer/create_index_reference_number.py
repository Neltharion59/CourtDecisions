from core_algorithms_index_inverted import create_attribute_index

index_name = "reference_numbers"
attribute_regex = "^[0-9]+[a-zA-ZěščřžýáíéóôúůďťňľĎŇŤŠČŘŽÝÁÍÉÚŮÓÔĽ]+\/[0-9]+\/[0-9]+$"

create_attribute_index(index_name, attribute_regex)
