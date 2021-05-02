import sys
import logging
import rds_config
import pymysql
import json
import re

#rds settings
rds_host = "meal-plan-db.cssril6qx5ub.us-east-2.rds.amazonaws.com"
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    group_url = event['groupUrl']

    match = re.match(r".*?group\?groupId=(\d+)", group_url)
    if match is None:
        return {
            'errorMessage': 'Cannot extract groupId from groupUrl'
        }
    group_id = match.group(1)

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.OrderGroups WHERE order_group_id = '{}'".format(group_id))
        group = cur.fetchone()
        if not group:
            return {
                'errorMessage': 'Group doesn\'t exist.'
            }
        logger.info("Group Id: {}".format(group['order_group_id']))

        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.Order WHERE order_group_id = '{}' and is_open = 1".format(group_id))
        order = cur.fetchone()
        if order:
            return {
                'errorMessage': 'There is already an open order for this group.'
            }

        cur.execute("INSERT INTO GROCERY_PROJECT_DB.Order (order_group_id, is_open) VALUES ('{}', 1);".format(group_id))
        conn.commit()

    cur.close()
    del cur
    conn.close()

    body = {
        'groupLocation': 'group?groupId={}'.format(group_id)
    }

    response = {
    'statusCode': 201,
    'body': body 
    }
    logger.info(response)

    return response
