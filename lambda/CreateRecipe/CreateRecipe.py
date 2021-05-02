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
    name = event['name']
    description = event['description']
    calories = event['calories']
    servings = event['servings']

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        cur.execute("INSERT INTO GROCERY_PROJECT_DB.Recipes (name, description, image_link, calories, servings) VALUES ('{}', '{}', 'none', '{}', '{}');".format(name, description, calories, servings))
        conn.commit()

        cur.execute("SELECT LAST_INSERT_ID() as recipeId;")
        user_dict = cur.fetchone()
        logger.info("recipeId: {}".format(user_dict['recipeId']))

    cur.close()
    del cur
    conn.close()

    body = {
        'recipeUrl': 'recipes/detail?recipeId={}'.format(user_dict['recipeId'])
    }

    response = {
    'statusCode': 201,
    'body': body
    }
    logger.info(response)

    return response
