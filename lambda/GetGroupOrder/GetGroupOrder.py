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
    if 'groupId' not in event:
        return {"No Group ID specified."}
    group_id = event['groupId']

    recipe_list = []
    ingredient_list = []

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        # Check the Order Group Exists
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.OrderGroups WHERE order_group_id = '{}'".format(group_id))
        group = cur.fetchone()
        if not group:
            return {
                'errorMessage': 'Group doesn\'t exist.'
            }
        logger.info("Group Id: {}".format(group['order_group_id']))

        # Check there is an open order for Group
        cur.execute("select * from GROCERY_PROJECT_DB.Order O where O.order_group_id = '{}' and O.is_open = 1".format(group_id))
        order = cur.fetchone()
        if not order:
            return {
                    'errorMessage': 'There is not an open order for this groupId: {}'.format(group_id)
            }
        logger.info("Order Id: {}".format(order['order_id']))

        cur.execute(""" SELECT OHR.recipe_id, R.name, R.description, R.image_link, R.calories, R.servings
                        FROM GROCERY_PROJECT_DB.OrderHasRecipes OHR, GROCERY_PROJECT_DB.Recipes R
                        WHERE OHR.order_id = '{}' AND OHR.recipe_id = R.recipe_id""".format(order['order_id']))
        recipes = cur.fetchall()
        logger.info(recipes)
        for recipe in recipes:
            rdict = recipe
            if (recipe['calories'] is None):
                cur.execute(""" SELECT sum(IIR.quantity * I.calories) as calories 
                                FROM GROCERY_PROJECT_DB.IngredientsInRecipe IIR, GROCERY_PROJECT_DB.Ingredients I 
                                WHERE recipe_id = '{}' and IIR.ingredient_id = I.ingredient_id;""".format(recipe['recipe_id']))
                calories = cur.fetchone()
                rdict['calories'] = int(calories['calories'])

            cur.execute(""" SELECT I.iname, I.calories, IIR.quantity, I.unit
                            FROM GROCERY_PROJECT_DB.Ingredients I INNER JOIN GROCERY_PROJECT_DB.IngredientsInRecipe IIR
                            ON I.ingredient_id = IIR.ingredient_id
                            WHERE IIR.recipe_id = '{}'""".format(recipe['recipe_id']))
            ingredients = cur.fetchall()
            logger.info(ingredients)

            rdict['location'] = 'recipes/detail?recipeId={}'.format(rdict['recipe_id'])
            rdict.pop('recipe_id')
            rdict['item_count'] = len(ingredients)
            rdict['items'] = ingredients
            recipe_list.append(rdict)

        cur.execute(""" SELECT OHI.ingredient_id, I.iname, I.calories, I.price, I.quantity, I.unit
                        FROM GROCERY_PROJECT_DB.OrderHasIngredients OHI, GROCERY_PROJECT_DB.Ingredients I
                        WHERE OHI.order_id = '{}' AND OHI.ingredient_id = I.ingredient_id""".format(order['order_id']))
        ingredients = cur.fetchall()
        logger.info(ingredients)
        for ingredient in ingredients:
            idict = ingredient
            idict['location'] = 'ingredients/detail?ingredientId={}'.format(idict['ingredient_id'])
            idict.pop('ingredient_id')
            ingredient_list.append(idict)

    cur.close()
    del cur
    conn.close()

    # Sort by search score if search string is present
    #logger.info(ingredient_list)

    ingredient_json_list = []
    response = {'recipe_count': len(recipe_list), 'ingredient_count': len(ingredient_list)}
    response['recipes'] = recipe_list
    response['ingredients'] = ingredient_list
    logger.info(response)

    return response

def getFuzzyScore(e):
    return e['fuzzy_score']

def getName(e):
    return e['Ingredient'].iname

class Ingredient:
    def __init__(self, conn_dict):
        self.ingredient_id = conn_dict['ingredient_id']
        self.iname = conn_dict['iname']
        self.calories = conn_dict['calories']
        self.price = conn_dict['price']
        self.quantity = conn_dict['quantity']
        self.unit = conn_dict['unit']

