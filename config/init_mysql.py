mporting the mysql connector
import mysql.connector

def init_mysql(database):
    database = database.lower()

    my_db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="dermdermderm99E!",
        database=database
    )

    return mydb
