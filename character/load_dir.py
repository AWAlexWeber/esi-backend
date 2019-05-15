######################
### Usable Imports ###
######################
import json, flask, requests

### Importing Directory Loads
from .character import *
from .setting import *

def character_load(app):
    @app.route('/character/get', methods=['POST'])
    def getting_character():

        response = json.dumps(get_character())
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