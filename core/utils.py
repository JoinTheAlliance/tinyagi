import os
import requests
from constants import debug, respond_to_user_input
def respond_to_terminal_input(msg):
    if(respond_to_user_input == False):
        return
    response = requests.get("http://127.0.0.1:5001/response", params={"msg": msg})
    return response.text.strip()

def debug_write_file(text, filename):
    # if logs directory does not exist, create it
    os.makedirs("logs", exist_ok=True)
    # check that all of the directories exist
    if filename.find("/") != -1:
        # there is a directory in the filename
        directory = filename[:filename.rfind("/")]
        # create the directory at logs/directory
        os.makedirs("logs/"+directory, exist_ok=True)
    if(debug == False):
        return
    file = open("logs/"+filename+".txt", "w")
    file.write(text)
    file.close()