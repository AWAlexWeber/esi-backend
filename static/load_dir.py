######################
### Usable Imports ###
######################
import json, flask, requests

### Importing Directory Loads
from .static import *

def static_load(app):
    @app.route('/static/wormholes', methods=['POST'])
    def get_wormhole_statics():
        response = json.dumps(get_all_wormholes())
        #print("Returning " + response)
        return response

    @app.route('/static/systems', methods=['POST'])
    def get_all_static_systems():
        response = json.dumps(get_all_systems())
        #print("Returning " + response)
        return response

