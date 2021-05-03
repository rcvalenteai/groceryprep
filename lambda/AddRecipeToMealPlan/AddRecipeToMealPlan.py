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
    mealplan_url = event['mealPlanUrl']
    recipe_url = event['recipeUrl']

    match = re.match(r".*?mealplan/detail\?mealPlanId=(\d+)", mealplan_url)
    if match is None:
        return {
            'errorMessage': 'Cannot extract mealplanId from mealplanUrl'
        }
    mealplan_id = match.group(1)

    match = re.match(r".*?recipes/detail\?recipeId=(\d+)", recipe_url)
    if match is None:
        return {
            'errorMessage': 'Cannot extract recipeId from recipeUrl'
        }
    recipe_id = match.group(1)

    logger.info("mealplan Id: {}".format(mealplan_id))
    logger.info("recipe Id: {}".format(recipe_id))

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        # Check the mealplan Exists
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.MealPlans WHERE meal_plan_id = '{}'".format(mealplan_id))
        mealplan = cur.fetchone()
        if not mealplan:
            return {
                'errorMessage': 'Meal Plan doesn\'t exist.'
            }
        logger.info("mealplan Id: {}".format(mealplan['meal_plan_id']))

        # Check the Recipe Exists
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.Recipes WHERE recipe_id = '{}'".format(recipe_id))
        recipe = cur.fetchone()
        if not recipe:
            return {
                'errorMessage': 'Recipe doesn\'t exist.'
            }
        logger.info("Recipe Id: {}".format(recipe['recipe_id']))

        # Check recipe is not already part of mealplan
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.MealPlanContains M where M.recipe_id = '{}' and M.meal_plan_id = '{}'".format(recipe_id, mealplan_id))
        result = cur.fetchone()
        if result:
            return {
                    'errorMessage': 'This mealplan already contains recipe with id: {}'.format(recipe_id)
            }

        cur.execute("INSERT INTO GROCERY_PROJECT_DB.MealPlanContains (meal_plan_id, recipe_id) VALUES ('{}', '{}')".format(mealplan_id, recipe_id))
        conn.commit()

    cur.close()
    del cur
    conn.close()

    body = {
        'mealplanLocation': 'mealplans/detail?mealplanId={}'.format(mealplan_id),
        'recipeLocation': 'recipes/detail?recipeId={}'.format(recipe_id),
    }

    response = {
    'statusCode': 200,
    'body': body
    }
    logger.info(response)

    return response
