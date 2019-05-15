######################
### Usable Imports ###
######################
import json, flask, requests

### Importing Directory Loads
from .auth import *
from .error import *


def auth_load(app):
    @app.route('/auth/code', methods=['GET'])
    def new_code_url():
        response = json.dumps(generate_request_url())
        print("Returning " + response)
        return response


    @app.route('/auth/code', methods=['POST'])
    def code_post():
        # Saving this code, and grabbing a new access and refresh token
        # We will be saving the refresh token, saving the access token, and returning the access token
        response = json.dumps(save_code())
        print("Returning " + response)
        return response