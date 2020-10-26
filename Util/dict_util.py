from Util.tokenizer import all_lowercase_chars


def split_dict_abc(dict_in, file_id):
    words = list(dict_in.keys())

    big_dict = {}
    for word in words:
        if word[0] in all_lowercase_chars:
            key = word[0]
        else:
            key = 'misc'

        if key not in big_dict:
            big_dict[key] = {}
        big_dict[key][word] = {file_id: dict_in[word]}

    return big_dict


def single_letter_dict_2_string(dict_in):
    string = ''
    for word in dict_in:
        string += '$\n'
        string += word + '\n'
        for file_id in dict_in[word]:
            string += file_id + ":"

            string += str(dict_in[word][file_id][0])
            for index in range(1, len(dict_in[word][file_id])):
                string += ',' + str(dict_in[word][file_id][index])
            string += '\n'

    return string


def single_letter_string_2_dict(string_in):
    pass
