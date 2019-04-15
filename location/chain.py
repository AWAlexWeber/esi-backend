### File that does all of the chain management
# Importing errors
from auth.error import throw_json_error

# Importing JSON
import json
import requests
import mysql.connector

from datetime import datetime, timedelta

# Getting the flask request object
from flask import request

# Importing config
from config.config import api_call_get

# Static imports
from static.map import *
from static.ship import *
from static.structure import *

from auth.auth import auth_character, get_access_token
from auth.error import throw_json_error, throw_json_success
# Primary file for dealing with location

### Function for getting the entire 'chain' from a single solar system starting point...
def get_chain():
    print("Getting the users full chain")
    json_input = request.data
    json_data = json.loads(json_input)

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    system_name = json_data['system_name']
    system_id = get_solar_system_id_from_name(system_name)['solarSystemID']

    ### Loading the first to-visit
    visit_list = []
    visit_list.append(system_id)

    ### Loading from system name
    output = {}

    ### Iterate on all connections, deep search
    while len(visit_list) > 0:
        system_to_visit = visit_list.pop(0)
        print(system_to_visit)

        ### Appending the data from the solar system id
        location_data = get_system_info(system_to_visit)

        ### Appending from valid sigs within location
        ### TODO: Traverse sigs, append their connections

        output[location_data['solarSystemName']] = location_data

    return throw_json_success(200, output)
