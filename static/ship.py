### File dealing with static data transmissions with the map
# Importing errors
from auth.error import throw_json_error

# Importing JSON
import json

# Importing config
from config.config import api_call_get, get_format_from_raw

from auth.auth import auth_character, get_access_token
from config.init_mysql import init_mysql

def get_ship_name_from_id(ship_id):
    mydb = init_mysql("db_static")
    cursor = mydb.cursor()

    select_ship = "SELECT * FROM invtypes WHERE typeID = %s"
    cursor.execute(select_ship, (ship_id,))
    result_raw = cursor.fetchall()

    # Checking for null
    if len(result_raw) <= 0:
        return result_raw

    result = get_format_from_raw(result_raw, cursor)
    return result