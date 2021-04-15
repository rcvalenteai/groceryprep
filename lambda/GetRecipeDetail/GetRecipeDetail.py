import sys
import logging
import rds_config
import pymysql
import json

#rds settings
rds_host = "meal-plan-db.cssril6qx5ub.us-east-2.rds.amazonaws.com"
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    recipe_id = event['recipeId']
    logger.info("Recipe Id: {}".format(recipe_id))
    if (recipe_id is None or len(recipe_id) == 0):
        logger.error("No recipe id specified for this endpoint")
        sys.exit()

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        cur.execute("select * from GROCERY_PROJECT_DB.Recipes R where R.recipe_id = '{}'".format(recipe_id))
        recipe_dict = cur.fetchone()

        cur.execute(""" SELECT I.iname, I.calories, IIR.quantity, I.unit
                        FROM GROCERY_PROJECT_DB.Ingredients I INNER JOIN GROCERY_PROJECT_DB.IngredientsInRecipe IIR
                        ON I.ingredient_id = IIR.ingredient_id
                        WHERE IIR.recipe_id = '{}'""".format(recipe_dict['recipe_id']))
        ingredients = cur.fetchall()
        logger.info(ingredients)

    cur.close()
    del cur
    conn.close()

    # Sort by search score if search string is present

    recipe_dict['location'] = 'recipes/detail?recipeId={}'.format(recipe_dict['recipe_id'])
    recipe_dict.pop('recipe_id')
    response = recipe_dict
    #response['ingredients'] = {'item_count': len(ingredients_list)}

#    for ingredient in ingredients:
#        ingredient['location'] = 'getIngredients/detail?recipeId={}'.format(ingredient['ingredient_id'])
#        ingredient.pop('ingredient_id')

    response['ingredients'] = {'item_count': len(ingredients), 'items': ingredients}
    #response['items'] = recipe_json_list
    json_response = {
            "statusCode": 200,
            "body": json.dumps(response, indent=4)
        }
    logger.info(json_response)

    return json_response

class Recipe:
    def __init__(self, conn_dict):
        self.recipe_id = conn_dict['recipe_id']
        self.name = conn_dict['name']
        self.description = conn_dict['description']
        self.image_link = conn_dict['image_link']
        self.calories = conn_dict['calories']

