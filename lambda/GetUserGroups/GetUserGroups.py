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
    user_id = event['userId']

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.Users WHERE user_id = '{}'".format(user_id))
        user = cur.fetchone()
        if not user:
            return {
                'errorMessage': 'User doesn\'t exist.'
            }
        logger.info("User Id: {}".format(user['user_id']))

        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.UserInGroup NATURAL JOIN GROCERY_PROJECT_DB.OrderGroups WHERE user_id = '{}'".format(user_id))
        user_groups = cur.fetchall()
        logger.info(user_groups)
        group_list = [UserGroup(group) for group in user_groups]

    cur.close()
    del cur
    conn.close()


    response = {'item_count': len(group_list)}
    group_json_list = []
    for group in group_list:
        gdict = group.__dict__;
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

class UserGroup:
    def __init__(self, conn_dict):
        self.group_id = conn_dict['order_group_id']
        self.name = conn_dict['name']
        self.creation_date = conn_dict['creation_date'].strftime("%m-%d-%Y")
