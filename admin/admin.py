# Importing libraries for use
# Importing flask
from flask import Flask
# Importing requests
# Importing JSON
import json

# Importing some helpers
import random
import requests

# Importing JSON
import json
import requests
import mysql.connector

# Getting the flask request object
from flask import request

# Loading other authentication code
from auth.auth import auth_character, get_access_token, auth_character_full
from auth.error import throw_json_error, throw_json_success
from config.init_mysql import init_mysql
from config.config import encode_datetime

from datetime import datetime, timedelta

def get_accounts():

    # Getting the sig info  
    json_input = request.data
    json_data = json.loads(json_input.decode('utf-8'))

    ### Authenticating the player
    # Authenticating our user
    auth = auth_character_full(json_data['character_id'], json_data['character_auth_code'], "admin")
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    # Authenticated
    connector = init_mysql("db_character")
    cursor = connector.cursor(dictionary=True)

    get_all_characters = "SELECT * FROM tb_character t1 INNER JOIN tb_character_type t2 ON t1.character_type = t2.character_type_id INNER JOIN db_auth.tb_character_sso t3 ON t3.character_entry_id = t1.character_sso_id INNER JOIN db_auth.tb_token t4 ON t4.token_id = t3.token_id"
    cursor.execute(get_all_characters)
    results = cursor.fetchall()
    results_output = encode_datetime(results)

    return results_output

def set_account_group():

    # Getting the request info
    json_input = request.data
    json_data = json.loads(json_input.decode('utf-8'))

    ### Authenticating the player
    # Authenticating our user
    auth = auth_character_full(json_data['character_id'], json_data['character_auth_code'], "admin")
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    # Authenticated
    connector = init_mysql("db_character")
    cursor = connector.cursor(dictionary=True)

    set_character_group = "UPDATE tb_character SET character_type = %s WHERE character_id = %s"
    cursor.execute(set_character_group,(json_data['character_type'],json_data['target_character']))
    
    connector.commit()