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
    screen_name = event['screenName']
    platform = event['platform']
    url = event['url']

    logger.info("Screen Name: {}".format(screen))
    if (screen_name is None or not screen_name):
        return {
            'errorMessage': 'Cannot be a content creator without a screen name.'
        }

    if (platform is None or not platform):
        return {
            'errorMessage': 'Cannot be a content creator without a platform.'
        }

    if (url is None or not url):
        return {
            'errorMessage': 'Cannot be a content creator without a url.'
        }

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.ContentCreators WHERE user_id = '{}'".format(user_id))
        user = cur.fetchone()
        if user:
            return {
                'errorMessage': 'User is already a content creator.'
            }

        cur.execute("INSERT INTO GROCERY_PROJECT_DB.ContentCreators (user_id, screen_name, platform, url) VALUES ('{}', '{}', '{}', '{}');".format(user_id, screen_name, platform, url))
        conn.commit()

    cur.close()
    del cur
    conn.close()


    body = {
        'screenName': screen_name,
        'platform': platform,
        'url': url
    }

    response = {
    'statusCode': 201,
    'body': body
    }
    logger.info(response)

    return response
