from Indexer.create_index_judge import index_name as index_name_judge
from Indexer.create_index_court import index_name as index_name_court
from Indexer.create_index_date import index_name as index_name_date
from Indexer.create_index_id_number import index_name as index_name_id
from Indexer.create_index_reference_number import index_name as index_name_reference_number
from Indexer.create_index_words import index_name as index_name_word_positions
from shared_info import index_directory
from Util.tokenizer import all_lowercase_chars
import re

expression_types = ["and", "or"]
attribute_to_index_dictionary = {
    "sudca": index_name_judge,
    "súd": index_name_court,
    "dátum": index_name_date,
    "idč": index_name_id,
    "spzn": index_name_reference_number
}
index_input_path = "{}/index_{}.txt".format(index_directory, "{}")
index_positional_input_path = index_input_path.format("{}_letter_{}".format(index_name_word_positions, '{}'))
word_regex = re.compile("^[a-zA-Z{}]+$".format(all_lowercase_chars))
document_record_regex = re.compile("^[0-9]+\:([0-9]+\,)*[0-9]+$")


def resolve_text_query(query_text):
    query_root = parse_to_tree(query_text)
    print(query_root)
    matching_ids = query_documents(query_root)

    return matching_ids


def parse_to_tree(query_text):
    tokens = []
    current_token = ""
    in_string = False
    parenthesis_depth = 0

    while len(query_text) > 0 and query_text[0] == '(' and query_text[-1] == ')':
        query_text = query_text[1:-1]

    for char in query_text:
        if char == " " and parenthesis_depth == 0 and not in_string:
            if current_token != "":
                tokens.append(current_token)
                current_token = ""
            continue
        if char == "(" and not in_string:
            parenthesis_depth = parenthesis_depth + 1
        if char == ")" and not in_string:
            parenthesis_depth = parenthesis_depth - 1
        if char == '"':
            in_string = not in_string
        current_token = current_token + char

    if current_token != "":
        tokens.append(current_token)
        current_token = ""

    if len(tokens) == 1:
        return ['and', tokens[0]]

    expression_type = None
    value_tokens = []
    for token in tokens:
        if token.lower() in expression_types:
            if expression_type is not None:
                if token.lower() != expression_type:
                    raise ValueError("Query has OR and AND on the same level")
            expression_type = token.lower()
        else:
            value_tokens.append(token.lower())

    if len(tokens) == 0:
        raise ValueError("Empty token")

    if expression_type is None:
        print(tokens)
        raise ValueError("Query has no OR/AND between multiple tokens")

    for i in range(len(value_tokens)):
        value_tokens[i] = parse_to_tree(value_tokens[i])

    return [expression_type] + value_tokens


def query_documents(query):
    logical_operator = query[0]

    id_lists = []
    for token in query[1:]:
        if isinstance(token, list):
            ids = query_documents(token)
        elif token[0] == '"' and token[-1] == '"':
            ids = evaluate_full_text_query(token[1:-1])
        else:
            ids = evaluate_attribute_query(token)
        id_lists.append(ids)

    result_ids = id_lists[0]
    if logical_operator == "and":
        for id_list in id_lists[1:]:
            result_ids = [x for x in result_ids if x in id_list]
    elif logical_operator == "or":
        for id_list in id_lists[1:]:
            result_ids = result_ids + [x for x in id_list if x not in result_ids]

    return result_ids


def evaluate_attribute_query(text):
    attribute_name, attribute_value = text.split('=')
    attribute_value = attribute_value.replace('"', '')

    if attribute_name not in attribute_to_index_dictionary:
        raise ValueError("Trying to query non-existent attribute - {}".format(attribute_name))

    index_path = index_input_path.format(attribute_to_index_dictionary[attribute_name])
    matching_ids = []
    with open(index_path, 'r', encoding='utf-8') as index_file:
        for line in index_file:
            tokens = line.split(':')
            if tokens[0].lower() == attribute_value.lower():
                matching_ids = tokens[1].replace('\n', '').split(',')

    return matching_ids


def evaluate_full_text_query(text):
    full_text_query_words = text.split(' ')

    word_occurences = []
    for word in full_text_query_words:
        document_dict = {}
        try:
            with open(index_positional_input_path.format(word[0]), 'r', encoding='utf-8') as input_file:
                in_word = False
                for line in input_file:
                    line = line.replace('\n', '')

                    if line == "$" and in_word:
                        break

                    if word_regex.match(line):
                        if word != line:
                            continue
                        else:
                            in_word = True

                    if document_record_regex.match(line) and in_word:
                        tokens = line.split(':')
                        document_id = tokens[0]
                        positions = [int(x) for x in tokens[1].split(',')]
                        document_dict[document_id] = positions
        except FileNotFoundError:
            pass
        word_occurences.append({"word": word, "occurences": document_dict})

    document_occurence_dict = {}
    for word_entry in word_occurences:
        for document_id in word_entry["occurences"]:
            if document_id not in document_occurence_dict:
                document_occurence_dict[document_id] = [[] for _ in word_occurences]

    for i in range(len(word_occurences)):
        for document_id in word_occurences[i]["occurences"]:
            document_occurence_dict[document_id][i] = word_occurences[i]["occurences"][document_id]

    if len(word_occurences) > 1:
        pass
    ids_out = [document_id for document_id in document_occurence_dict]

    return ids_out


#ids = resolve_text_query('sudca="JUDr. Michal Eliaš" AND súd="Okresný súd Trnava" AND "ukradol deti"')
ids = resolve_text_query('sudca="JUDr. Michal Eliaš" AND súd="Okresný súd Trnava" AND "odstránil"')
#ids = resolve_text_query('sudca="JUDr. Michal Eliaš" AND súd="Okresný súd Trnava"')
print(ids)
