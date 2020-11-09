from Querying_Engine.query_resolver import resolve_text_query


def query_resolving(input_generator):
    for user_input in input_generator:
        if user_input.lower() == "exit":
            exit()

        try:
            ids = resolve_text_query(user_input)
            print(ids)
        except:
            print("Wrong query")


def cli_input_generator():
    while True:
        yield input()


query_resolving(cli_input_generator())
