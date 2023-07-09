# Importing errors
from auth.error import throw_json_error

# Importing JSON
import json
import requests
import mysql.connector

from cachetools import cached, LRUCache, TTLCache
from datetime import datetime, timedelta

# Getting the flask request object
from flask import request

# Importing config
from config.config import api_call_get

from auth.auth import auth_character, get_access_token, auth_character_corporation
from auth.error import throw_json_error, throw_json_success

SEAT_TOKEN="Mwr8TLVLFXQiAg1TCgaqg9D0UGMLatY8"


def seat_character_api_call(character_id):
    url="https://seat.no-vacancies.space/api/v2/character/sheet/%s" % character_id
    httpResponse = requests.get(url, headers={"Accept": "application/json", "X-Token": SEAT_TOKEN})
    return httpResponse.json()

@cached(cache=TTLCache(maxsize=16384, ttl=86400))
def get_character_from_character_id(character_id):
    return seat_character_api_call(character_id)['data']

def get_pilots():
    # Getting the characters location
    # Checking how hardcore we are on updating
    json_input = request.data.decode('utf-8')
    json_data = json.loads(json_input)

    # Authenticating our user
    auth = auth_character(json_data['character_id'], json_data['character_auth_code'])
    if auth == -1:
        return throw_json_error(400, "Invalid authentication code")
    
    if not auth_character_corporation(json_data['character_id']):
        return throw_json_error(400, "Invalid authentication code")
    
    # First using seat to get the characters user id
    user_id = seat_character_api_call(json_data['character_id'])['data']['user_id']

    # Getting the associated characters now
    url="https://seat.no-vacancies.space/api/v2/users/%s" % user_id
    httpResponse = requests.get(url, headers={"Accept": "application/json", "X-Token": SEAT_TOKEN})

    associated_characters = (httpResponse.json()['data']['associated_character_ids'])
    output_associated_characters = list()

    for character_id in associated_characters:
        character_data = get_character_from_character_id(character_id)
        character_data['character_id'] = character_id
        output_associated_characters.append(character_data)

    return throw_json_success("success", {"pilots": output_associated_characters})
