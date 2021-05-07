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
    email = event['email']
    user_password = event['password']

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        cur.execute("""SELECT U.fname, U.lname, U.user_id, IF(UIG.user_id = U.user_id, UIG.order_group_id, NULL) as order_group_id
                       FROM GROCERY_PROJECT_DB.Users U, GROCERY_PROJECT_DB.UserInGroup UIG
                       WHERE U.email = '{}' AND U.hash_pass = '{}'
                       LIMIT 0, 1""".format(email, user_password))
        user = cur.fetchone()
        if not user:
            return {
                'errorMessage': 'No user with that email/password.'
            }

    cur.close()
    del cur
    conn.close()

    response = {
        'firstName': '{}'.format(user['fname']),
        'lastName': '{}'.format(user['lname']),
        'userUrl': 'user?userId={}'.format(user['user_id']),
        'groupUrl': 'group?groupId={}'.format(user['order_group_id'])
    }

    logger.info(response)

    return response
