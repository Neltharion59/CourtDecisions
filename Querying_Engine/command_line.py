####################################################################################################################
# This script offers CLI interface to query the document base                                                 ######
####################################################################################################################

from os import getcwd
import sys

# Mandatory if we want to run this scripts from windows cmd. Must precede all imports from this project
conf_path = getcwd()
sys.path.append(conf_path)
sys.path.append(conf_path + '..')
sys.path.append(conf_path + '../..')

# Custom imports from other folders of this project
# We're just user interface for algorithms from another script
from Querying_Engine.query_resolver import resolve_text_query, stringify_file_info
# Visual separator for individual results
result_separator = '----------------------------------------------------------------------------'


# This function reads queries from console input and prints results until "exit" is typed in
def query_resolving(input_generator):
    # As long as there's input, let's perform action
    for user_input in input_generator:
        # If input is the exit command, let's finish the script
        if user_input.lower() == "exit":
            exit()

        # Let's try to resolve query, fetch results and print them
        try:
            # Let's fetch list of document info for documents matching the query
            files = resolve_text_query(user_input)
            # Tell the user how many results we have
            print("{} results".format(len(files)))
            # Let's loop over all query results
            for file in files:
                # Print the result separator
                print(result_separator)
                # Print the current result to console
                print(stringify_file_info(file))
        # If something failed, let's tell the user
        except:
            print("Wrong query")

        # Let's separate this query's results from another one
        print(result_separator)


# Simple utility function to read from command line infinitely
def cli_input_generator():
    while True:
        yield input()


# Let's start reading the input
query_resolving(cli_input_generator())
