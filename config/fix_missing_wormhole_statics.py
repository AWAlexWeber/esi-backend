# Importing the mysql connector
import mysql.connector
import random
import string
import requests
import datetime


def get_format_from_raw(raw, cursor):
   result = [dict(line) for line in [zip([column[0] for column in cursor.description], row) for row in raw]][0]
   return result

def get_format_from_raw_full(raw, cursor):
   result = [dict(line) for line in [zip([column[0] for column in cursor.description], row) for row in raw]]
   return result

def date_to_string(datetime):
    output = datetime.strftime("%Y-%m-%d %H:%M:%S")
    return output

def init_mysql(database):
    database = database.lower()

    my_db = mysql.connector.connect(
        host="localhost",
        user="vsadmin",
        passwd="dermdermderm99E!",
        database=database
    )

    return my_db

print("Fixing the missing wormhole statics...")

### We will iterate on all wormholes from the static map
connector = init_mysql("db_static")
cursor = connector.cursor()

GET_ALL_SHATTERED = "SELECT * FROM db_static.mapSolarSystems WHERE solarSystemName LIKE 'J0%'"
cursor.execute(GET_ALL_SHATTERED, ())
result_raw = cursor.fetchall()
result = get_format_from_raw_full(result_raw, cursor)
count = 0
for result_entry in result:
    count+=1
    print(result_entry)

print(count)