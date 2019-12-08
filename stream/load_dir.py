######################
### Usable Imports ###
######################
import json, flask, requests

### Importing Directory Loads
from .stream import *

def stream_load(app):

    # Function for getting locations, whether a single person or multiple
    @app.route('/stream/auth/get', methods=['POST'])
    def auth_get_new():
        response = json.dumps(get_new_auth())
        print("Returning " + response)
        return response

    @app.route('/stream/token/get', methods=['POST'])
    def token_get_new():
        response = json.dumps(get_new_token())
        print("Returning " + response)
        return response