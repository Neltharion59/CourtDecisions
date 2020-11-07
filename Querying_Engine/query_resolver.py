expression_types = ["and", "or"]


def resolve_text_query(query_text):
    results = []

    query_root = parse_to_tree(query_text)
    print(query_root)
    matching_ids = query_documents(query_root)

    return results


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


def evaluate_full_text_query(text):
    pass


def evaluate_attribute_query(text):
    pass
