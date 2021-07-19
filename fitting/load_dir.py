######################
### Usable Imports ###
######################
import json, flask, requests

### Importing Directory Loads
from .fitting import *

def fitting_load(app):
    # Function for getting all fits associated with an account
    @app.route('/fit/get_eve_all', methods=['POST'])
    def get_all_eve():
        response = json.dumps(get_eve_all())
        return response

    @app.route('/fit/add', methods=['POST'])
    def add_fit():
        response = json.dumps(add_eft_fit())
        return response