import sys
import logging
import rds_config
import pymysql
import json
import time
import re
from datetime import date

#rds settings
rds_host = "meal-plan-db.cssril6qx5ub.us-east-2.rds.amazonaws.com"
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    user_id = event['userId']
    groupUrl = event['groupUrl']

    match = re.match(r".*?group\?groupId=(\d*)", groupUrl)
    if match is None:
        return {
            'errorMessage': json.dumps('Cannot extract groupId from groupUrl')
        }

    group_id = match.group(1)
    logger.info("Group Id: {}".format(group_id))
    if (group_id is None or not group_id):
        return {
            'errorMessage': json.dumps('Cannot join a group without a groupId number.')
        }

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
                'errorMessage': json.dumps('User doesn\'t exist.')
            }
        logger.info("User Id: {}".format(user['user_id']))

        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.OrderGroups WHERE order_group_id = '{}'".format(group_id))
        group = cur.fetchone()
        if not group:
            return {
                'errorMessage': json.dumps('Group doesn\'t exist.')
            }
        logger.info("Group Id: {}".format(group['order_group_id']))

        # This trys to catch duplicate key errors. Another method which may be better is to use try catch with pymysql 'IntegrityError'
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.UserInGroup WHERE user_id = '{}' and order_group_id = '{}'".format(user_id, group_id))
        group = cur.fetchone()
        if group:
            return {
                'errorMessage': json.dumps('User is already part of order group.')
            }

        cur.execute("INSERT INTO GROCERY_PROJECT_DB.UserInGroup (user_id, order_group_id) VALUES ('{}', '{}')".format(user_id, group_id))
        conn.commit()

    cur.close()
    del cur
    conn.close()


    body = {
        'groupName': group['name'],
        'groupLocation': 'group?groupId={}'.format(group['order_group_id'])
    }

    response = {
    'statusCode': 200,
    'body': json.dumps(body, indent=4)
    }
    logger.info(response)

    return response
