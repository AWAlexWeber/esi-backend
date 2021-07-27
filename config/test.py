import csv

# Importing the mysql connector
import mysql.connector
import os

def init_mysql(database):
    my_db = mysql.connector.connect(
        host="localhost",
        user=os.environ['MYSQL_SERVER_USERNAME'],
        passwd=os.environ['MYSQL_SERVER_PASSWORD'],
        database=database
    )

    return my_db
    
with open('full.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')

    output = []
    row_count = 0

    for row in reader:
        row_data = ', '.join(row)
        row_array = row_data.split(',')

        # Tracking row
        if row_count == 0:
            row_count = row_count + 1
            continue

        row_count = row_count + 1

        # Stealing the ID

        row_name = row_array[0]
        last_slash = row_name.rfind('/')
        name = row_name[last_slash + 1:len(row_name)]

        new_data = []
        new_data.append(name)

        entry_count = 0

        for entry in row_array:

            if entry_count == 0:
                entry_count = entry_count + 1
                continue

            new_data.append(entry)

        output.append(new_data)

    # Inserting
    mydb = init_mysql("db_static")
    cursor = mydb.cursor()

    for entry in output:

        insert = "INSERT INTO wormholeStaticInfo (name, destination, source, lifetime_hours, max_mass_per_jump, total_mass, respawn, mass_regen, type_id)" \
                 "VALUES" \
                 "(%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        cursor.execute(insert, entry)
        mydb.commit()