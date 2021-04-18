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
    meal_plan_url = event['mealPlanUrl']
    user_url = event['userUrl']

    match = re.match(r".*?mealPlans/detail\?mealPlanId=(\d+)", meal_plan_url)
    if match is None:
        return {
            'errorMessage': 'Cannot extract mealPlanId from mealPlanUrl'
        }
    meal_plan_id = match.group(1)

#    match = re.match(r".*?user\?userId=(\d+)", user_url)
#    if match is None:
#        return {
#            'errorMessage': json.dumps('Cannot extract userId from userUrl')
#        }
#    user_id = match.group(1)
    user_id = user_url

    logger.info("MealPlan Id: {}".format(meal_plan_id))
    logger.info("User Id: {}".format(user_id))

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        # Check the MealPlan Exists
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.MealPlans WHERE meal_plan_id = '{}'".format(meal_plan_id))
        meal_plan = cur.fetchone()
        if not meal_plan:
            return {
                'errorMessage': 'MealPlan doesn\'t exist.'
            }
        logger.info("meal_plan Id: {}".format(meal_plan['meal_plan_id']))

        # Check the User Exists
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.Users WHERE user_id = '{}'".format(user_id))
        user = cur.fetchone()
        if not user:
            return {
                'errorMessage': 'User doesn\'t exist.'
            }
        logger.info("User Id: {}".format(user['user_id']))

        # Check if entry already exists
        cur.execute("SELECT * from GROCERY_PROJECT_DB.Subscribe S where S.user_id = '{}' and S.meal_plan_id = '{}'".format(user_id, meal_plan_id))
        subscribe = cur.fetchone()
        if subscribe:
            return {
                    'errorMessage': 'UserId {} is already subscribed to MealPlanId {}'.format(user_id, meal_plan_id)
            }

        cur.execute("INSERT INTO GROCERY_PROJECT_DB.Subscribe (user_id, meal_plan_id) VALUES ('{}', '{}')".format(user_id, meal_plan_id))
        conn.commit()

    cur.close()
    del cur
    conn.close()

    body = {
        'mealPlanLocation': 'mealPlans/detail?mealPlanId={}'.format(meal_plan_id),
    }

    response = {
    'statusCode': 200,
    'body': body
    }
    logger.info(response)

    return response
