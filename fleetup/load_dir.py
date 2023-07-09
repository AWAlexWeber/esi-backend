######################
### Usable Imports ###
######################
import json, flask, requests

### Importing Directory Loads
from .fleetup import *

def fleetup_load(app):
    # Function for getting locations, whether a single person or multiple
    @app.route('/fleetup/get', methods=['POST'])
    def pilots_get():
        response = json.dumps(get_pilots())
        return response