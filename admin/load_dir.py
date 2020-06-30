######################
### Usable Imports ###
######################
import json, flask, requests

### Importing Directory Loads
from .admin import *

def admin_load(app):
    @app.route('/admin/accounts', methods=['POST'])
    
    def admin_get_accounts():
        response = json.dumps(get_accounts())
        print("Returning " + response)
        return response
        
    @app.route('/admin/set_character_type', methods=['POST'])
    
    def admin_set_account_group():
        response = json.dumps(set_account_group())
        print("Returning " + response)
        return response
