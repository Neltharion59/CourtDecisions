from Querying_Engine.query_resolver import resolve_text_query, retrieve_file_info, stringify_file_info
result_separator = '----------------------------------------------------------------------------'

def query_resolving(input_generator):
    for user_input in input_generator:
        if user_input.lower() == "exit":
            exit()

        try:
            ids = resolve_text_query(user_input)
            for file_id in ids:
                print(result_separator)
                print(stringify_file_info(retrieve_file_info(file_id['id'])))
        except:
            print("Wrong query")


def cli_input_generator():
    while True:
        yield input()


query_resolving(cli_input_generator())
