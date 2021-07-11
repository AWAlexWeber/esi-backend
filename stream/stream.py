# Importing errors
from auth.error import throw_json_error

# Importing JSON
import json
import requests
import mysql.connector

from datetime import datetime, timedelta

# Getting the flask request object
from flask import request

from config.config import *
from config.init_mysql import *

from auth.auth import auth_character, get_access_token
from auth.error import throw_json_error, throw_json_success

def get_new_token():
    print("Getting a new token for accessing the stream")

    # Getting the characters location
    # Checking how hardcore we are on updating
    json_input = request.data.decode('utf-8')
    json_data = json.loads(json_input)

    ### Authenticating the token...
    connector = init_mysql("db_cctv")
    cursor = connector.cursor()

    print("Loading from ")
    print(json_data)

    ### AND cctv_init < (NOW() - INTERVAL 5 MINUTE
    GET_TOKEN = "SELECT * FROM db_cctv.tb_cctv_token WHERE cctv_use_status = 0 AND cctv_token_code = %s AND cctv_init_character = %s"
    cursor.execute(GET_TOKEN, (json_data['stream_access_code'], json_data['character_id']))

    result = cursor.fetchall()

    ### Checking for sizes
    if (len(result) <= 0):
        return throw_json_error(500, "Invalid token or character ID")

    result_full = get_format_from_raw_full(result, cursor)[0]

    ### Checking for sizes
    if (len(result_full) <= 0):
        ### Invalid token
        return throw_json_error(500, "Invalid token or character ID")

    ### Okay, if we made it this far we are good
    ### Lets first set this token to used
    UPDATE_TOKEN_USE_STATUS = "UPDATE db_cctv.tb_cctv_token SET cctv_use_status = 1 WHERE cctv_token_code = %s"
    cursor.execute(UPDATE_TOKEN_USE_STATUS, (json_data['stream_access_code'],))

    ### Okay, now we are going to insert this new stream into our system
    ### Once we have done that, we are going to go ahead and generate the authentication token
    ### Then we are going to insert this stream into our system
    access_token = gen_random_string(256)

    INSERT_NEW_STREAM = "INSERT INTO db_cctv.tb_cctv (cctv_auth, cctv_name, cctv_character_id) VALUES (%s, %s, %s)"
    cursor.execute(INSERT_NEW_STREAM, (access_token, json_data['stream_title'], json_data['character_id']))

    connector.commit()

    return throw_json_success("Success", access_token)

def get_new_auth():
    print("Getting a new auth code for the stream data")

    # Getting the characters location
    # Checking how hardcore we are on updating
    json_input = request.data.decode('utf-8')
    json_data = json.loads(json_input)

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    ### Okay, we will now proceed to generate a new authentication token....
    new_token = gen_random_string(8)

    ### Inserting into our database
    connector = init_mysql("db_cctv")
    cursor = connector.cursor()

    INSERT_CCTV_TOKEN = "INSERT INTO tb_cctv_token (cctv_token_code, cctv_init_character) VALUES (%s, %s)"
    cursor.execute(INSERT_CCTV_TOKEN, (new_token, json_data['character_id']))

    connector.commit()

    return throw_json_success("Success", new_token)

def get_current_tokens():
    print("Getting all available tokens")

    json_input = request.data.decode('utf-8')
    json_data = json.loads(json_input)

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    ### Connecting with our database
    connector = init_mysql("db_cctv")
    cursor = connector.cursor()

    SELECT_TOKEN = "SELECT * FROM tb_cctv_token"
    cursor.execute(SELECT_TOKEN, )

    result = list(cursor.fetchall())
    new_result = []
    for element in result:
        new_element = []
        for value in element:
            if isinstance(value, datetime.datetime):
                value = date_to_string(value)
            new_element.append(value)

        new_element = tuple(new_element)
        new_result.append(new_element)

    print(new_result)
    return throw_json_success("Success", new_result)

def delete_tokens():
    print("Deleting given token")

    json_input = request.data.decode('utf-8')
    json_data = json.loads(json_input)

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    token_ids = json_data['token_delete_array']
    ### Converting
    for token_id in token_ids:
        print(token_id)
        ### Connecting with our database
        connector = init_mysql("db_cctv")
        cursor = connector.cursor()

        DELETE_CCTV_TOKEN = "DELETE FROM tb_cctv_token WHERE cctv_token_id = %s"
        cursor.execute(DELETE_CCTV_TOKEN, (token_id,))

        connector.commit()

    SELECT_TOKEN = "SELECT * FROM tb_cctv_token"
    cursor.execute(SELECT_TOKEN, )

    result = list(cursor.fetchall())
    new_result = []
    for element in result:
        new_element = []
        for value in element:
            if isinstance(value, datetime.datetime):
                value = date_to_string(value)
            new_element.append(value)

        new_element = tuple(new_element)
        new_result.append(new_element)

    print(new_result)
    return throw_json_success("Success", new_result)