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
    meal_plan_id = event['mealPlanId']
    logger.info("mealPlan Id: {}".format(meal_plan_id))
    if (meal_plan_id is None or len(meal_plan_id) == 0):
        logger.error("No meal_plan id specified for this endpoint")
        return { "No Meal Plan with Specified ID" }

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        cur.execute("select * from GROCERY_PROJECT_DB.MealPlans R where R.meal_plan_id = '{}'".format(meal_plan_id))
        meal_plan_dict = cur.fetchone()

        cur.execute(""" SELECT MPC.recipe_id, R.name, R.description, R.image_link, R.calories, R.servings
                        FROM GROCERY_PROJECT_DB.MealPlanContains MPC, GROCERY_PROJECT_DB.Recipes R
                        WHERE MPC.meal_plan_id = '{}' AND MPC.recipe_id = R.recipe_id""".format(meal_plan_dict['meal_plan_id']))
        recipes = cur.fetchall()
        logger.info(recipes)
        recipes_list = []
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
            recipes_list.append(rdict)

    cur.close()
    del cur
    conn.close()

    # Sort by search score if search string is present

    meal_plan_dict['location'] = 'meal_plan/detail?meal_planId={}'.format(meal_plan_dict['meal_plan_id'])
    meal_plan_dict.pop('meal_plan_id')
    response = meal_plan_dict
    response['ingredients'] = {'item_count': len(recipes_list), 'items': recipes_list}
    json_response = {
            "statusCode": 200,
            "body": meal_plan_dict
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

class Ingredient:
    def __init__(self, conn_dict):
        self.ingredient_id = conn_dict['ingredient_id']
        self.iname = conn_dict['iname']
        self.calories = conn_dict['calories']
        self.price = conn_dict['price']
        self.quantity = conn_dict['quantity']
        self.unit = conn_dict['unit']
