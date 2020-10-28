import re

unwanted_chars = '/,.():„“_-%€§;!?[]+*"‰&#=|<>'
unwanted_patterns = [
    [" [a-zA-ZěščřžýáíéóôúůďťňľĎŇŤŠČŘŽÝÁÍÉÚŮÓÔĽ]\.", ""],
    ["[0-9]+", ""],
    ["(^| )\<[0-9a-zA-ZěščřžýáíéóôúůďťňľĎŇŤŠČŘŽÝÁÍÉÚŮÓÔĽ]\>($| )", " "],
]
single_letter_words = "aikosuvz"
all_lowercase_chars = "aáäbcčdďeéfghiíjklľĺmnňoóôpqrřsštťuúůvwxyýzž"


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

    # Messy chars
    string = strip_chars(string)

    # Whitespace
    string = clear_whitespaces(string)

    # Words that aren't really words
    for regex_pair in unwanted_patterns:
        string = re.sub(regex_pair[0], regex_pair[1], string)

    # Whitespace again
    string = clear_whitespaces(string)

    # Single-letter-composed words
    for char in all_lowercase_chars:
        string = re.sub("" + char + "{3,}", "", string)
    for char in all_lowercase_chars:
        string = re.sub("(^| )" + char + "{2,}($| )", " ", string)

    # Single-letter words
    for char in set(all_lowercase_chars)-set(single_letter_words):
        string = re.sub("(^| ){}($| )".format(char), " ", string)

    # Whitespace and again
    string = clear_whitespaces(string)

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
