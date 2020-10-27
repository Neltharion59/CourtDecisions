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
    dict_out = {}

    word_sections = string_in.split('$')
    for word_section in word_sections:
        # Get rid of empty lines
        lines = word_section.split("\n")
        lines = lines[1:-1]
        # Isolate word itself
        if len(lines) <= 0:
            continue
        word = lines[0]
        lines = lines[1:]
        # Create word entry in dict
        dict_out[word] = {}
        for line in lines:
            tokens = line.split(':')
            dict_out[word][tokens[0]] = tokens[1].split(',')

    return dict_out


def merge_single_letter_dicts(dict_1, dict_2):
    for key in dict_2:
        if key not in dict_1:
            dict_1[key] = {}
        for key_2 in dict_2[key]:
            if key_2 not in dict_1[key]:
                dict_1[key][key_2] = []
            dict_1[key][key_2] = sorted(dict_1[key][key_2] + list(set(dict_2[key][key_2]) - set(dict_1[key][key_2])))

    return dict_1
