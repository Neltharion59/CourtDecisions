from core_algorithms_index_inverted import create_attribute_index

index_name = "courts"
attribute_regex = "(.*súd.*)[\na-zA-Z\/0-9ěščřžýáíéóôúůďťňľĎŇŤŠČŘŽÝÁÍÉÚŮÓÔĽ]*Súd\:\n"

create_attribute_index(index_name, attribute_regex)
