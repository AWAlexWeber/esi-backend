### Python file for all character-based account calls...
## Mostly updating, editing, etc...
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

from auth.auth import auth_character, get_access_token, import_skills
from auth.error import throw_json_error, throw_json_success
# Primary file for dealing with location

def get_character():
    json_input = request.data.decode('utf-8')
    json_data = json.loads(json_input)

    ### Authenticating the player
    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    ### Okay if we have authenticated, lets get all of the relevant information
    get_character_query = "SELECT tb_character_type.*, tb_character.character_id, tb_character.character_type FROM tb_character INNER JOIN tb_character_type WHERE tb_character.character_id = %s AND character_type_id = character_type"

    ### Connecting
    mydb = init_mysql("db_character")
    cursor = mydb.cursor()

    cursor.execute(get_character_query, (json_data['character_id'], ))

    result_raw = cursor.fetchall()
    print("Character fetch raw", json_data)
    print(result_raw)

    result_full = get_format_from_raw(result_raw, cursor)

    return throw_json_success("Success", result_full)

def import_skills(character_id, character_auth_code):
    # This should be ran as part of the auth process but it can also be triggered normally
    # Given the character ID and character auth code, lets get (or generate) and access token
    sso_id = auth_character(character_id, character_auth_code)

    # Checking for error
    if sso_id == -1:
        return throw_json_error(500, "Invalid character authentication code")

    # Otherwise, lets get that token
    access_token = get_access_token(character_id, sso_id)

    # Next, we will get the players ship
    result_skill = api_call_get("characters/" + str(character_id) + "/skills/", {"character_id": character_id, "token": access_token})

    print(result_skill)



