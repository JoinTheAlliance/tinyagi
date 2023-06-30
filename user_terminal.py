from flask import Flask, request
import requests
import threading
import logging

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
log.setLevel(logging.CRITICAL)

def start_server():
    app.run(port=5001, debug=False)
    log = logging.getLogger('werkzeug')
    log.disabled = True
    log.setLevel(logging.CRITICAL)

# start flask on 5001

@app.route("/response", methods=["GET"])
def receive_message():
    message = request.args.get('msg')  # Get data from input, we named it 'msg'
    print(f"\nAGENT> {message}\n>")
    return "", 200  # Return a successful HTTP response

def create_input_event(prompt):
    # Make HTTP request
    response = requests.get("http://127.0.0.1:5000/msg", params={"msg": prompt})
    # Extract and return text
    return response.text.strip()

def main():
    # Start the Flask app in a separate thread
    threading.Thread(target=start_server, daemon=True).start()

    while True:
        prompt = input("")
        # if input is not empty
        if prompt != "":
            create_input_event(prompt)

if __name__ == "__main__":
    main()

