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

default_refresh_time = 60

# Function thats called externally
def get_location():
    # Getting the characters location
    # Checking how hardcore we are on updating
    json_input = request.data.decode('utf-8')
    json_data = json.loads(json_input)

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    # Lets get the options...
    refresh_type = "Normal"
    try:
        refresh_type = json_data['refresh_type']
    except:
        print("Not given a refresh type, using the normal default type")

    # Lets check how old the datapoint is. Older than the normal value will result in a refresh
    refresh_time = default_refresh_time

    if refresh_type == "Normal":
        refresh_time = default_refresh_time
    elif refresh_type == "Force":
        refresh_time = 0
    elif refresh_type == "Cache":
        refresh_time = 99999

    # We have our refresh time, lets get the location and its update time...
    mydb = init_mysql("db_character")
    cursor = mydb.cursor()

    location_get = "SELECT * FROM tb_character_location WHERE character_id = %s"
    cursor.execute(location_get, (json_data['character_id'],))
    result_raw = cursor.fetchall()

    ### Wait a second...
    ### Did this character ever get generated their location?
    ### If not, we need to generate it first...
    if len(result_raw) <= 0:
        print("Missing data for this character, generating the information...")
        result_raw = update_character_location(json_data['character_id'], json_data['character_auth_code'])
        result = get_format_from_raw_full(result_raw, cursor)[0]

        # Removing update time
        result['update_time'] = ""

        if len(result['wormhole_data']) > 0:
            result['wormhole_data'] = json.loads(result['wormhole_data'])
        else:
            result['wormhole_data'] = "{}"

        print(result)

        ### Getting the actual information we need data
        system_info = get_system_info(result['character_system_id'])
        result['data'] = system_info

        return throw_json_success("success", result)

    else:

        result = get_format_from_raw(result_raw, cursor)
        update_time = result['update_time']

        time_between = datetime.now() - update_time
        minutes = time_between.seconds / 60 / 60

        if (minutes < refresh_time):
            print("Refreshing our location information...")
            update_character_location(json_data['character_id'], json_data['character_auth_code'])

        location_get = "SELECT * FROM tb_character_location WHERE character_id = %s"
        cursor.execute(location_get, (json_data['character_id'],))
        result_raw = cursor.fetchall()
        result = get_format_from_raw_full(result_raw, cursor)[0]
        print(result)

        # Removing update time
        result['update_time'] = ""

        if len(result['wormhole_data']) > 0:
            result['wormhole_data'] = json.loads(result['wormhole_data'])
        else:
            result['wormhole_data'] = "{}"

        # Giving the result the location-based data that we are SUPPOSED to have...

        ### Getting the actual information we need data
        system_info = get_system_info(result['character_system_id'])
        result['data'] = system_info

        return throw_json_success("success", result)


def update_character_location(character_id, character_auth_code):
    print("Updating the location data for the given character")

    ### Data we are collecting
    solar_system_id = ""
    solar_system_name = ""
    docked = True
    structure_id = 0
    structure_name = "Unknown"
    ship_name = ""
    ship_custom_name = ""
    ship_id = ""

    # Given the character ID and character auth code, lets get (or generate) and access token
    sso_id = auth_character(character_id, character_auth_code)

    # Checking for error
    if sso_id == -1:
        return throw_json_error(500, "Invalid character authentication code")

    # Otherwise, lets get that token
    access_token = get_access_token(character_id, sso_id)
    # Now that we have an access token, lets begin working with it

    # First we will get the players exact location
    result_location = api_call_get("characters/" + str(character_id) + "/location/", {"character_id": character_id, "token": access_token})

    # Getting the solar system ID and the structure ID
    result_location_content = json.loads(result_location.content.decode('utf-8'))

    try:
        solar_system_id = result_location_content['solar_system_id']
    except KeyError as err:
        solar_system_id = 30000142

    try:
        structure_id = result_location_content['structure_id']

    except KeyError as err:
        docked = False

    # Next, we will get the players ship
    result_ship = api_call_get("characters/" + str(character_id) + "/ship/", {"character_id": character_id, "token": access_token})

    result_location_ship = json.loads(result_ship.content.decode('utf-8'))
    print(result_location_ship)
    ship_custom_name = result_location_ship['ship_name']
    ship_id = result_location_ship['ship_type_id']

    ### Getting static data
    solar_system_name = get_solar_system_name_from_id(solar_system_id)['solarSystemName']
    ship_name = get_ship_name_from_id(ship_id)['typeName']

    if docked:
        structure_name = get_station_name_from_id(structure_id)
        if len(structure_name) <= 0:
            structure_name = "Unknown"

    # Lets check; if this is a wormhole then there is an abundance of extra information we need to know...
    wormhole_data = ""
    if solar_system_name[0:1] == "J":
        # Lets get the wormhole data
        wormhole_data = get_wormhole_data_from_id(solar_system_id, solar_system_name)
        wormhole_data = json.dumps(wormhole_data)

    ### Final data set, lets create or update our entry
    ### Check if we have an entry
    mydb = init_mysql("db_character")
    cursor = mydb.cursor()
    statement_check = "SELECT character_id FROM tb_character_location WHERE character_id = %s"
    cursor.execute(statement_check, (character_id,))
    result_raw = cursor.fetchall()

    if len(result_raw) <= 0:
        # Time to create the entry
        # Creating insert data
        insert_data = [wormhole_data, docked, character_id, solar_system_name, solar_system_id, structure_name, structure_id, ship_name, ship_id, ship_custom_name]
        statement_insert = "INSERT INTO tb_character_location (wormhole_data, character_docked, character_id, character_system_name, character_system_id, character_structure_name, character_structure_id, character_ship_name, character_ship_id, character_ship_custom_name)" \
                           "VALUES" \
                           "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(statement_insert, insert_data)
        mydb.commit()

    else:
        # Update the entry
        statement_update = "UPDATE tb_character_location SET wormhole_data = %s, character_docked = %s, update_time = NOW(), character_system_name = %s, character_system_id = %s, character_structure_name = %s, character_structure_id = %s, character_ship_name = %s, character_ship_id = %s, character_ship_custom_name = %s WHERE character_id = %s"
        cursor.execute(statement_update, (wormhole_data, docked, solar_system_name, solar_system_id, structure_name, structure_id, ship_name, ship_id, ship_custom_name, character_id))

        mydb.commit()

    # Regardless:

    location_get = "SELECT * FROM tb_character_location WHERE character_id = %s"
    cursor.execute(location_get, (character_id,))
    result_raw = cursor.fetchall()
    return result_raw

# Function for aggregating wormhole information
def get_wormhole_data_from_id(system_id, system_name):
    print("Getting wormhole information...")

    # First, lets get our wormhole statics
    constellation_id = get_constellation_from_system_id(system_id)['constellationID']
    wormhole_class = get_wormhole_class(system_name)
    wormhole_statics = (constellation_id)

    output = {
        "statics": wormhole_statics,
        "constellationID": constellation_id,
        "wormhole_class": wormhole_class
    }

    return output