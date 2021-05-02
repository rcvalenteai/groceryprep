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
        cur.execute("SELECT fname, lname, email, address, phone, creation_date FROM GROCERY_PROJECT_DB.Users WHERE user_id = '{}'".format(user_id))
        user = cur.fetchone()
        if not user:
            return {
                'errorMessage': 'User doesn\'t exist.'
            }
        logger.info("User Email: {}".format(user['email']))

    cur.close()
    del cur
    conn.close()

    user['creation_date'] = user['creation_date'].strftime("%Y-%m-%d")

    response = user
    logger.info(response)

    return response

