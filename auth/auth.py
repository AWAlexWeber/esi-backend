# Importing some helpers
import random
import requests
import os
from datetime import datetime, timedelta

# Datetime
import base64

# Importing the mysql connector
import mysql.connector

# Importing errors
from auth.error import throw_json_error
from config.config import convert_invtype_to_name, get_format_from_raw, get_format_from_raw_full

# Getting the flask request object
from flask import request

# Importing JSON
import json

# Hasing
import hashlib

### Importing our config
from config.config import gen_random_string, api_call_get

# Primary authentication file
# Some static values
scope = os.environ["CLIENT_SCOPE"]
redirect = "http://vs-eve.com/auth"
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']

token_expiration = 20

# Function for authenticating the character ID against the auth code as well as a group permissions set
def auth_character_full(character_id, character_auth_code, permission_set):
    if (auth_character(character_id, character_auth_code) == -1):
        return -1

    # Checking group permissions
    my_db = mysql.connector.connect(
        host="localhost",
        user=os.environ['MYSQL_SERVER_USERNAME'],
        passwd=os.environ['MYSQL_SERVER_PASSWORD'],
        database="db_character"
    )

    try:
        permission_set = "%" + permission_set + "%"
        my_cursor = my_db.cursor(buffered=True)
        print(character_id, permission_set)
        get_character_statement = "SELECT * FROM tb_character INNER JOIN tb_character_type WHERE tb_character.character_type = tb_character_type.character_type_id AND character_permission_access LIKE %s AND tb_character.character_id = %s"
        sql_values = (permission_set, character_id)
        my_cursor.execute(get_character_statement, sql_values)

        result = my_cursor.fetchall()
        print(result)

        if len(result) <= 0:
            print("Error, unable to validate authentication code")
            return -1

        else:
            return result[0][0]

    except mysql.connector.Error as err:
        print("Something went wrong (get code): {}".format(err))
        return -1

# Function for authenticating the character ID against character auth code
def auth_character(character_id, character_auth_code):
    print("Authenticating character")

    my_db = mysql.connector.connect(
        host="localhost",
        user=os.environ['MYSQL_SERVER_USERNAME'],
        passwd=os.environ['MYSQL_SERVER_PASSWORD'],
        database="db_auth"
    )

    try:
        my_cursor = my_db.cursor(buffered=True)
        get_character_statement = "SELECT character_sso_id FROM db_character.tb_character WHERE character_id = %s AND character_auth_code = %s"
        sql_values = (character_id, character_auth_code)
        my_cursor.execute(get_character_statement, sql_values)

        result = my_cursor.fetchall()

        if len(result) <= 0:
            print("Error, unable to validate authentication code")
            return -1

        else:
            return result[0][0]



    except mysql.connector.Error as err:
        print("Something went wrong (get code): {}".format(err))
        return -1


# Function for getting and updating the access token
def get_access_token(character_id, sso_id):
    print("Getting a new access token, or updating... (from " + str(character_id) + " and " + str(sso_id) + ")")

    my_db = mysql.connector.connect(
        host="localhost",
        user=os.environ['MYSQL_SERVER_USERNAME'],
        passwd=os.environ['MYSQL_SERVER_PASSWORD'],
        database="db_auth"
    )

    print("First getting the token from the SSO id")
    try:
        my_cursor = my_db.cursor(buffered=True)

        get_token_id = "SELECT token_id FROM tb_character_sso WHERE character_entry_id = %s AND character_id = %s"
        my_cursor.execute(get_token_id, (sso_id, character_id))

        result = my_cursor.fetchall()[0][0]
        token_id = result
        print("Recieved token id of " + str(result))

    except mysql.connector.Error as err:
        print("1: Something went wrong (get code): {}".format(err))
        return -1

    try:
        cursor = my_db.cursor(buffered=True)

        # First lets get the expiration time of this token...
        # More than 20 minutes and its time to refresh the token
        # We will also delete it since its no longer useful anyways
        get_access_token = "SELECT * FROM tb_token WHERE token_id = %s"
        cursor.execute(get_access_token, (token_id,))

        result_raw = cursor.fetchall()
        result = get_format_from_raw_full(result_raw, cursor)[0]

        # Lets check; have we updated recently?
        date = result['init_date']
        time_between = datetime.now() - date
        minutes = time_between.seconds/60

        # Are we too old?
        if minutes>token_expiration:
            print("Date is too old, generating a new token!")
            return refresh_access_token(token_id, result['refresh_token'])

        else:
            # Good! We can simply return the already generated token
            return result['access_token']


    except mysql.connector.Error as err:
        print("2: Something went wrong (get code): {}".format(err))
        return -1

def refresh_access_token(token_id, refresh_token):
    print("Generating a new access token from the given token id")

    authorization = gen_base64_auth()
    authorization = authorization.decode('ascii')
    authorization = 'Basic ' + authorization

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'login.eveonline.com',
        'Authorization': authorization
    }

    url = "https://login.eveonline.com/oauth/token"
    payload = {'grant_type': 'refresh_token', 'refresh_token': str(refresh_token)}

    r = requests.post(url, headers=headers, data=payload)
    if (r.status_code != 200):
        # Oh no an error
        return -1
    else:
        content = json.loads(r.content.decode('utf-8'))
        access_token = content['access_token']

        # Updating in the database...
        my_db = mysql.connector.connect(
            host="localhost",
            user=os.environ['MYSQL_SERVER_USERNAME'],
            passwd=os.environ['MYSQL_SERVER_PASSWORD'],
            database="db_auth"
        )

        cursor = my_db.cursor()

        update_statement = "UPDATE tb_token SET access_token = %s, init_date = NOW() WHERE token_id = %s"
        cursor.execute(update_statement, (access_token, token_id))
        my_db.commit()

        return access_token



# Function for getting a state ID from the state
def get_state_id(state):

    my_db = mysql.connector.connect(
        host="localhost",
        user=os.environ['MYSQL_SERVER_USERNAME'],
        passwd=os.environ['MYSQL_SERVER_PASSWORD'],
        database="db_auth"
    )

    try:
        my_cursor = my_db.cursor(buffered=True)

        # Making the insert
        sql_statement = "SELECT state_id FROM tb_state WHERE state_value = %s"
        sql_values = (state,)
        my_cursor.execute(sql_statement, sql_values)
        my_db.commit()

        result = my_cursor.fetchall()

        if (len(result) <= 0):
            return -1

        return result[0][0]

    except mysql.connector.Error as err:
        print("Something went wrong (get code): {}".format(err))
        return -1


# Function for updating a state
# Assuming that we want to now set the state to activated for getting our access / refresh token
def set_state_activated(state):
    print("Set activation status for " + state + " to true")

    my_db = mysql.connector.connect(
        host="localhost",
        user=os.environ['MYSQL_SERVER_USERNAME'],
        passwd=os.environ['MYSQL_SERVER_PASSWORD'],
        database="db_auth"
    )

    try:
        my_cursor = my_db.cursor()

        # Making the insert
        sql_statement = "UPDATE db_auth.tb_state SET state_used = 1, date_used = NOW() WHERE state_value = %s"
        sql_values = (state,)
        my_cursor.execute(sql_statement, sql_values)
        my_db.commit()

        if my_cursor.rowcount > 0:
            return True

        else:
            return False

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        return False


# Function for verifying that a state exists within our database
def check_state(state):

    my_db = mysql.connector.connect(
        host="localhost",
        user=os.environ['MYSQL_SERVER_USERNAME'],
        passwd=os.environ['MYSQL_SERVER_PASSWORD'],
        database="db_auth"
    )

    try:
        my_cursor = my_db.cursor()

        # Making the insert
        sql_statement = "SELECT * FROM db_auth.tb_state WHERE state_value = %s"
        sql_values = (state, )
        my_cursor.execute(sql_statement, sql_values)

        # Converting into JSON to help with analysis
        row_headers = [x[0] for x in my_cursor.description]  # this will extract row headers
        rv = my_cursor.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))

        if len(json_data) <= 0:
            return False

        json_data = json_data[0]
        # Checking if this state has NOT been used yet
        # If it has, that is a problem...

        if json_data['state_used'] == 0:
            return True

        return False

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        return 0


# Function for generating a new state
def generate_state_id():

    state = ""
    for i in range(0,5):
        state += "" + str(random.randint(1,100))

    state = "naphestate" + str(state)

    # Inserting this new state into our database for logging purposes...
    my_db = mysql.connector.connect(
        host="localhost",
        user=os.environ['MYSQL_SERVER_USERNAME'],
        passwd=os.environ['MYSQL_SERVER_PASSWORD'],
        database="db_auth"
    )

    try:
        my_cursor = my_db.cursor()

        # Making the insert
        sql_statement = "INSERT INTO db_auth.tb_state (state_value) VALUES (%s)"
        sql_values = (state, )
        my_cursor.execute(sql_statement, sql_values)

        my_db.commit()
        return state

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        return 0


# Function for generating a new request URL
def generate_request_url():
    url = "https://login.eveonline.com/oauth/authorize?"

    # Adding the scope variable (this is hard coded)
    url = url + "scope="+scope+"&"

    # Adding the state
    state_id = generate_state_id()

    if state_id == 0:
        print("Failure to generate state id, returning")
        return throw_json_error(500, "Failure to generate state id")

    url = url + "state="+state_id+"&"

    # Adding response code
    url = url + "response_type=code&"

    # Adding redirect
    url = url + "redirect_uri=" + redirect + "&"

    # Finally, adding client ID
    url = url + "client_id=" + client_id

    output = {
        "code": 200,
        "url": url
    }

    return output


# Function for saving a code into our system
# We will also update the state, indicating that it was used
def save_code():

    # Grabbing the code, etc
    # Saving the code
    json_input = request.data
    json_data = json.loads(json_input.decode('utf-8'))

    code = json_data['code']
    state = json_data['state']

    print("Saving into our system code: " + str(code) + ", state: " + str(state))

    # Checking that this state exists in our system
    # If it doesn't, someone is fucking with our shit
    response = check_state(state)

    if not response:
        return throw_json_error(500, "Invalid State")

    update_state = set_state_activated(state)
    if not update_state:
        return throw_json_error(500, "Failure to update state usage")

    # Obtaining the actual state ID now for use as a foreign key
    state_id = get_state_id(state)

    # Using this ID to now insert a new code

    if state_id == -1:
        return throw_json_error(500, "Invalid state, failure to find within database")

    # Actually saving the code now
    # Inserting this new state into our database for logging purposes...
    my_db = mysql.connector.connect(
        host="localhost",
        user=os.environ['MYSQL_SERVER_USERNAME'],
        passwd=os.environ['MYSQL_SERVER_PASSWORD'],
        database="db_auth"
    )

    code_id = 0

    try:
        my_cursor = my_db.cursor()

        # Making the insert
        sql_statement = "INSERT INTO db_auth.tb_code (code, state) VALUES (%s,%s)"
        sql_values = (code, state_id)
        my_cursor.execute(sql_statement, sql_values)

        my_db.commit()
        code_id = my_cursor.lastrowid

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        return 0

    # Finally! We are going to actually generate an access token and a refresh token
    response = get_auth(code, state, code_id, state_id)

    refresh_token = response['refresh_token']
    token_id = response['token_id']

    # Loading the response into our database...
    # First checking to see if this is a character ALREADY in our system!!!
    character_data = get_character_id_from_token(response['access_token'])

    # Check if character already exists in our system
    # If it DOES, we are going to update this characters refresh token so that way it cant be used again...
    character_id = character_data['CharacterID']

    try:
        my_cursor = my_db.cursor(buffered=True)
        mysql_statement = "SELECT character_id FROM db_auth.tb_character_sso WHERE character_id = %s"
        sql_values = (character_id,)
        my_cursor.execute(mysql_statement, sql_values)

        if my_cursor.rowcount > 0:
            # We already have a character...
            # Updating that characters entry

            # New authentication
            update_statement = "UPDATE db_auth.tb_character_sso SET character_id = %s, refresh_token = %s, token_id = %s WHERE character_id = %s"
            update_values = (character_id, refresh_token, token_id, character_id)

            my_cursor.execute(update_statement, update_values)

            # New authentication
            random_string = gen_random_string(128)
            new_auth = hashlib.sha512(random_string.encode()).hexdigest()

            insert_new_character = "UPDATE db_character.tb_character SET character_auth_code = %s WHERE character_id = %s"
            insert_values = (new_auth, character_id)

            my_cursor.execute(insert_new_character, insert_values)

            my_db.commit()

        else:
            # We need to insert this character!
            insert_statement = "INSERT INTO db_auth.tb_character_sso (character_id, token_id, refresh_token) VALUES (%s, %s, %s)"
            insert_values = (character_id, token_id, refresh_token)

            my_cursor.execute(insert_statement, insert_values)

            # New authentication
            random_string = gen_random_string(128)
            new_auth = hashlib.sha512(random_string.encode()).hexdigest()

            insert_new_character = "INSERT INTO db_character.tb_character (character_id, character_sso_id, character_name, character_auth_code) VALUES (%s, %s, %s, %s)"
            insert_values = (character_id, my_cursor.lastrowid, character_data['CharacterName'], new_auth)

            my_cursor.execute(insert_new_character, insert_values)

            my_db.commit()
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))

        return {"code": 500, "reason": str(err)}

    output = {
        "code": 200,
        "auth_code": new_auth,
        "character_name": character_data['CharacterName'],
        "character_id": character_id
    }

    # Either way, we now re import skills
    import_skills(character_id, new_auth)

    return output


# Function for getting an access / refresh token from an authentication code
def get_auth(code, state, code_id, state_id):


    authorization = gen_base64_auth()
    authorization = authorization.decode('ascii')
    authorization = 'Basic ' + authorization
    print(authorization)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'login.eveonline.com',
        'Authorization': authorization
    }

    url = "https://login.eveonline.com/oauth/token"
    payload = {'grant_type': 'authorization_code', 'code': str(code)}

    print(payload)
    print(url)
    print(headers)

    r = requests.post(url, headers=headers, data=payload)
    print(r.content,r.status_code,r.reason)

    ### Inserting into our database...

    # Actually saving the code now
    # Inserting this new state into our database for logging purposes...
    my_db = mysql.connector.connect(
        host="localhost",
        user=os.environ['MYSQL_SERVER_USERNAME'],
        passwd=os.environ['MYSQL_SERVER_PASSWORD'],
        database="db_auth"
    )

    try:
        my_cursor = my_db.cursor()

        # Making the insert
        sql_statement = "INSERT INTO db_auth.tb_token (access_token, refresh_token, state_used, code_id, state_id) VALUES (%s,%s,%s,%s,%s)"
        content = json.loads(r.content.decode('utf-8'))
        sql_values = (content['access_token'], content['refresh_token'], state, code_id, state_id)
        my_cursor.execute(sql_statement, sql_values)

        my_db.commit()
        content['token_id'] = my_cursor.lastrowid

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        return 0

    return content


# Function for generating base 64 auth
def gen_base64_auth():
    prebase = str.encode(client_id+":"+client_secret)
    base64auth = base64.b64encode(prebase)
    return base64auth

# Function for getting the character ID from the characters code
def get_character_id_from_token(code):
    print("Getting character code...")
    print("Using access code " + code)


    authorization = "Bearer " + str(code)

    headers = {
        'Host': 'login.eveonline.com',
        'Authorization': authorization
    }

    url = "https://login.eveonline.com/oauth/verify"
    r = requests.get(url, headers=headers)

    print(r.content, r.status_code, r.reason)
    return json.loads(r.content.decode('utf-8'))

def import_skills(character_id, character_auth_code):
    # This should be ran as part of the auth process but it can also be triggered normally
    # Given the character ID and character auth code, lets get (or generate) and access token
    sso_id = auth_character(character_id, character_auth_code)

    # Checking for error
    if sso_id == -1:
        return throw_json_error(500, "Invalid character authentication code")

    # Otherwise, lets get that token
    access_token = get_access_token(character_id, sso_id)

    my_db = mysql.connector.connect(
        host="localhost",
        user=os.environ['MYSQL_SERVER_USERNAME'],
        passwd=os.environ['MYSQL_SERVER_PASSWORD'],
        database="db_character"
    )

    # Next, we will get the players ship
    result_skill = api_call_get("characters/" + str(character_id) + "/skills/", {"character_id": character_id, "token": access_token})
    result_character = api_call_get("characters/" + str(character_id), {"character_id": character_id, "token": access_token})
    result_skill_content = json.loads(result_skill.content.decode('utf-8'))
    result_character_content = json.loads(result_character.content.decode('utf-8'))
    corporation_id = result_character_content['corporation_id']

    skills = list()
    for skill in result_skill_content['skills']:
        # Converting the typeID to the typeName
        skill_name = convert_invtype_to_name(skill['skill_id'], my_db)
        skill_level = skill['active_skill_level']
        data = {'skill_id': skill['skill_id'], 'skill_name': skill_name, 'skill_level': skill_level}
        skills.append(data)

    # Inserting the data
    update_character_skills = "UPDATE db_character.tb_character SET character_skill_json = %s, corporation_id = %s WHERE character_id = %s"
    cursor = my_db.cursor()
    cursor.execute(update_character_skills, (json.dumps(skills), corporation_id, character_id))
    my_db.commit()

# Function for authenticating the character ID against character auth code
def auth_character_corporation(character_id):
    my_db = mysql.connector.connect(
        host="localhost",
        user=os.environ['MYSQL_SERVER_USERNAME'],
        passwd=os.environ['MYSQL_SERVER_PASSWORD'],
        database="db_auth"
    )

    try:
        my_cursor = my_db.cursor(buffered=True)
        my_cursor.execute('SELECT character_id, corporation_id FROM db_character.tb_character WHERE character_id = %s', (int(character_id),))

        result = my_cursor.fetchall()
        
        if int(result[0][1]) != 98323701:
            print("Error, unable to validate corporation")
            return False
        
        else:
            return True
        
    except mysql.connector.Error as err:
        print("Mysql exeception: {}".format(err))
        return False
    
    except Exception as err:
        print("Something went wrong: {}".format(err))
        return False