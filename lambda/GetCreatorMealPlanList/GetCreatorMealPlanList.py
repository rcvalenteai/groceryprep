import sys
import logging
import rds_config
import pymysql
import json
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
    user_id = event['userId']

    meal_plan_list = []

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        base_query = "SELECT MP.meal_plan_id, MP.name FROM GROCERY_PROJECT_DB.MealPlansByContentCreators MPBCC, GROCERY_PROJECT_DB.MealPlans MP WHERE MPBCC.user_id = '{}' AND MPBCC.meal_plan_id = MP.meal_plan_id".format(user_id) 
        cur.execute(base_query)
        meal_plans = cur.fetchall()

    cur.close()
    del cur
    conn.close()

    response = {'item_count': len(meal_plans)}

    for meal_plan in meal_plans:
        meal_plan['location'] = 'mealplan/detail?mealPlanId={}'.format(meal_plan['meal_plan_id'])
        meal_plan.pop('meal_plan_id')

    response['items'] = meal_plans
    logger.info(response)

    return response
