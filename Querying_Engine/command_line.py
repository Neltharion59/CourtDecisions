from os import getcwd
import sys

conf_path = getcwd()
sys.path.append(conf_path)
sys.path.append(conf_path + '..')
sys.path.append(conf_path + '../..')

from Querying_Engine.query_resolver import resolve_text_query, retrieve_file_info, stringify_file_info
result_separator = '----------------------------------------------------------------------------'


def query_resolving(input_generator):
    for user_input in input_generator:
        if user_input.lower() == "exit":
            exit()

        try:
            files = resolve_text_query(user_input)
            print("{} results".format(len(files)))
            for file in files:
                print(result_separator)
                print(stringify_file_info(file))
        except:
            print("Wrong query")
        print(result_separator)


def cli_input_generator():
    while True:
        yield input()


query_resolving(cli_input_generator())
