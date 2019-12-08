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
        #print("Returning " + response)
        return response

    @app.route('/sig/add_multiple', methods=['POST'])
    def sig_multiple_add():
        response = json.dumps(add_sig_multiple())
        #print("Returning " + response)
        return response

    @app.route('/sig/get', methods=['POST'])
    def get_all_sigs():
        response = json.dumps(get_sigs())
        #print("Returning " + response)
        return response

    @app.route('/sig/delete', methods=['POST'])
    def delete_input_sig():
        response = json.dumps(delete_sig())
        #print("Returning " + response)
        return response

    @app.route('/sig/edit', methods=['POST'])
    def edit_input_sig():
        response = json.dumps(edit_sig())
        #print("Returning " + response)
        return response