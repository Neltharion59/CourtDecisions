import re
from shared_info import index_directory
from Util.tokenizer import all_lowercase_chars
from Indexer.create_index_words import index_name as input_index_name
from nltk import edit_distance


def normalized_similarity(word1, word2):
    distance = edit_distance(word1, word2)
    normalized_distance = distance/max(len(word1), len(word2))
    similarity = round(1 - normalized_distance, 2)
    return similarity


def insert_ordered(array, element):
    for i in range(len(array)):
        if array[i][1] < element[1]:
            array.insert(i, element)
            return
    array.append(element)
    return


output_index_name = "word_similarity"
index_input_file_path_template = "{}/index_{}_letter_{}.txt".format(index_directory, input_index_name, '{}')
index_output_file_path_template = "{}/index_{}_letter_{}.txt".format(index_directory, output_index_name, '{}')
index_suffix_names = list(all_lowercase_chars) + ["misc"]

pattern_word_delimiter = re.compile("^\$$")
pattern_positional_index_row = re.compile("^[0-9]+\:([0-9]+\,)*[0-9]+$")

vocabulary_top = []
vocabulary = []
for letter in index_suffix_names:
    try:
        with open(index_input_file_path_template.format(letter), 'r', encoding='utf-8') as input_file:
            for line in input_file:
                line = line.replace('\n', '')
                if not pattern_word_delimiter.match(line) and not pattern_positional_index_row.match(line):
                    vocabulary.append(line)
                    vocabulary_top.append(line)
    except FileNotFoundError:
        pass

print("Vocabulary has been read - contains {} words.".format(len(vocabulary)))

for letter in index_suffix_names:
    try:
        with open(index_output_file_path_template.format(letter), 'r', encoding='utf-8') as input_file:
            for line in input_file:
                word = line.split(":")[0]
                vocabulary_top.remove(word)
    except FileNotFoundError:
        pass

print("Vocabulary has been reduced - contains {} words.".format(len(vocabulary_top)))

i = 1
for word_top in vocabulary_top:
    print("Making similarities for word {} -> {:.2%}:".format(word_top, i/len(vocabulary_top)))
    similarities = []
    j = 1
    for word in vocabulary:
        print("{} - {} -> {:.2%} -> {:.2%}".format(word_top, word, i/len(vocabulary_top), j/len(vocabulary)))
        insert_ordered(similarities, (word, normalized_similarity(word_top, word)))
        j = j + 1
    output_string = word_top + ":"
    for similarity_tuple in similarities:
        output_string = output_string + similarity_tuple[0] + " " + str(similarity_tuple[1]) + ","
    output_string = output_string[:-1] + "\n"
    with open(index_output_file_path_template.format(word_top[0]), 'a+', encoding='utf-8') as output_file:
        output_file.write(output_string)
    i = i + 1
