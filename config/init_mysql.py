
# Importing the mysql connector
import mysql.connector

def init_mysql(database):
    my_db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="dermdermderm99",
        database=database
    )

    return my_db;