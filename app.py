# Importing libraries for use
# Importing flask
from flask import Flask
# Importing requests
# Importing JSON
import json

# Including other python files
from auth.error import throw_json_error

# Including auth
from auth.auth import generate_request_url
from auth.auth import save_code
from auth.auth import get_auth

# Including the sig stuff
from sig.sig import add_sig
from location.location import get_location
from character.setting import *
from location.chain import *


# Setting up the flask
app = Flask("EvE ERB API")


@app.route('/')
def init_route():
    response = json.dumps(throw_json_error(404, "Page not found"))
    print("Returning " + response)
    return response


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

# Function for getting locations, whether a single person or multiple
@app.route('/chain/get', methods=['POST'])
def chain_get():
    response = json.dumps(get_chain())
    print("Returning " + response)
    return response

# Function for getting locations, whether a single person or multiple
@app.route('/location/get', methods=['POST'])
def location_get():
    response = json.dumps(get_location())
    print("Returning " + response)
    return response

@app.route('/sig/add', methods=['POST'])
def sig_add():
    response = json.dumps(add_sig())
    print("Returning " + response)
    return response

@app.route('/setting/get', methods=['POST'])
def setting_get():
    response = json.dumps(get_settings())
    print("Returning " + response)
    return response

@app.route('/setting/wormhole/add', methods=['POST'])
def setting_wormhole_add():
    response = json.dumps(add_wormhole_mask())
    print("Returning " + response)
    return response

@app.route('/setting/wormhole/delete', methods=['POST'])
def setting_wormhole_delete():
    response = json.dumps(delete_wormhole_mask())
    print("Returning " + response)
    return response

if __name__ == '__main__':
    app.run()
