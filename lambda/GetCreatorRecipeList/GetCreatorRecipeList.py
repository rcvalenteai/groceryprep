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

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        base_query = "SELECT R.recipe_id, R.name FROM GROCERY_PROJECT_DB.RecipesByContentCreators RBCC, GROCERY_PROJECT_DB.Recipes R WHERE RBCC.user_id = '{}' AND RBCC.recipe_id = R.recipe_id".format(user_id) 
        cur.execute(base_query)
        recipes = cur.fetchall()

    cur.close()
    del cur
    conn.close()

    response = {'item_count': len(recipes)}

    for recipe in recipes:
        recipe['location'] = 'recipes/detail?recipeId={}'.format(recipe['recipe_id'])
        recipe.pop('recipe_id')

    response['items'] = recipes
    logger.info(response)

    return response
