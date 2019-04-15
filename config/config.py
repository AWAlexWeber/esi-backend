import random
import string
import requests

### Global variables
base_api = "https://esi.evetech.net/dev/"

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

    print("Sending request to " + str(path) + " with data of " + str(data))
    response = requests.get(path, data="")
    return response