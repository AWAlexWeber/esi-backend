# Importing JSON
import json
import mysql.connector
import re

def init_mysql(database):
    my_db = mysql.connector.connect(
        host="localhost",
        user="vsadmin",
        passwd="dermdermderm99E!",
        database=database
    )

    return my_db

def convert_invtype_to_name(invtype, mydb):
    cursor = mydb.cursor()

    location_get = "SELECT typeName FROM db_static.invTypes WHERE typeID = %s"
    cursor.execute(location_get, (invtype,))
    result_raw = cursor.fetchall()
    return result_raw[0][0]

def missing_skills(fitting_id, character_id):
    # Gets the total missing skills for a fit given its id for a character given their ID
    # If they can fly it, returns a success
    return

def get_all_missing_skills(fitting_id):
    # Gets all missing skills for each character for a given fit
    # Getting all of the characters first
    
    mydb = init_mysql("db_character")
    cursor = mydb.cursor()

    get_all_characters = "SELECT * FROM tb_character WHERE character_role = 'primary'"
    cursor.execute(get_all_characters)
    results = cursor.fetchall()

    get_fit_skills = "SELECT * FROM db_fitting.tb_fitting WHERE fit_id = %s"
    cursor.execute(get_fit_skills, (fitting_id,))
    results_fit = cursor.fetchall()
    fit_skills_id = json.loads(results_fit[0][-2])

    success_list = list()
    fail_list = list()

    skill_id_to_name = {}

    for character_data in results:
        character_name = character_data[2]
        character_skills = json.loads(character_data[5])
        
        character_skill_id = {}
        character_skill_name = {}
        for skill in character_skills:
            character_skill_id[skill['skill_id']] = skill['skill_level']
            character_skill_name[skill['skill_name']] = skill['skill_level']

        skip_flag = False
        missing_skill_list = list()
        for prereq in fit_skills_id:
            skill_id = prereq
            if int(skill_id) not in character_skill_id or character_skill_id[int(skill_id)] < fit_skills_id[skill_id]:
                skip_flag = True
                missing_skill_list.append(convert_invtype_to_name(skill_id, mydb) + " " + str(fit_skills_id[skill_id]))

        if skip_flag:
            fail_list.append("-- " + character_name + " ( " + character_data[-2] + ") -- \n")

            for missing_skill in missing_skill_list:
                fail_list.append(missing_skill)
            fail_list.append("")

            continue

        success_list.append(character_name)

    print("===============================")
    for s in success_list:
        print(s)
    print("===============================")    
    for f in fail_list:
        print(f)



get_all_missing_skills(9)