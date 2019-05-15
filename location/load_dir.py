######################
### Usable Imports ###
######################
import json, flask, requests

### Importing Directory Loads
from .location import *
from .chain import *

def location_load(app):
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