# Importing JSON
import json
import mysql.connector
import re

from config.config import *

"""
These functions exist primary to convert different formats of fits to other formats
Below are the following formats we have available

1) ESI Raw; This is directly from the Eve ESI endpoint
2) EFT; This is the paste tool format

Examples:
"""
eft_example = "[Vedmak, Vedmak]\n\
Damage Control II\n\
Multispectrum Energized Membrane II\n\
Entropic Radiation Sink II\n\
Entropic Radiation Sink II\n\
Nanofiber Internal Structure II\n\
Medium Ancillary Armor Repairer\n\
\n\
Medium F-RX Compact Capacitor Booster\n\
50MN Quad LiF Restrained Microwarpdrive\n\
Warp Disruptor II\n\
Tracking Computer II\n\
\n\
Medium Energy Neutralizer II\n\
Small Energy Neutralizer II\n\
Small Energy Neutralizer II\n\
Heavy Entropic Disintegrator II\n\
\n\
Medium Polycarbon Engine Housing II\n\
Medium Hyperspatial Velocity Optimizer II\n\
Medium Hyperspatial Velocity Optimizer II\n\
\n\
\n\
\n\
Valkyrie II x5\n\
Hornet EC-300 x5\n\
\n\
Optimal Range Script x1\n\
Tracking Speed Script x1\n\
Navy Cap Booster 800 x11\n\
Baryon Exotic Plasma M x499\n\
Meson Exotic Plasma M x1461\n\
Occult M x802\n\
Mystic M x1500\n\
Nanite Repair Paste x122\n\
"

esi_raw_example = {
    "description": "",
    "fitting_id": 76109314,
    "items": [{
        "flag": "MedSlot2",
        "quantity": 1,
        "type_id": 2281
    }, {
        "flag": "MedSlot3",
        "quantity": 1,
        "type_id": 2281
    }, {
        "flag": "MedSlot6",
        "quantity": 1,
        "type_id": 4383
    }, {
        "flag": "LoSlot3",
        "quantity": 1,
        "type_id": 4405
    }, {
        "flag": "LoSlot4",
        "quantity": 1,
        "type_id": 4405
    }, {
        "flag": "LoSlot5",
        "quantity": 1,
        "type_id": 4405
    }, {
        "flag": "HiSlot0",
        "quantity": 1,
        "type_id": 16519
    }, {
        "flag": "HiSlot1",
        "quantity": 1,
        "type_id": 16519
    }, {
        "flag": "HiSlot2",
        "quantity": 1,
        "type_id": 16519
    }, {
        "flag": "HiSlot3",
        "quantity": 1,
        "type_id": 16519
    }, {
        "flag": "HiSlot4",
        "quantity": 1,
        "type_id": 16519
    }, {
        "flag": "MedSlot1",
        "quantity": 1,
        "type_id": 19227
    }, {
        "flag": "MedSlot5",
        "quantity": 1,
        "type_id": 19231
    }, {
        "flag": "LoSlot1",
        "quantity": 1,
        "type_id": 22291
    }, {
        "flag": "LoSlot2",
        "quantity": 1,
        "type_id": 22291
    }, {
        "flag": "MedSlot0",
        "quantity": 1,
        "type_id": 24417
    }, {
        "flag": "HiSlot5",
        "quantity": 1,
        "type_id": 24427
    }, {
        "flag": "RigSlot2",
        "quantity": 1,
        "type_id": 26088
    }, {
        "flag": "RigSlot0",
        "quantity": 1,
        "type_id": 26436
    }, {
        "flag": "RigSlot1",
        "quantity": 1,
        "type_id": 26440
    }, {
        "flag": "Cargo",
        "quantity": 8115,
        "type_id": 27395
    }, {
        "flag": "Cargo",
        "quantity": 8000,
        "type_id": 27423
    }, {
        "flag": "MedSlot4",
        "quantity": 1,
        "type_id": 28744
    }, {
        "flag": "DroneBay",
        "quantity": 4,
        "type_id": 31876
    }, {
        "flag": "LoSlot0",
        "quantity": 1,
        "type_id": 33824
    }],
    "name": "Rattlesnake",
    "ship_type_id": 17918
}

def init_mysql(database):
    my_db = mysql.connector.connect(
        host="localhost",
        user="vsadmin",
        passwd="dermdermderm99E!",
        database=database
    )

    return my_db

def convert_esi_to_eft(input):
    mydb = init_mysql("db_static")
    low, mid, high, rig, drone, cargo = [], [], [], [], [], []
    for entry in input['items']:
        name = convert_invtype_to_name(entry['type_id'], mydb)
        quantity = entry['quantity']
        quantity_name = name + " x" + str(quantity)
        if "LoSlot" in entry['flag']:
            low.append(name)
        elif "MedSlot" in entry['flag']:
            mid.append(name)
        elif "HiSlot" in entry['flag']:
            high.append(name)
        elif "RigSlot" in entry['flag']:
            rig.append(name)
        elif "DroneBay" in entry['flag']:
            drone.append(quantity_name)
        else:
            cargo.append(quantity_name)

    line_data = []
    line_data.append("[" + convert_invtype_to_name(input['ship_type_id'], mydb) + ", " + input["name"] + "]\n")
    for slot in low:
        line_data.append(slot + "\n")
    line_data.append('\n')
    for slot in mid:
        line_data.append(slot + "\n")
    line_data.append('\n')
    for slot in high:
        line_data.append(slot + "\n")
    line_data.append('\n')
    for slot in rig:
        line_data.append(slot + "\n")
    line_data.append('\n')
    line_data.append('\n')
    line_data.append('\n')
    for slot in drone:
        line_data.append(slot + "\n")
    line_data.append('\n')
    for slot in cargo:
        line_data.append(slot + "\n")
    
    output = "".join(line_data)
    return output

def convert_eft_to_esi(input):
    """ Splitting all of the spaces """
    split_input = input.split("\n")

    """ Grabbing the title & name """
    title = split_input[0]
    ship_name, ship_title = (title.split(", "))
    ship_name, ship_title = ship_name[1:], ship_title[:-1]
    
    slots = ["LoSlot","MedSlot","HiSlot","RigSlot","","","DroneBay","Cargo"]
    current_slot_index = 0
    slot_count = 0

    mydb = init_mysql("db_static")

    """ Building the control data """
    items = []

    """ Attempting to process each line for fitting. """
    for line in split_input[1:]:
        if len(line) == 0:
            current_slot_index += 1
            slot_count = 0
            continue


        item = line
        quantity = re.search(' x[0-9]', line)
        if quantity != None:
            # Valid quantity sequence
            d = quantity.span()
            quantity = line[d[0] + 2:]
            item = line[:d[0]]
        else:
            quantity = 1

        typeID = convert_name_to_invtype(item, mydb)
        data = {
            "flag": str(slots[current_slot_index]) + str(slot_count),
            "quantity": int(quantity),
            "type_id": int(typeID)
        }
        items.append(data)

        slot_count += 1

    data = {
        "description": "",
        "fitting_id": 0,
        "items": items,
        "name": ship_title,
        "ship_type_id": int(convert_name_to_invtype(ship_name, mydb))
    }

    return data

def perform_tests():
    eft_convert = convert_eft_to_esi(eft_example)
    esi_convert = convert_esi_to_eft(esi_raw_example)
    eft_reconvert = (convert_esi_to_eft(eft_convert))
    esi_reconvert = (convert_eft_to_esi(esi_convert))