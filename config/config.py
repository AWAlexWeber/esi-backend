import random
import string
import requests
import datetime
import base64
import json

### Global variables
base_api = "https://esi.evetech.net/dev/"

seat_client_id = "95ec26f88cf14508962c862b80e86dcc"
seat_client_secret = "Qk2XLAmb603CKFktZyw1Rqae4oVMP7UK8RUTE7OQ"

client_id = "5181baa1c09140708770534822b7e9cc"
client_secret = "0qrAXVeAwe1CZUFH0PMpEdCfuWN0bRp1uR6dEaqw"

def gen_random_string(length):

    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

#######################
## Private Functions ##
#######################

def get_format_from_raw(raw, cursor):
   result = [dict(line) for line in [zip([column[0] for column in cursor.description], row) for row in raw]][0]
   return result

def get_format_from_raw_full(raw, cursor):
   result = [dict(line) for line in [zip([column[0] for column in cursor.description], row) for row in raw]]
   return result

def date_to_string(datetime):
    output = datetime.strftime("%Y-%m-%d %H:%M:%S")
    return output


### Function for making a call to an API ###
def api_call_get(endpoint, data):
    path = base_api + endpoint


    # Converting the data set into GET url
    data_string = "?"
    for entry in data:
        data_string = data_string + str(entry) + "=" + str(data[entry]) + '&'

    # Appending to path
    path = path + data_string
    path = path[0:len(path) - 1]
    bearer = {'Authorization': 'Bearer ' + data['token']}

    print("Sending request to " + str(path) + " with data of " + str(data) + " and header of " + str(bearer))

    response = requests.get(path, data="", headers=bearer)

    return response

### Converting all instances of datetime into a string for output purposes
### Requires an array as input
def encode_datetime(result):

    # Performing format fix
    new_result_output = []
    for value in result:

        ### Building the new output value
        new_value = value

        for element in value:
            data = value[element]
            if isinstance(data, datetime.datetime):

                new_value[element] = date_to_string(value[element])

        new_result_output.append(new_value)

    return new_result_output

def manual_request():

    print("Performing manual api request")
    return str(manual_request_location())

def manual_request_access_token():

    ### Attempting to perform a manual access token call from a refresh token...
    refresh_token = "7e1Oqv_aG8zaUrhmAEslqWeZ0WNozVh2UGt3_c7CV3uIxPkCVmMgTIC4DaFYZdkrfsAxcPQyAqcFNwTIWJXF2a_NcXSoUVgWkZCxex-XvFhPxML8gvRO-NK4an3_S3BQf4A8YOpoVnpmWY2IMKyf3d5h14XSPj_G2q5_Wd0k1ThQmmopu6_lD6sezT_eAZ6dVi5sNndeRNiGhi386__sIJ6ZWD23Hw5t_QJVudC8FAdtQ--xeuPhkAMcZgnGKU5LdUPWNW_P8XyExdLHCr6jK2EcJc_GlRGvfo8r_cCWsjnWoxt3c-L-1-uW3lfrtynjz3BcFs0RI9tepTUrODfjRkvCYM4pnYVNJ50MaBzuXvY"
    authorization = gen_base64_seat_auth()
    authorization = authorization.decode('ascii')
    authorization = 'Basic ' + authorization

    # 2115529576

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'login.eveonline.com',
        'Authorization': authorization
    }

    url = "https://login.eveonline.com/oauth/token"
    payload = {'grant_type': 'refresh_token', 'refresh_token': str(refresh_token)}

    r = requests.post(url, headers=headers, data=payload)
    output = json.loads(r.content.decode('utf-8'))
    print(output)

def manual_request_location():

    access_token = "1|CfDJ8HHFK/DOe6xKoNPHamc0mCVVB9iCNcpOblsQEtOeQ5Fvhr+5kvx5VUedZp+3y1XDCnMWupl4aVZPtQ6nTp0TTYFO1crgSDDv1qye1LdIGUmH+ovhJgEwnMS1LkA6zLtAnnVwdAfxyNDcFXubmls9NcEWv8F///+RoRkCXS5adYYS"
    character_id = "2115529576"

    result_location = api_call_get("characters/" + str(character_id) + "/wallet/journal/",
                                   {"character_id": character_id, "token": access_token, "page": 1})

    print(result_location)
    print(result_location.reason)
    print(result_location.content)

    return result_location.content

# Function for generating base 64 auth
def gen_base64_auth():
    prebase = str.encode(client_id+":"+client_secret)
    base64auth = base64.b64encode(prebase)
    return base64auth

# Function for generating base 64 auth
def gen_base64_seat_auth():
    prebase = str.encode(seat_client_id+":"+seat_client_secret)
    base64auth = base64.b64encode(prebase)
    return base64auth