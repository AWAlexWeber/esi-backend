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

from auth.auth import auth_character, get_access_token
from auth.error import throw_json_error, throw_json_success

# Importing extras
from .convert import *

# Function thats called externally
def get_eve_all():
    json_input = request.data.decode('utf-8')
    json_data = json.loads(json_input)

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    character_id, character_auth_code = json_data['character_id'], json_data['character_auth_code']

    # Attempting to load all of the eve fits associated with this account
    # Given the character ID and character auth code, lets get (or generate) and access token
    sso_id = auth_character(character_id, character_auth_code)

    # Checking for error
    if sso_id == -1:
        return throw_json_error(500, "Invalid character authentication code")

    # Otherwise, lets get that token
    access_token = get_access_token(character_id, sso_id)
    # Now that we have an access token, lets begin working with it

    # First we will get the players exact location
    result_fit = api_call_get("characters/" + str(character_id) + "/fittings/", {"character_id": character_id, "token": access_token})

    # Getting the solar system ID and the structure ID
    result_fit_content = json.loads(result_fit.content.decode('utf-8'))

    # Converting each fit over to EFT style fitting
    output_eft = []
    for fit in result_fit_content:
        output_eft.append(convert_esi_to_eft(fit))

    return throw_json_success("success", output_eft)

def add_eft_fit():
    json_input = request.data.decode('utf-8')
    json_data = json.loads(json_input)

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    character_id, character_auth_code = json_data['character_id'], json_data['character_auth_code']

    # Converting from EFT to ESI
    eft_fit = json_data['eft_fit']
    esi_fit = convert_eft_to_esi(eft_fit)
    esi_fit_str = json.dumps(esi_fit)
    fit_attributes = json.dumps(json_data['fit_attributes'])
    fit_title = json_data['fit_title']

    # Saving it into our database
    mydb = init_mysql("db_fitting")
    cursor = mydb.cursor()

    skill_type_id, skill_type_name = (calculate_fit_skill_reqs(esi_fit, mydb))

    fitting_add = "INSERT INTO tb_fitting (fit_attributes, fit_esi, fit_eft, character_id, fit_title, fit_skillreqs_typeid, fit_skillreqs_typename) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(fitting_add, (fit_attributes, esi_fit_str, eft_fit, json_data['character_id'], fit_title, json.dumps(skill_type_id), json.dumps(skill_type_name)))

    mydb.commit()
    return throw_json_success("success", "Fit inserted")

def calculate_fit_skill_reqs(esi_fit, mydb):
    cursor = mydb.cursor()

    # Internal function that calculates total skill requirements for a fit
    items = esi_fit['items']
    ship_type_id = esi_fit['ship_type_id']

    # Adding our ship type
    items.append({'type_id': ship_type_id})

    skill_reqs_id = {}
    skill_reqs_name = {}

    for item in items:
        # Getting the database entry for this item
        get_skill_req = "SELECT * FROM db_static.skillReqsData WHERE typeID = %s"
        cursor.execute(get_skill_req, (item['type_id'], ))
        results = cursor.fetchall()

        if len(results) <= 0:
            continue

        results = results[0]
        
        skills_name = json.loads(results[2])
        skills_id = json.loads(results[3])

        for skill in skills_name:
            if skill in skill_reqs_name:
                skill_reqs_name[skill] = max(skills_name[skill], skill_reqs_name[skill])
            else:
                skill_reqs_name[skill] = skills_name[skill]

        for skill in skills_id:
            if skill in skill_reqs_id:
                skill_reqs_id[skill] = max(skills_id[skill], skill_reqs_id[skill])
            else:
                skill_reqs_id[skill] = skills_id[skill]

    return (skill_reqs_id, skill_reqs_name)

