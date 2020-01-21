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

from datetime import datetime, timedelta

# Getting the flask request object
from flask import request
from auth.auth import auth_character, get_access_token
from auth.error import throw_json_error, throw_json_success
from config.init_mysql import init_mysql
from config.config import *

# Getting the flask request object
from flask import request

def get_search():
    print("Getting all of the search data")

    # Getting the sig info
    json_input = request.data
    json_data = json.loads(json_input.decode('utf-8'))

    ### Authenticating the player
    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    connector = init_mysql("db_map")
    cursor = connector.cursor()

    SELECT_ALL_SEARCH = "SELECT * FROM tb_search"
    cursor.execute(SELECT_ALL_SEARCH)

    result = cursor.fetchall()
    result_encoded = get_format_from_raw_full(result)
    throw_json_success("Success", result_encoded)


def add_search():
    print("Adding a new search entry")

    # Getting the sig info
    json_input = request.data
    json_data = json.loads(json_input.decode('utf-8'))

    ### Authenticating the player
    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    connector = init_mysql("db_map")
    cursor = connector.cursor()

    # Adding a new sig
    ADD_NEW_SEARCH = "INSERT INTO tb_search (search_name, search_character) VALUES (%s, %s)"
    cursor.execute(ADD_NEW_SEARCH, (json_data['search_name'], json_data['character_id']))

    connector.commit()

    throw_json_success("Success", {})