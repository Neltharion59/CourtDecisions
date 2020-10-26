import re
from shared_info import file_txt_directory
unwanted_chars = ['/', ',', '.', '(', ')', ':']
all_lowercase_chars = "aáäbcčdďeéfghiíjklľĺmnňoóôpqrřsštťuúůvxyýzž"


def tokenize_string(string):
    tokens = string.split(' ')
    return tokens


def clear_string(string):
    # Lowercase
    string = string.lower()

    # Words split into individual letters
    regex = re.compile("[\n ]([a-zA-ZěščřžýáíéóôúůďťňľĎŇŤŠČŘŽÝÁÍÉÚŮÓÔĽ]( [a-zěščřžýáíéóôúůďťňľĎŇŤŠČŘŽÝÁÍÉÚŮÓÔĽ]){1,})[\n \.]", re.MULTILINE)
    matches = [x[0] for x in regex.findall(string)]
    for match in matches:
        string = string.replace(match, match.replace(' ', ''))

    # Abreviations
    string = re.sub(" [a-zA-ZěščřžýáíéóôúůďťňľĎŇŤŠČŘŽÝÁÍÉÚŮÓÔĽ]\.", "", string)

    # Messy chars
    string = strip_chars(string)

    # Whitespace
    string = clear_whitespaces(string)

    # Single-letter words
    for char in all_lowercase_chars:
        string = re.sub(" " + char + "{2,} ", "", string)

    return string


def clear_whitespaces(string):
    string = string.replace("\n", " ")
    string = string.replace("\t", " ")
    string = ' '.join(string.split())

    return string


def strip_chars(string):
    for char in unwanted_chars:
        string = string.replace(char, '')
    return string
