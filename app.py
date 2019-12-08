##########################
### Base level imports ###
##########################

from flask import Flask
from flask_cors import CORS
import json
from auth.error import *

########################
# Setting up the flask #
########################

app = Flask("EvE ERB API")
CORS(app)

###########################
# Setting up load imports #
###########################

from auth.load_dir import auth_load
from character.load_dir import character_load
from location.load_dir import location_load
from sig.load_dir import sig_load
from static.load_dir import static_load
from stream.load_dir import stream_load
from config.load_dir import config_load

@app.route('/')
def init_route():
    response = json.dumps(throw_json_error(404, "Page not found"))
    print("Returning " + response)
    return response

### Loading routes
auth_load(app)
character_load(app)
location_load(app)
sig_load(app)
static_load(app)
stream_load(app)
config_load(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
