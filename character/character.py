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

from auth.auth import auth_character, get_access_token
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
    print(result_raw)

    result_full = get_format_from_raw(result_raw, cursor)

    return throw_json_success("Success", result_full)



