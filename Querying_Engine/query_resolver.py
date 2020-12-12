from datetime import datetime

from Indexer.create_index_judge import index_name as index_name_judge
from Indexer.create_index_court import index_name as index_name_court
from Indexer.create_index_date import index_name as index_name_date
from Indexer.create_index_id_number import index_name as index_name_id
from Indexer.create_index_reference_number import index_name as index_name_reference_number
from Indexer.create_index_words import index_name as index_name_word_positions
from shared_info import index_directory, file_description_directory, file_word_directory
from Util.tokenizer import all_lowercase_chars
from functools import reduce
import operator as op
import re

expression_types = ["and", "or"]
attribute_to_index_dictionary = {
    "sudca": index_name_judge,
    "súd": index_name_court,
    "dátum": index_name_date,
    "idč": index_name_id,
    "spzn": index_name_reference_number
}
index_to_attribute_scren_name_dictionary = {
    index_name_judge: "Sudca",
    index_name_court: "Súd",
    index_name_date: "Dátum vydania",
    index_name_id: "Identifikačné číslo spisu",
    index_name_reference_number: "Spisová značka"
}
index_input_path = "{}/index_{}.txt".format(index_directory, "{}")
index_positional_input_path = index_input_path.format("{}_letter_{}".format(index_name_word_positions, '{}'))
word_regex = re.compile("^[a-zA-Z{}]+$".format(all_lowercase_chars))
document_record_regex = re.compile("^[0-9]+\:([0-9]+\,)*[0-9]+$")
inverse_order_relevance_penalty = 0.5

file_preview_index_name = 'text_preview'
text_preview_offset = 30
text_preview_length = 30


def resolve_text_query(query_text):
    print(query_text)
    print("Resolving query: {}".format(query_text))
    query_root = parse_to_tree(query_text)
    matching_ids = query_documents(query_root)
    matching_files = list(filter(lambda x: index_name_date in x, map(lambda x: {**x, **retrieve_file_info(x['id'])}, matching_ids)))
    sorted_ids = order_by_relevance(matching_files)
    return sorted_ids


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
    for result in result_ids:
        temp = result["relevance"]
        result["relevance"] = []
        result["relevance"].append(temp)

    if logical_operator == "and":
        for id_list in id_lists[1:]:
            id_only_list = [x["id"] for x in id_list]
            temp = []
            for result in result_ids:
                if result["id"] in id_only_list:
                    result["relevance"].append(id_list[id_only_list.index(result["id"])]["relevance"])
                    temp.append(result)
            result_ids = temp
    elif logical_operator == "or":
        for id_list in id_lists[1:]:
            id_only_list = [x["id"] for x in result_ids]
            for doc_id in id_list:
                if doc_id["id"] not in id_only_list:
                    if doc_id["relevance"] is not list:
                        doc_id["relevance"] = [doc_id["relevance"]]
                    result_ids.append(doc_id)

    for result in result_ids:
        result["relevance"] = round(reduce(op.add, result["relevance"])/len(result["relevance"]), 2)

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
            if attribute_value.lower() in tokens[0].lower():
                matching_ids = tokens[1].replace('\n', '').split(',')

    ids_out = [{"id": document_id, "relevance": 1.0} for document_id in matching_ids]
    return ids_out


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
        ids_out = []
        for document_id in document_occurence_dict:
            distances = []
            for i in range(1, len(word_occurences)):
                distances.append([])
                for first_word_index in document_occurence_dict[document_id][i-1]:
                    for second_word_index in document_occurence_dict[document_id][i]:
                        if first_word_index == second_word_index:
                            continue

                        curr_relevance = abs(first_word_index-second_word_index)
                        if first_word_index > second_word_index:
                            curr_relevance = curr_relevance * (1 - inverse_order_relevance_penalty)
                        curr_relevance = 1 - min(1, round(curr_relevance/100, 2))
                        distances_index = i - 1

                        distances[distances_index].append(curr_relevance)

            relevance = reduce(op.add, [reduce(op.add, x)/len(x) if len(x) > 0 else 0 for x in distances])/len(distances)
            ids_out.append({"id": document_id, "relevance": relevance})
    else:
        max_occurence = reduce(max, (len(document_occurence_dict[x][0]) for x in document_occurence_dict))
        ids_out = [{"id": document_id, "relevance": len(document_occurence_dict[document_id][0])/max_occurence} for document_id in document_occurence_dict]

    return ids_out


def order_by_relevance(result_list):
    return sorted(result_list, key=lambda x: (x["relevance"], datetime.strptime(x[index_name_date], "%d. %m. %Y")), reverse=True)


def retrieve_file_info(file_id):
    result_file_info = {}

    input_file_name = file_description_directory + "/" + file_id + ".txt"
    try:
        with open(input_file_name, 'r', encoding='utf-8') as input_file:
            for line in input_file:
                tokens = line.replace('\n', '').split(':')
                result_file_info[tokens[0]] = tokens[1]
    except FileNotFoundError:
        print("File description of file with id " + file_id + " not found.")

    input_file_name = file_word_directory + "/" + file_id + ".txt"
    try:
        with open(input_file_name, 'r') as input_file:
            words = input_file.read().split(' ')
            description = ' '.join(words[text_preview_offset: text_preview_offset + text_preview_length])
            result_file_info[file_preview_index_name] = description
    except FileNotFoundError:
        print("Word file of file with id " + file_id + " not found.")

    return result_file_info


def stringify_file_info(file_info_dict):
    result_string = ""
    for attribute_name in file_info_dict:
        if attribute_name in index_to_attribute_scren_name_dictionary:
            result_string += index_to_attribute_scren_name_dictionary[attribute_name] + ":\t" + file_info_dict[attribute_name] + "\n"
    if file_preview_index_name in file_info_dict:
        print("Adding file info")
        print(file_info_dict[file_preview_index_name])
        print("Added file info")
        result_string += file_info_dict[file_preview_index_name]
    return result_string
