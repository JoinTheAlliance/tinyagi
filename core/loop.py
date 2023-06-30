from handle_user_input import handle_user_input
import database

chroma_client = database.get_client()
collections = database.get_collections()

def main():
    handle_user_input()

    # get self
    # get the current feed of memory

    # all arguments after the file name are user input
    loop_prompt = """
    """

    # check for ongoing tasks and run them
    # run the main loop