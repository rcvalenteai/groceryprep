import sys
import logging
import rds_config
import pymysql
import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from datetime import datetime

#rds settings
rds_host = "meal-plan-db.cssril6qx5ub.us-east-2.rds.amazonaws.com"
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    search_string = ""
    if 'search' in event:
        search_string = event['search']
    logger.info("Search string: {}".format(search_string))

    group_list = []

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        base_query = "SELECT * FROM GROCERY_PROJECT_DB.OrderGroups O;" 
        cur.execute(base_query)
        groups = cur.fetchall()

        for group in groups:
            group_obj = Group(group)

            fuzzy_score = fuzz.partial_ratio(group_obj.name, search_string)
            if (len(search_string) == 0):
                group_list.append({'Group': group_obj, 'fuzzy_score': 100})
            elif (len(search_string) and fuzzy_score > 65):
                group_list.append({'Group': group_obj, 'fuzzy_score': fuzzy_score})

    cur.close()
    del cur
    conn.close()

    # Sort by search score if search string is present
    #logger.info(group_list)
    if (len(search_string)):
        group_list.sort(key=getFuzzyScore)
    else:
        group_list.sort(key=getName)

    group_json_list = []
    response = {'item_count': len(group_list)}
    for group in group_list:
        gdict = group['Group'].__dict__
        logger.info(gdict)
        gdict['location'] = 'group?groupId={}'.format(gdict['group_id'])
        gdict.pop('group_id')
        group_json_list.append(gdict)

    response['items'] = group_json_list
    logger.info(response)

    return response

def getFuzzyScore(e):
    return e['fuzzy_score']

def getName(e):
    return e['Group'].name

class Group:
    def __init__(self, conn_dict):
        self.group_id = conn_dict['order_group_id']
        self.name = conn_dict['name']
        self.creation_date = conn_dict['creation_date'].strftime("%m-%d-%Y")
