######################
### Usable Imports ###
######################
import json, flask, requests

from config.config import manual_request

# Some basic stuff
def config_load(app):
    # Function for making a manual API request
    @app.route('/config/manual', methods=['POST'])
    def request_manual():
        response = json.dumps(manual_request())
        print("Returning " + response)
        return response