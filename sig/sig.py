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


### This primarily deals with the sig handling... ###

# Function for adding a sig to the trackboard
def add_sig():
    ##print("Adding a sig...")

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

    # Building data from the given info
    mydb = init_mysql("db_map")
    cursor = mydb.cursor()

    ### Creating the log entry
    log_entry = []
    log_entry_create = {"info": "Created sig", "user": json_data['character_id'],
                        "date": datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")}
    log_entry.append(log_entry_create)

    ### Converting to string
    log_entry = json.dumps(log_entry)

    insert = "INSERT INTO tb_sig (sig_id_num, sig_id_letter, sig_type, sig_name, sig_wormhole_data, sig_system, sig_age, sig_log, sig_mass, sig_display_lifespan) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    data = [json_data['sig_id_num'], json_data['sig_id_letter'], json_data['sig_type'], json_data['sig_name'], str(json_data['sig_wormhole_data']), json_data['sig_system'], json_data['sig_age'], log_entry, json_data['sig_mass'], json_data['sig_display_lifespan']]
    cursor.execute(insert, data)
    mydb.commit()

def get_sigs():
    ##print("Getting all sigs :O")

    # Getting the sig info
    json_input = request.data
    json_data = json.loads(json_input.decode('utf-8'))

    ### Authenticating the player
    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    # Building data from the given info
    mydb = init_mysql("db_map")
    cursor = mydb.cursor()

    select = "SELECT * FROM tb_sig WHERE sig_status = 0"
    cursor.execute(select)

    result_raw = cursor.fetchall()
    result = get_format_from_raw_full(result_raw, cursor)

    result = encode_datetime(result)

    return throw_json_success("success", result)

# Function for deleting a sig
def delete_sig():
    ##print("Deleting a sig...")

    # Getting the sig info
    json_input = request.data
    json_data = json.loads(json_input.decode('utf-8'))

    ### Authenticating the player
    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")

    # Building data from the given info
    mydb = init_mysql("db_map")
    cursor = mydb.cursor()

    sig_delete_list = json_data['sig_id_list']
    ##print(sig_delete_list)

    for sig_delete in sig_delete_list:
        if sig_delete_list[sig_delete] == 1:

            delete = "UPDATE tb_sig SET sig_status = 1 WHERE sig_id = %s"
            cursor.execute(delete, (sig_delete,))

    mydb.commit()

# Function for setting a sig to be the home sig

# Function for adding a sig to the trackboard
def add_sig_multiple():
    ##print("Adding LOTS of sigs")

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

    # Building data from the given info
    mydb = init_mysql("db_map")
    cursor = mydb.cursor()

    sig_list = json_data['sig_list']

    ### THIS IS GOING TO SUCK ###
    ### FIRST WE NEED TO GET ALL OF THE EXISTING SIGS FOR THIS SYSTEM ###
    GET_SELECTED_SYSTEM_SIGS = "SELECT * FROM tb_sig WHERE sig_system = %s AND sig_status = 0"
    cursor.execute(GET_SELECTED_SYSTEM_SIGS, (json_data['system'],))
    result = cursor.fetchall()
    result_full = get_format_from_raw_full(result, cursor)

    ### Building a map of the full sig to the sig id inside of the system this will make it easier to update later
    ### Okay, now lets see which one of these we need to update
    update_list = {}
    delete_list = {}
    sig_id_list = {}
    sig_list_full = {}

    for sig in result_full:
        sig_id = sig['sig_id']
        sig_num = str(sig['sig_id_num'])

        sig_letter = str(   sig['sig_id_letter'])

        sig_full_id = str(sig_letter)+"-"+str(sig_num)
        sig_id_list[sig_full_id] = sig_id
        sig_list_full[sig_full_id] = sig

        if sig_full_id in sig_list:
            update_list[sig_full_id] = 1
        else:
            delete_list[sig_full_id] = 1

    ### Okay, we have an update list and a list of all the new sigs...
    ### First, lets perform the inserts since that will be the easiest one...
    for sig in sig_list:

        ### Is this in the update? If so, we will skip
        if sig in update_list:
            ### We need to update it now...
            ### First thing, is lets check if we have more information to offer...
            current_sig = sig_list_full[sig]
            input_sig = sig_list[sig]

            input_scan_strength = input_sig['scan_strength']
            index_scan_break = input_scan_strength.index('.') + 2

            input_scan_strength = float(input_scan_strength[0:index_scan_break])
            current_scan_strength = float(current_sig['sig_scan_strength'])

            current_scan_type = current_sig['sig_type']
            current_scan_name = current_sig['sig_name']
            input_scan_type = input_sig['group']
            input_scan_name = input_sig['name']

            if len(input_scan_type) <= 1:
                input_scan_type = "Unknown"

            ### Checking if our scan strength is bigger
            #print("Comparing scan strength of " + str(current_scan_strength) + " , " + str(input_scan_strength))

            if current_scan_strength >= input_scan_strength:
                continue

            ### Checking
            if current_scan_strength == input_scan_strength and current_scan_type == input_scan_type and current_scan_name == input_scan_name:
                continue

            ### Checking if the new name is empty and the current name is not
            if (len(current_scan_type) > 0 and len(input_scan_type) < 0 ) or (len(current_scan_name) > 0 and len(input_scan_name) < 0 ):
                continue

            ### Checking if we STILL have nothing else to add...


            ### Okay we have more input scan strength
            ### Making the update
            sig_id = sig_id_list[sig]

            update_data = (input_scan_strength, input_scan_type, input_sig['name'], sig_id)
            UPDATE_EXISTING_SIG = "UPDATE tb_sig SET sig_scan_strength = %s, sig_type = %s, sig_name = %s WHERE sig_id = %s"
            cursor.execute(UPDATE_EXISTING_SIG, update_data)


            continue

        elif json_data['delete'] == "missing":
            ### Okay we have a sig that is NOT in the update list! And we are deleting the missing
            ### Lets delete this sig
            print("Deleting this sig of ID ")
            print(sig)

        ### Is a new sig
        ### Building the insert...
        sig_data = sig_list[sig]

        sig_id_letter = sig[0:3]
        sig_id_num = sig[4:]
        sig_group = sig_data['group']

        if len(sig_group) <= 1:
            sig_group = "Unknown"

        sig_age = 0
        if sig_group == "Wormhole":
            sig_age = 1440

        sig_name = sig_data['name']

        ### Formatting the scan strength
        scan_strength = 0
        scan_strength_string = sig_data['scan_strength']
        scan_strength_index = scan_strength_string.index(".") + 2
        scan_strength = scan_strength_string[0:scan_strength_index]

        ### Creating the log entry
        log_entry = []
        log_entry_create = {"info": "Created sig", "user": json_data['character_id'], "date": datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")}
        log_entry.append(log_entry_create)

        ### Converting to string
        log_entry = json.dumps(log_entry)

        insert_values = (sig_id_num, sig_id_letter, sig_group, sig_name, json_data['system'], sig_age, scan_strength, log_entry)
        INSERT_SIG = "INSERT INTO tb_sig (sig_id_num, sig_id_letter, sig_type, sig_name, sig_system, sig_age, sig_scan_strength, sig_log) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(INSERT_SIG, insert_values)

    ### Checking for those who will be deleted
    if json_data['delete'] == "missing":
        for sig in delete_list:
            DELETE_SIG = "DELETE FROM tb_sig WHERE sig_id = %s"
            cursor.execute(DELETE_SIG, (sig_id_list[sig],))

    ### Committing our inserts
    mydb.commit()

def edit_sig():
    ##print("Editing a sig and saving")

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

    # Building data from the given info
    mydb = init_mysql("db_map")
    cursor = mydb.cursor()

    ###############
    ###############
    ## Checking for wormhole data update...
    ###############
    ###############
    GET_SIG = "SELECT * FROM tb_sig WHERE sig_id = %s"
    cursor.execute(GET_SIG, (json_data['sig_id'],))
    result = get_format_from_raw_full(cursor.fetchall(), cursor)[0]
    ###print(result)
    existing_wormhole_data = json.loads(result['sig_wormhole_data'])
    input_wormhole_data = json.loads(json_data['sig_wormhole_data'])

    ###print(existing_wormhole_data)
    ###print(input_wormhole_data)

    set_age = result['sig_age']

    ### If we are setting the type and there WAS NOT A TYPE BEFORE, we NEED to update the age!
    if ("wormhole_type" not in existing_wormhole_data and "wormhole_type" in input_wormhole_data) or not (existing_wormhole_data['wormhole_type'] == input_wormhole_data['wormhole_type']):
        ### Okay time to get the age for this wormhole type...
        ### Note: If we are given nothing we want to set the age BACK to zero
        new_wormhole_type = input_wormhole_data['wormhole_type']

        if len(new_wormhole_type) <= 0:
            set_age = 0

        else:
            ### Okay, we've been given a NEW input...
            ### Lets get that age...
            set_age = 1440

    scan_strength = result['sig_scan_strength']


    insert = "UPDATE tb_sig SET sig_mass = %s, sig_display_lifespan = %s, sig_id_num = %s, sig_id_letter = %s, sig_type = %s, sig_name = %s, sig_wormhole_data = %s, sig_age = %s, sig_scan_strength = %s WHERE sig_id = %s"
    data = [json_data['sig_mass'], json_data['sig_display_lifespan'], json_data['sig_id_num'], json_data['sig_id_letter'], json_data['sig_type'], json_data['sig_name'],
            str(json_data['sig_wormhole_data']), set_age, scan_strength, json_data['sig_id']]

    ##print("EXECUTING...")

    cursor.execute(insert, data)
    mydb.commit()


