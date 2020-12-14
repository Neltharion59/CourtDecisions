####################################################################################################################
# This script offers util functions to process queries.                                                       ######
# Primarily only 'resolve_text_query' should be used outside this script                                      ######
# Should not be called as stand-alone                                                                         ######
####################################################################################################################

from datetime import datetime
from functools import reduce
import operator as op
import re

# Custom imports from other folders of this project
# All paths to directories within project are held in one play, to be able to change them easily.
from shared_info import index_directory, file_description_directory, file_word_directory
# Index names are stored at corresponding indexers, so that they are unified across the project
from Indexer.create_index_judge import index_name as index_name_judge
from Indexer.create_index_court import index_name as index_name_court
from Indexer.create_index_date import index_name as index_name_date
from Indexer.create_index_id_number import index_name as index_name_id
from Indexer.create_index_reference_number import index_name as index_name_reference_number
from Indexer.create_index_words import index_name as index_name_word_positions
# All sorts of util functions are going to be used here.
from Util.tokenizer import all_lowercase_chars

# Enumeration of types of composite query expressions.
expression_types = ["and", "or"]
# Dictionary for conversion: attribute_name_in_query -> index_name
attribute_to_index_dictionary = {
    "sudca": index_name_judge,
    "súd": index_name_court,
    "dátum": index_name_date,
    "idč": index_name_id,
    "spzn": index_name_reference_number
}
# Dictionary for conversion: index_name -> attribute_name_on_output_screen
index_to_attribute_scren_name_dictionary = {
    index_name_judge: "Sudca",
    index_name_court: "Súd",
    index_name_date: "Dátum vydania",
    index_name_id: "Identifikačné číslo spisu",
    index_name_reference_number: "Spisová značka"
}
# String template for path to inverse index file (parametrized by index name)
index_input_path = "{}/index_{}.txt".format(index_directory, "{}")
# String template for path to positional index file (parametrized by index name)
index_positional_input_path = index_input_path.format("{}_letter_{}".format(index_name_word_positions, '{}'))
# Regex to detect words in text file
word_regex = re.compile("^[a-zA-Z{}]+$".format(all_lowercase_chars))
# Regex to detect record in positional index file -> to differ it from meta lines in positional index file
document_record_regex = re.compile("^[0-9]+\:([0-9]+\,)*[0-9]+$")
# Relevance penalty when queried words appear in reverse order in text file
inverse_order_relevance_penalty = 0.5

# Artificial index name - attribute dictionaries for query result also need text preview
file_preview_index_name = 'text_preview'
# Position from which to take preview words
text_preview_offset = 30
# How many preview words to take
text_preview_length = 30


# Function that transforms textual query on input to list of results (dictionaries of document attributes).
# Is meant to be used from outside of this script.
def resolve_text_query(query_text):
    # Let's output progress to console.
    print("Resolving query: {}".format(query_text))
    # Let's parse the textual query to hierarchical tree.
    query_root = parse_to_tree(query_text)
    # Let's retrieve ids and relevance of documents matching this query.
    matching_ids = query_documents(query_root)
    # Let's retrieve info of all matching files.
    matching_files = list(filter(lambda x: index_name_date in x, map(lambda x: {**x, **retrieve_file_info(x['id'])}, matching_ids)))
    # Let's order the result files primarily by relevance descendingly, secondarily by ruling date descendingly
    query_results = order_by_relevance(matching_files)
    # Let's return the results
    return query_results


# Function that is meant to recursively parse textual query into a tree that can be easily processed.
def parse_to_tree(query_text):
    # Let's initialize helping variables
    tokens = []
    current_token = ""
    in_string = False
    parenthesis_depth = 0

    # If the query is parenthesised at top level, let's get rid of the useless parenthesis.
    while len(query_text) > 0 and query_text[0] == '(' and query_text[-1] == ')':
        query_text = query_text[1:-1]

    # Let's process the query character by character, creating tokens
    for char in query_text:
        # If we have space, we are at top level and not in string expression, it means end of current token
        if char == " " and parenthesis_depth == 0 and not in_string:
            if current_token != "":
                tokens.append(current_token)
                current_token = ""
            continue

        # If we have opening bracket outside string expression, we are in deeper parenthesis
        if char == "(" and not in_string:
            parenthesis_depth = parenthesis_depth + 1
        # If we have closing bracket outside string expression, we are in less deep parenthesis
        if char == ")" and not in_string:
            parenthesis_depth = parenthesis_depth - 1
        # If we have string expression denoter, let's remember it
        if char == '"':
            in_string = not in_string

        # If nothing special happened, we should append the current character to current token
        current_token = current_token + char

    # If we have looped over entire query and last token has not been added to list of tokens, we should do it now
    if current_token != "":
        tokens.append(current_token)
        current_token = ""

    # If there is only one token, we are done (use 'and' expression for unified processing)
    if len(tokens) == 1:
        return ['and', tokens[0]]

    # Let's initialize more helping variables
    expression_type = None
    value_tokens = []
    # Let's loop over all tokens of the query we received on input
    for token in tokens:
        # If current token is 'and' or 'or', let's check if everything is correct
        # and remember what type of composite expression we have
        if token.lower() in expression_types:
            if expression_type is not None:
                if token.lower() != expression_type:
                    raise ValueError("Query has OR and AND on the same level")
            expression_type = token.lower()
        else:
            value_tokens.append(token.lower())

    # If we have no takens, processed query is empty string
    if len(tokens) == 0:
        raise ValueError("Empty token")

    # If we have multiple tokens but no connecting operation, query is invalid
    if expression_type is None:
        print(tokens)
        raise ValueError("Query has no OR/AND between multiple tokens")

    # Recursively parse all tokens of the query
    for i in range(len(value_tokens)):
        value_tokens[i] = parse_to_tree(value_tokens[i])

    # Let's return parsed tree
    return [expression_type] + value_tokens


# Function that is meant to retrieve ids and relevance of all documents matching the query tree
def query_documents(query):
    # Let's see what logical operator connects tokens of current query
    # ('and' if there is only 1 token for unified processing)
    logical_operator = query[0]

    id_lists = []
    # Let's loop over all tokens in current query and evaluate them
    for token in query[1:]:
        # If current token is list, it means it is a nested query, so it should be recursively evaluated
        if isinstance(token, list):
            ids = query_documents(token)
        # If current token is closed within string-denoting characters, it should be evaluated as full text query
        elif token[0] == '"' and token[-1] == '"':
            ids = evaluate_full_text_query(token[1:-1])
        # Otherwise the token must be attribute query
        else:
            ids = evaluate_attribute_query(token)
        # Let's add list of ids matched by current token to list of final results
        id_lists.append(ids)

    # Let's merge ids matched by individual tokens
    # Start from results of first token
    result_ids = id_lists[0]
    # Let's loop over these ids and retrieve their relevance
    for result in result_ids:
        temp = result["relevance"]
        result["relevance"] = []
        result["relevance"].append(temp)

    # If logical operator of this query is 'and', resulting ids should be conjunction of results of individual tokens
    if logical_operator == "and":
        # Let's perform the conjunction over results of all tokens
        for id_list in id_lists[1:]:
            id_only_list = [x["id"] for x in id_list]
            temp = []
            for result in result_ids:
                if result["id"] in id_only_list:
                    result["relevance"].append(id_list[id_only_list.index(result["id"])]["relevance"])
                    temp.append(result)
            result_ids = temp
    # If logical operator of this query is 'and', resulting ids should be union of results of individual tokens
    elif logical_operator == "or":
        # Let's perform the union over results of all tokens
        for id_list in id_lists[1:]:
            id_only_list = [x["id"] for x in result_ids]
            for doc_id in id_list:
                if doc_id["id"] not in id_only_list:
                    if doc_id["relevance"] is not list:
                        doc_id["relevance"] = [doc_id["relevance"]]
                    result_ids.append(doc_id)

    # Now we have ids of documents matching the entire query. Let's calculate their relevance
    for result in result_ids:
        result["relevance"] = round(reduce(op.add, result["relevance"])/len(result["relevance"]), 2)

    # Return the result - unordered list of dicts containing id and relevance of each matched document
    return result_ids


# Function that is meant to retrieve ids and relevance of all documents matching simple attribute query in textual form
def evaluate_attribute_query(text):
    # Let's retrieve attribute name and desired value of the query
    attribute_name, attribute_value = text.split('=')
    attribute_value = attribute_value.replace('"', '')

    # If queried attribute does not exist in indexes, the query must be faulty
    if attribute_name not in attribute_to_index_dictionary:
        raise ValueError("Trying to query non-existent attribute - {}".format(attribute_name))

    # Let's prepare path to index file to be read from.
    index_path = index_input_path.format(attribute_to_index_dictionary[attribute_name])
    matching_ids = []
    # Let's read the index file and find line with desired attribute value, and retrieve all matching ids.
    # Document is considered a match if queried value is substring of found value.
    with open(index_path, 'r', encoding='utf-8') as index_file:
        for line in index_file:
            tokens = line.split(':')
            if attribute_value.lower() in tokens[0].lower():
                matching_ids += tokens[1].replace('\n', '').split(',')

    # Let's assign relevance to each found id. With attribute queries, relevance is always 1.0 -> Full relevance
    ids_out = [{"id": document_id, "relevance": 1.0} for document_id in matching_ids]

    # Let's return result
    return ids_out


# Function that is meant to retrieve ids and relevance of all documents matching simple full text query in textual form
def evaluate_full_text_query(text):
    # Let's prepare list of queried words (order matters)
    full_text_query_words = text.split(' ')

    word_occurences = []
    # Let's loop over all words in this full text query
    for word in full_text_query_words:
        # Let's initialize dictionary of all documents
        document_dict = {}
        try:
            # Let's open index file for current word
            with open(index_positional_input_path.format(word[0]), 'r', encoding='utf-8') as input_file:
                in_word = False
                # Let's loop over all lines of index file
                for line in input_file:
                    line = line.replace('\n', '')

                    # Ignore delimiter line
                    if line == "$" and in_word:
                        break

                    # Ignore line with word (but remember that we encountered it)
                    if word_regex.match(line):
                        if word != line:
                            continue
                        else:
                            in_word = True

                    # If we are at desired word, let's remember document id and word positions
                    if document_record_regex.match(line) and in_word:
                        tokens = line.split(':')
                        document_id = tokens[0]
                        positions = [int(x) for x in tokens[1].split(',')]
                        document_dict[document_id] = positions
        except FileNotFoundError:
            pass
        # Apprend results of current word to total word results.
        word_occurences.append({"word": word, "occurences": document_dict})

    document_occurence_dict = {}
    # Let's loop over entries for each word of query and initialize result dict
    for word_entry in word_occurences:
        for document_id in word_entry["occurences"]:
            if document_id not in document_occurence_dict:
                document_occurence_dict[document_id] = [[] for _ in word_occurences]

    # Let's loop over entries for each word of query and initialize occurence lists
    for i in range(len(word_occurences)):
        for document_id in word_occurences[i]["occurences"]:
            document_occurence_dict[document_id][i] = word_occurences[i]["occurences"][document_id]

    # Let's overlap occurence lists and determine relevance
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


# Let's order search results by primarily relevance, secondarily date; both descending
def order_by_relevance(result_list):
    return sorted(result_list, key=lambda x: (x["relevance"], datetime.strptime(x[index_name_date], "%d. %m. %Y")), reverse=True)


# Let's retrieve info of a document with given id
def retrieve_file_info(file_id):
    # Let's initialize result dict
    result_file_info = {}

    # Let's prepare file name of description index of given document
    input_file_name = file_description_directory + "/" + file_id + ".txt"
    # Let's read the content of description index and store it in dict
    try:
        with open(input_file_name, 'r', encoding='utf-8') as input_file:
            for line in input_file:
                tokens = line.replace('\n', '').split(':')
                result_file_info[tokens[0]] = tokens[1]
    except FileNotFoundError:
        print("File description of file with id " + file_id + " not found.")

    # Let's prepare file name of text version of given document
    input_file_name = file_word_directory + "/" + file_id + ".txt"
    # Let's read the content of text file and store it in dict
    try:
        with open(input_file_name, 'r') as input_file:
            words = input_file.read().split(' ')
            description = ' '.join(words[text_preview_offset: text_preview_offset + text_preview_length])
            result_file_info[file_preview_index_name] = description
    except FileNotFoundError:
        print("Word file of file with id " + file_id + " not found.")

    return result_file_info


# Use this to turn dictionary with file info into pretty human-readable string
def stringify_file_info(file_info_dict):
    result_string = ""
    for attribute_name in file_info_dict:
        if attribute_name in index_to_attribute_scren_name_dictionary:
            result_string += index_to_attribute_scren_name_dictionary[attribute_name] + ":\t" + file_info_dict[attribute_name] + "\n"
    if file_preview_index_name in file_info_dict:
        result_string += file_info_dict[file_preview_index_name]
    return result_string
