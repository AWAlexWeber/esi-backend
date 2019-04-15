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

# Getting the flask request object
from flask import request


### This primarily deals with the sig handling... ###

# Function for adding a sig to the trackboard
def add_sig():
    print("Adding a sig...")

    # Getting the sig info
    json_input = request.data
    json_data = json.loads(json_input)

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    # Building data from the given info
    mydb = init_mysql("db_map")
    cursor = mydb.cursor()

    insert = "INSERT INTO tb_sig (sig_id_num, sig_id_letter, sig_type, sig_name, sig_wormhole_data, sig_system) VALUES (%s, %s, %s, %s, %s, %s)"
    data = [json_data['sig_id_num'], json_data['sig_id_letter'], json_data['sig_type'], json_data['sig_name'], "{}", json_data['sig_system']]
    cursor.execute(insert, data)
    mydb.commit()

