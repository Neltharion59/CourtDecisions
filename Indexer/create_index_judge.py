from core_algorithms_index_inverted import create_attribute_index

index_name = "judges"
attribute_regex = "(^(([[\.a-zA-Z]*\,? )?(\,?[[\.a-zA-Z]* )*([ĎŇŤŠČŘŽÝÁÍÉÚŮÓÔĽA-Z][ěščřžýáíéóôÖöőüúůďťňľa-z]+[ \-]?){2,}(,? [[\.a-zA-Z]*)?)\nMeno a priezvisko sudcu, VSÚ:\n)|(^Meno a priezvisko sudcu, VSÚ:\n(([[\.a-zA-Z]*\,? )?(\,?[[\.a-zA-Z]* )*([ĎŇŤŠČŘŽÝÁÍÉÚŮÓÔĽA-Z][ěščřžýáíéóôÖöőüúůďťňľa-z]+[ \-]?){2,}(,? [[\.a-zA-Z]*)?)\n)"

create_attribute_index(index_name, attribute_regex, regex_group_index=[1, 7])
