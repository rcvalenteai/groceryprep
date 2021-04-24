import sys
import logging
import rds_config
import pymysql
import json
from decimal import *
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#rds settings
rds_host = "meal-plan-db.cssril6qx5ub.us-east-2.rds.amazonaws.com"
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    if 'groupId' not in event:
        return {"No Group ID specified."}
    group_id = event['groupId']

    if 'cost' not in event:
        return {"Must provide a cost to split."}

    cost = Decimal(event['cost']).quantize(Decimal('.01'))

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        # Check the Order Group Exists
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.OrderGroups WHERE order_group_id = '{}'".format(group_id))
        group = cur.fetchone()
        if not group:
            return {
                'errorMessage': 'Group doesn\'t exist.'
            }
        logger.info("Group Id: {}".format(group['order_group_id']))

        # Check there is an open order for Group
        cur.execute("SELECT * from GROCERY_PROJECT_DB.UserInGroup WHERE order_group_id = '{}'".format(group_id))
        users_in_group = len(cur.fetchall())
        logger.info("Users: {}".format(users_in_group))

    cur.close()
    del cur
    conn.close()

    cost_per = (cost / Decimal(users_in_group)).quantize(Decimal('.01'), rounding=ROUND_UP)
    response = {'totalCost': cost, 'userCount': users_in_group, 'costPer': cost_per}
    logger.info(response)

    return response
