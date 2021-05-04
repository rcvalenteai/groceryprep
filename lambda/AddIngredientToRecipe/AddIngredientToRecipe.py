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
    ingredient_url = event['ingredientUrl']
    recipe_url = event['recipeUrl']
    quantity = event['quantity']

    match = re.match(r".*?ingredients\?ingredientId=(\d+)", ingredient_url)
    if match is None:
        return {
            'errorMessage': 'Cannot extract ingredientId from ingredientUrl'
        }
    ingredient_id = match.group(1)

    match = re.match(r".*?recipes/detail\?recipeId=(\d+)", recipe_url)
    if match is None:
        return {
            'errorMessage': 'Cannot extract recipeId from recipeUrl'
        }
    recipe_id = match.group(1)

    logger.info("ingredient Id: {}".format(ingredient_id))
    logger.info("recipe Id: {}".format(recipe_id))

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        # Check the ingredient Exists
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.Ingredients WHERE ingredient_id = '{}'".format(ingredient_id))
        ingredient = cur.fetchone()
        if not ingredient:
            return {
                'errorMessage': 'ingredient doesn\'t exist.'
            }
        logger.info("ingredient Id: {}".format(ingredient['ingredient_id']))

        # Check the Recipe Exists
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.Recipes WHERE recipe_id = '{}'".format(recipe_id))
        recipe = cur.fetchone()
        if not recipe:
            return {
                'errorMessage': 'Recipe doesn\'t exist.'
            }
        logger.info("Recipe Id: {}".format(recipe['recipe_id']))

        # Check ingredient is not already part of recipe
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.IngredientsInRecipe R where R.recipe_id = '{}' and R.ingredient_id = '{}'".format(recipe_id, ingredient_id))
        result = cur.fetchone()
        if result:
            return {
                    'errorMessage': 'This recipe already contains ingredient with id: {}'.format(ingredient_id)
            }

        cur.execute("INSERT INTO GROCERY_PROJECT_DB.IngredientsInRecipe (ingredient_id, recipe_id, quantity) VALUES ('{}', '{}', {})".format(ingredient_id, recipe_id, quantity))
        conn.commit()

    cur.close()
    del cur
    conn.close()

    body = {
        'ingredientLocation': 'ingredients?ingredientId={}'.format(ingredient_id),
        'recipeLocation': 'recipes/detail?recipeId={}'.format(recipe_id),
        'quantity': quantity
    }

    response = {
    'statusCode': 200,
    'body': body
    }
    logger.info(response)

    return response
