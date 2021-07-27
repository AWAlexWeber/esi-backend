# Used to load our db_static.skills database that contains all required skills for an item
#importing the mysql connector
import json
import mysql.connector
from collections import defaultdict
import os

query = "SELECT i.typeID as itemID, i.typeName as itemName, ip.typeID as prerqSkillID, ip.typeName as prereqSkillName, dtal.valueInt as prerqSkillLevelInt,	dtal.valueFloat  as prerqSkillLevelFloat FROM invGroups g LEFT JOIN invTypes i 	ON i.groupID = g.groupID LEFT JOIN dgmTypeAttributes dta	ON dta.typeID = i.typeID AND	   dta.attributeID IN (182, 183, 184, 1285, 1289, 1290) LEFT JOIN dgmTypeAttributes dtal 	ON dtal.typeID = dta.typeID AND	((dtal.attributeID = 277 AND dta.attributeID = 182) OR (dtal.attributeID = 278 AND dta.attributeID = 183) OR (dtal.attributeID = 279 AND dta.attributeID = 184) OR (dtal.attributeID = 1286 AND dta.attributeID = 1285) OR (dtal.attributeID = 1287 AND dta.attributeID = 1289) OR	(dtal.attributeID = 1288 AND dta.attributeID = 1290)) JOIN invTypes ip ON ip.typeID = dta.valueInt OR ip.typeID = dta.valueFloat WHERE i.typeID NOT IN (19430, 9955) AND i.published = 1 AND g.categoryID NOT IN (0,1,2,3,25) ORDER BY g.groupName DESC" 

def init_mysql(database):
    database = database.lower()

    my_db = mysql.connector.connect(
        host="localhost",
        user=os.environ['MYSQL_SERVER_USERNAME'],
        passwd=os.environ['MYSQL_SERVER_PASSWORD'],
        database=database
    )

    return my_db

db = init_mysql("db_static")
cursor = db.cursor()
cursor.execute(query)
results = cursor.fetchall()

# Creating our tree
class TreeNode:
    def __init__(self, typeID, typeName):
        self.typeID, self.typeName = typeID, typeName
        self.prereqs = []

# Dictionary of all tree nodes; key = typeID, value = TreeNode
treeNodeDict = {}
for line in results:
    typeID, typeName, prereqID, prereqName, n, prereqLevel = (line)
    prereqLevel = int(prereqLevel)
    treeNode = None

    if typeID not in treeNodeDict:
        treeNode = TreeNode(typeID, typeName)
        treeNodeDict[typeID] = treeNode

    treeNode = treeNodeDict[typeID]

    treeNode.prereqs.append((prereqID, prereqName, prereqLevel))

# Traversal
allReqs = defaultdict(lambda: list())
for typeID in treeNodeDict.keys():
    # Performing tree calculation for each typeID
    
    exploredSet = set()
    frontierList = list()
    prereqData = list()
    
    frontierList.append(treeNodeDict[typeID])

    while len(frontierList) > 0:
        currentNode = frontierList.pop()
        exploredSet.add(currentNode.typeID)

        for prereqValue in currentNode.prereqs:
            prereqID = prereqValue[0]

            if prereqID in exploredSet:
                continue

            prereqData.append({
                "typeID": prereqValue[0],
                "typeName": prereqValue[1],
                "prereqSkillLevel": prereqValue[2] 
            })

            if prereqID in treeNodeDict:
                prereq = treeNodeDict[prereqID]
                frontierList.append(prereq)

    reqDict = {}
    reqIdDict = {}
    for req in prereqData:
        reqDict[req['typeName']] = max(req['prereqSkillLevel'], ( 0 if req['typeName'] not in reqDict else reqDict[req['typeName']]))
        reqIdDict[req['typeID']] = max(req['prereqSkillLevel'], ( 0 if req['typeID'] not in reqDict else reqDict[req['typeID']]))
        #insert_req = "INSERT INTO skillReqs (typeID, typeName, prereqSkillTypeID, prereqSkillTypeName, prereqSkillLevel) VALUES (%s, %s, %s, %s, %s)"
        #cursor.execute(insert_req, (typeID, treeNodeDict[typeID].typeName, req['typeID'], req['typeName'], req['prereqSkillLevel']))
    
    insert_req = "INSERT INTO skillReqsData (typeID, typeName, skillReqsTypeID, skillReqsTypeName) VALUES (%s, %s, %s, %s)"
    cursor.execute(insert_req, (typeID, treeNodeDict[typeID].typeName, json.dumps(reqDict), json.dumps(reqIdDict)))
    
db.commit()