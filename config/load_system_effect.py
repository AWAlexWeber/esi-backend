import csv

# Importing the mysql connector
import mysql.connector

def init_mysql(database):
    database = database.lower()

    my_db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="dermdermderm99E!",
        database=database
    )

    return my_db

with open('full_systems.txt', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    print("Running...")

    output = []
    row_count = 0

    connector = init_mysql("db_static")
    cursor = connector.cursor()

    print("More running...")



    for unmod_row in reader:

        print(unmod_row)
        row = unmod_row

        if len(row) > 4:
            effectType = row[4]

            if ',' in effectType:
                effectType = effectType[0:len(effectType) - 1]

            if effectType == "CataclysmicVariable":
                effectType = "Cataclysmic Variable"
            elif effectType == "RedGiant":
                effectType = "Red Giant"
            elif effectType == "BlackHole":
                effectType = "Black Hole"

            print(row[0]+" " +effectType)


            ### Time to insert this into the database
            if effectType == "":
                continue

            get_solar_system_id = "SELECT solarSystemID from mapsolarsystems WHERE solarSystemName = %s;"
            cursor.execute(get_solar_system_id, (row[0],))
            systemID = cursor.fetchall()[0][0]


            insert_effect = "INSERT INTO wormholeeffect (solarSystemID, wormholeEffect) VALUES (%s, %s)"
            cursor.execute(insert_effect, (systemID, effectType))

    connector.commit()