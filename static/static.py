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

def get_all_wormholes():

    ### Getting all of the possible wormhole types and all of their associative datapoints
    #print("Getting all static wormhole data values")

    ### Getting data
    connector = init_mysql("db_static")
    cursor = connector.cursor()

    select = "SELECT * FROM wormholestaticinfo"
    cursor.execute(select)

    result_raw = cursor.fetchall()
    result = get_format_from_raw_full(result_raw, cursor)

    return throw_json_success("Success", result)

def get_all_systems():

    ### Getting all of the possible wormhole types and all of their associative datapoints
    #print("Getting all static wormhole data values")

    ### Getting data
    connector = init_mysql("db_static")
    cursor = connector.cursor()

    select = "SELECT solarSystemName, security FROM mapsolarsystems"
    cursor.execute(select)

    result_raw = cursor.fetchall()
    result = get_format_from_raw_full(result_raw, cursor)

    return throw_json_success("Success", result)