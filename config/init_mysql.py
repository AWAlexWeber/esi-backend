#importing the mysql connector
import mysql.connector
import os

def init_mysql(database):
    database = database.lower()

    mydb = mysql.connector.connect(
        host="localhost",
        user=os.environ['MYSQL_SERVER_USERNAME'],
        passwd=os.environ['MYSQL_SERVER_PASSWORD'],
        database=database
    )

    return mydb
