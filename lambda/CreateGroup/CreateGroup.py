import sys
import logging
import rds_config
import pymysql
import json
import time
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
    group_name = event['groupName']
    logger.info("Group Name: {}".format(group_name))
    if (group_name is None or not group_name):
        return {
            'errorMessage': 'Cannot create a group without a group name.'
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
                'errorMessage': 'User doesn\'t exist.'
            }
        logger.info("User Id: {}".format(user['user_id']))

        today = date.today().strftime("%Y-%m-%d")
        logger.info(today)
        cur.execute("INSERT INTO GROCERY_PROJECT_DB.OrderGroups (name, creation_date) VALUES ('{}', '{}');".format(group_name, today))
        conn.commit()

        cur.execute("SELECT LAST_INSERT_ID() AS groupId;")
        order_group = cur.fetchone()
        logger.info("Created groupId: {}".format(order_group))

        cur.execute("INSERT INTO GROCERY_PROJECT_DB.UserInGroup (user_id, order_group_id) VALUES ('{}', '{}')".format(user_id, order_group['groupId']))
        conn.commit()

    cur.close()
    del cur
    conn.close()


    body = {
        'groupName': group_name,
        'groupLocation': 'group?groupId={}'.format(order_group['groupId'])
    }

    response = {
    'statusCode': 201,
    'body': body
    }
    logger.info(response)

    return response
