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

### Private helper function for sigs...
def get_sigs_internal():
    ### Getting all of the sigs in our chain...
    connector = init_mysql("db_map")
    cursor = connector.cursor()
    GET_SIGS = "SELECT * FROM tb_sig WHERE sig_status = 0"
    cursor.execute(GET_SIGS)
    result_raw = cursor.fetchall()
    result = get_format_from_raw_full(result_raw, cursor)

    sig_output_id = {}
    sig_output_system = {}

    for sig in result:
        ### Getting our sig data
        sig_id = sig['sig_id']
        sig_system = sig['sig_system']

        # Appending
        sig_output_id[sig_id] = sig

        if sig_system in sig_output_system:
            sig_output_system[sig_system][sig_id] = sig
        else:
            sig_output_system[sig_system] = {}
            sig_output_system[sig_system][sig_id] = sig

    sig_output = {
        "sig_output_id": sig_output_id,
        "sig_output_system": sig_output_system
    }

    return sig_output


### Function for getting the entire 'chain' from a single solar system starting point...
def get_chain():
    #print("Getting the users full chain")
    json_input = request.data
    json_data = json.loads(json_input.decode('utf-8'))

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    system_name = json_data['system_name']
    system_id = get_solar_system_id_from_name(system_name)['solarSystemID']

    ### Getting sig data
    sig_data = get_sigs_internal()

    ### Loading the first to-visit
    visit_list = []
    visit_list.append(system_id)
    parent_data = {}

    visisted_list = []

    ### Loading from system name
    output = {}

    ### Iterate on all connections, deep search
    while len(visit_list) > 0:

        system_to_visit = visit_list.pop(0)
        if system_to_visit in visisted_list:
            continue

        #print("Iterating on " + str(system_to_visit))
        child_data = []

        ### Appending the data from the solar system id
        location_data = get_system_info(system_to_visit)
        location_name = location_data['solarSystemName']

        if location_name in sig_data['sig_output_system']:
            ### Okay this system has sigs...
            ### Lets work on those real quick

            sig_system_data = sig_data['sig_output_system'][location_name]
            for sig in sig_system_data:
                sig_data_iterate = sig_system_data[sig]
                if "sig_wormhole_data" in sig_data_iterate:

                    sig_wormhole_data = json.loads(sig_data_iterate['sig_wormhole_data'])
                    if "wormhole_destination" not in sig_wormhole_data:
                        continue

                    sig_wormhole_destination = sig_wormhole_data['wormhole_destination']

                    ### If this is a real thing, lets continue
                    if len(sig_wormhole_destination) <= 0:
                        continue

                    ### Okay, we have a valid destination...
                    ### Lets add this ID to our system
                    solar_system_id = get_solar_system_id_from_name(sig_wormhole_destination)

                    ### Checking for invalid systems
                    if len(solar_system_id) <= 0:
                        continue

                    ### Getting the final system ID
                    solar_system_id = solar_system_id['solarSystemID']

                    visit_list.append(solar_system_id)
                    child_data.append(sig_wormhole_destination)

        location_data['children_by_system'] = child_data
        output[location_data['solarSystemName']] = location_data
        visisted_list.append(system_to_visit)

    return throw_json_success(200, output)
