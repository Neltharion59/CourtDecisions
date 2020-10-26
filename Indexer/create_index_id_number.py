from core_algorithms_index_inverted import create_attribute_index

index_name = "identification_numbers"
attribute_regex = "Identifikačné číslo súdneho spisu: ([0-9]{10})"

create_attribute_index(index_name, attribute_regex)
