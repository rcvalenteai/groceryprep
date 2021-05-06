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
    user_url = event['userUrl']
    match = re.match(r".*?user\?userId=(\d+)", user_url)
    if match is None:
        return {
            'errorMessage': 'Cannot extract userId from userUrl'
        }
    user_id = match.group(1)

    description = event['description']
    meal_plan_name = event['name']

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        cur.execute("INSERT INTO GROCERY_PROJECT_DB.MealPlans (description, name, image_link) VALUES ('{}', '{}', 'none');".format(description, meal_plan_name))
        conn.commit()

        cur.execute("SELECT LAST_INSERT_ID() as mealPlanId;")
        mealplan_dict = cur.fetchone()
        logger.info("recipeId: {}".format(mealplan_dict['mealPlanId']))

        cur.execute("INSERT INTO GROCERY_PROJECT_DB.MealPlansByContentCreators (meal_plan_id, user_id) VALUES ('{}', '{}')".format(mealplan_dict['mealPlanId'], user_id))
        conn.commit()

    cur.close()
    del cur
    conn.close()

    body = {
        'mealPlanUrl': 'mealplan/detail?mealPlanId={}'.format(mealplan_dict['mealPlanId'])
    }

    response = {
    'statusCode': 201,
    'body': body
    }
    logger.info(response)

    return response
