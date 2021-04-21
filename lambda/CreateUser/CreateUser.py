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
    first_name = event['firstName']
    last_name = event['lastName']
    email = event['email']
    address = event['address']
    phone_number = event['phone']
    user_password = event['password']

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.Users WHERE email = '{}'".format(email))
        group = cur.fetchone()
        if group:
            return {
                'errorMessage': json.dumps('User with email already exists.')
            }

        cur.execute("INSERT INTO GROCERY_PROJECT_DB.Users (fname, lname, email, address, phone, creation_date, hash_pass) VALUES ('{}', '{}', '{}', '{}', '{}', CURDATE(), '{}');".format(first_name, last_name, email, address, phone_number, user_password))
        conn.commit()

        cur.execute("SELECT LAST_INSERT_ID() as userId;")
        user_dict = cur.fetchone()
        logger.info("UserUrl: {}".format(user_dict['userId']))

    cur.close()
    del cur
    conn.close()

    body = {
        'userUrl': 'user?userId={}'.format(user_dict['userId'])
    }

    response = {
    'statusCode': 201,
    'body': body
    }
    logger.info(response)

    return response
