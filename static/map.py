### File dealing with static data transmissions with the map
# Importing errors
from auth.error import throw_json_error

# Importing JSON
import json

# Importing config
from config.config import api_call_get, get_format_from_raw, get_format_from_raw_full

from auth.auth import auth_character, get_access_token
from config.init_mysql import init_mysql

def get_region_name_from_region_id(regionID):

    mydb = init_mysql("db_static")
    cursor = mydb.cursor()

    select_solar_system_name = "SELECT regionName FROM mapregions WHERE regionID = %s"
    cursor.execute(select_solar_system_name, (regionID,))
    result_raw = cursor.fetchall()

    # Checking for null
    if len(result_raw) <= 0:
        return result_raw

    result = get_format_from_raw(result_raw, cursor)
    return result

def get_region_id_from_solar_system_id(solar_system_id):
    mydb = init_mysql("db_static")
    cursor = mydb.cursor()

    select_solar_system_name = "SELECT regionID FROM mapsolarsystems WHERE solarSystemID = %s"
    cursor.execute(select_solar_system_name, (solar_system_id,))
    result_raw = cursor.fetchall()

    # Checking for null
    if len(result_raw) <= 0:
        return result_raw

    result = get_format_from_raw(result_raw, cursor)
    return result

def get_constellation_name_from_constellation_id(constellation_id):

    mydb = init_mysql("db_static")
    cursor = mydb.cursor()

    select_solar_system_name = "SELECT constellationName FROM mapconstellations WHERE constellationID = %s"
    cursor.execute(select_solar_system_name, (constellation_id,))
    result_raw = cursor.fetchall()

    # Checking for null
    if len(result_raw) <= 0:
        return result_raw

    result = get_format_from_raw(result_raw, cursor)
    return result

def get_solar_system_name_from_id(solar_system_id):
    mydb = init_mysql("db_static")
    cursor = mydb.cursor()

    select_solar_system_name = "SELECT solarSystemName FROM mapsolarsystems WHERE solarSystemID = %s"
    cursor.execute(select_solar_system_name, (solar_system_id,))
    result_raw = cursor.fetchall()

    # Checking for null
    if len(result_raw) <= 0:
        return result_raw

    result = get_format_from_raw(result_raw, cursor)
    return result

def get_solar_system_id_from_name(solar_system_name):
    mydb = init_mysql("db_static")
    cursor = mydb.cursor()

    select_solar_system_name = "SELECT solarSystemID FROM mapsolarsystems WHERE solarSystemName = %s"
    cursor.execute(select_solar_system_name, (solar_system_name,))
    result_raw = cursor.fetchall()

    # Checking for null
    if len(result_raw) <= 0:
        return result_raw

    result = get_format_from_raw(result_raw, cursor)
    return result

def get_constellation_from_system_id(system_id):
    # Getting our constellation ID from system ID
    mydb = init_mysql("db_static")
    cursor = mydb.cursor()

    select_solar_system_name = "SELECT constellationID FROM mapsolarsystems WHERE solarSystemID = %s"
    cursor.execute(select_solar_system_name, (system_id,))
    result_raw = cursor.fetchall()

    # Checking for null
    if len(result_raw) <= 0:
        return result_raw

    result = get_format_from_raw(result_raw, cursor)
    return result

def get_wormhole_class(system_name):
    # Getting wormhole statics from a constellation

    # Getting our constellation ID from system ID
    mydb = init_mysql("db_static")
    cursor = mydb.cursor()

    select = "select solarsystemname,wormholeclassid from mapsolarsystems join maplocationwormholeclasses on regionid=locationid WHERE solarsystemname = %s"
    cursor.execute(select, (system_name,))
    result_raw = cursor.fetchall()

    output = 'C' + str(result_raw[0][1])

    return output

def get_wormhole_statics(constellation_id, solarSystemName):
    # Getting wormhole statics from a constellation

    # Getting our constellation ID from system ID
    mydb = init_mysql("db_static")
    cursor = mydb.cursor()

    # Checking if it is a fucking shattered
    if "J0" in solarSystemName:
        ### Okay we are getting the shattered statics...
        print("Getting the shattered statics...")

    else:

        select_query = "SELECT staticmap.*, invtypes.typeName, invtypes.typeID FROM db_static.staticmap INNER JOIN invtypes WHERE constellationID = %s AND staticmap.typeID = invtypes.typeID"
        cursor.execute(select_query, (constellation_id,))
        result_raw = cursor.fetchall()

        # Checking for null
        if len(result_raw) <= 0:
            return result_raw

        result = get_format_from_raw_full(result_raw, cursor)

    static_list = []

    for entry in result:
        static_list.append(entry['typeID'])


    static_output_list = {}
    static_data = []
    static_word_text = "Static "
    count = 0

    # For each entry in our static list, lets get the actual wormhole information
    for entry in static_list:
        select = "SELECT * FROM db_static.wormholestaticinfo WHERE typeID = %s"
        cursor.execute(select, (entry,))
        results_raw = cursor.fetchall()

        results = get_format_from_raw(results_raw, cursor)
        static_data.append(results)

        if count == 0:
            static_word_text = static_word_text + results['destination']
        else:
            static_word_text = static_word_text + "/" + results['destination']

        count = count + 1

    static_output_list['statics'] = static_data
    static_output_list['display_text'] = static_word_text
    return static_output_list

def get_security_string_from_system_id(system_id):
    mydb = init_mysql("db_static")
    cursor = mydb.cursor()

    select_solar_system_name = "SELECT security, solarSystemName FROM mapsolarsystems WHERE solarSystemID = %s"
    cursor.execute(select_solar_system_name, (system_id,))
    result_raw = cursor.fetchall()

    # Checking for null
    if len(result_raw) <= 0:
        return result_raw

    result = get_format_from_raw(result_raw, cursor)
    security = float(result['security'])
    name = result['solarSystemName']
    if name[0:1] == 'J':
        return "JS"
    elif security >= 0.5:
        return "HS"
    elif security > 0.0:
        return "LS"
    else:
        return "NS"

def get_wormhole_effect_from_system_id(solar_system_id):
    mydb = init_mysql("db_static")
    cursor = mydb.cursor()

    select_solar_system_name = "SELECT wormholeEffect FROM wormholeeffect WHERE solarSystemID = %s"
    cursor.execute(select_solar_system_name, (solar_system_id,))
    result_raw = cursor.fetchall()

    if len(result_raw) <= 0:
        return "None"
    else:
        return result_raw[0][0]



# This function gets us the information dealing with a solar system, by that solar system's ID
# This is an important function thats used for rendering purposes across all screens
# This will only pull from static data, so NO ESI integration here!
def get_system_info(solar_system_id):

    #print("Loading system information from " + str(solar_system_id))

    # Given that we have recieved a solar system id, lets convert that into something more useful
    output = {}

    output['solarSystemID'] = solar_system_id
    output['constellationID'] = get_constellation_from_system_id(solar_system_id)['constellationID']
    output['constellationName'] = get_constellation_name_from_constellation_id(output['constellationID'])['constellationName']
    output['solarSystemName'] = get_solar_system_name_from_id(solar_system_id)['solarSystemName']
    output['regionID'] = get_region_id_from_solar_system_id(solar_system_id)['regionID']
    output['regionName'] = get_region_name_from_region_id(output['regionID'])['regionName']
    output['securityClass'] = get_security_string_from_system_id(solar_system_id)
    output['wormholeEffect'] = get_wormhole_effect_from_system_id(solar_system_id);

    ### Getting notes for this location, IF there is indeed notes for it...

    ### Assembling wormhole data
    if output['solarSystemName'][0:1] == "J" and len(output['solarSystemName']) == 7 and output['securityClass'] == "JS":
        wormhole_output = {}
        wormhole_output['static'] = get_wormhole_statics(output['constellationID'], output['solarSystemName'])
        wormhole_output['class'] = get_wormhole_class(output['solarSystemName'])
        output['wormhole'] = wormhole_output


    ### Assembling both signature, note, and meta data

    return output