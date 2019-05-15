######################
### Usable Imports ###
######################
import json, flask, requests

### Importing Directory Loads
from .sig import *

def sig_load(app):
    @app.route('/sig/add', methods=['POST'])
    def sig_add():
        response = json.dumps(add_sig())
        print("Returning " + response)
        return response

    @app.route('/sig/get', methods=['POST'])
    def get_all_sigs():
        response = json.dumps(get_sigs())
        print("Returning " + response)
        return response