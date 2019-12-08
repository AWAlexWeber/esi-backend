### Settings file
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

def init_setting_file(character_id, cursor, mydb):
    insert = "INSERT INTO tb_character_setting (character_id, wormhole_mask) VALUES (%s, '[]')"
    cursor.execute(insert, (character_id,))
    mydb.commit()

def delete_wormhole_mask():
    print("Getting character settings")

    ### Authenticating user
    json_input = request.data
    json_data = json.loads(json_input.decode('utf-8'))

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    mydb = init_mysql("db_character")
    select = "SELECT * FROM tb_character_setting WHERE character_id = %s"
    cursor = mydb.cursor()
    cursor.execute(select, (json_data['character_id'],))
    result_raw = cursor.fetchall()
    result = get_format_from_raw(result_raw, cursor)
    print(result)

    wormhole_mask = json.loads(result['wormhole_mask'])
    ### Getting the index we need to delete
    index_track = 0
    for entry in wormhole_mask:
        system_name = entry['systemName']
        if system_name == json_data['system_name']:
            break
        index_track = index_track + 1

    wormhole_mask.pop(0)
    wormhole_mask = json.dumps(wormhole_mask)

    update = "UPDATE tb_character_setting SET wormhole_mask = %s WHERE character_id = %s"
    cursor.execute(update, (wormhole_mask, json_data['character_id']))
    mydb.commit()

    select = "SELECT * FROM tb_character_setting WHERE character_id = %s"
    cursor.execute(select, (json_data['character_id'],))

    result_raw = cursor.fetchall()
    result = get_format_from_raw(result_raw, cursor)
    result['wormhole_mask'] = json.loads(result['wormhole_mask'])

    return throw_json_success(200, result)


def add_wormhole_mask():
    print("Getting character settings")

    ### Authenticating user
    json_input = request.data
    json_data = json.loads(json_input.decode('utf-8'))
    print(json_data)

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    mydb = init_mysql("db_character")
    select = "SELECT * FROM tb_character_setting WHERE character_id = %s"
    cursor = mydb.cursor()
    cursor.execute(select, (json_data['character_id'],))
    result_raw = cursor.fetchall()
    result = get_format_from_raw(result_raw, cursor)
    print(result)
    wormhole_mask = json.loads(result['wormhole_mask'])

    ### Appending the system by system name
    system_name = json_data['system_name']
    system_nickname = json_data['system_nickname']
    system_id = get_solar_system_id_from_name(system_name)

    ### Using this, we are rebuilding it
    new_tag = {"systemName": system_name, "systemID": system_id, "systemNickname": system_nickname}
    wormhole_mask.append(new_tag)
    wormhole_mask = json.dumps(wormhole_mask)
    print(wormhole_mask)

    update = "UPDATE tb_character_setting SET wormhole_mask = %s WHERE character_id = %s"
    cursor.execute(update, (wormhole_mask, json_data['character_id']))
    mydb.commit()

    select = "SELECT * FROM tb_character_setting WHERE character_id = %s"
    cursor.execute(select, (json_data['character_id'],))

    result_raw = cursor.fetchall()
    result = get_format_from_raw(result_raw, cursor)
    result['wormhole_mask'] = json.loads(result['wormhole_mask'])

    return throw_json_success(200, result)


def get_settings():
    print("Getting character settings")

    ### Authenticating user
    json_input = request.data
    json_data = json.loads(json_input.decode('utf-8'))

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    mydb = init_mysql("db_character")
    select = "SELECT * FROM tb_character_setting WHERE character_id = %s"
    cursor = mydb.cursor()
    cursor.execute(select, (json_data['character_id'],))
    result_raw = cursor.fetchall()

    if len(result_raw) <= 0:
        init_setting_file(json_data['character_id'], cursor, mydb)

        cursor.execute(select, (json_data['character_id'],))

        result_raw = cursor.fetchall()
        result = get_format_from_raw(result_raw, cursor)
        result['wormhole_mask'] = json.loads(result['wormhole_mask'])
        return throw_json_success(200, result)

    else:
        result = get_format_from_raw(result_raw, cursor)
        result['wormhole_mask'] = json.loads(result['wormhole_mask'])
        return throw_json_success(200, result)



