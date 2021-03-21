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
    search_string = event['search']
    logger.info("Search string: {}".format(search_string))
    if (search_string is None):
        search_string = ""

    recipe_list = []

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        cur.execute('select * from GROCERY_PROJECT_DB.Recipes')
        recipes = cur.fetchall()
        for recipe in recipes:
            #logger.info(recipe)
            fuzzy_score = fuzz.partial_ratio(recipe['name'], search_string)
            recipe_obj = Recipe(recipe)
            # calc calories
            if (recipe_obj.calories is None):
                cur.execute(""" SELECT sum(IIR.quantity * I.calories) as calories 
                                FROM GROCERY_PROJECT_DB.IngredientsInRecipe IIR, GROCERY_PROJECT_DB.Ingredients I 
                                WHERE recipe_id = '1' and IIR.ingredient_id = I.ingredient_id;""")
                calories = cur.fetchone()
                recipe_obj.calories = int(calories['calories'])


            if (len(search_string) == 0):
                recipe_list.append({'Recipe': recipe_obj, 'fuzzy_score': 100})
            elif (len(search_string) and fuzzy_score > 65):
                recipe_list.append({'Recipe': recipe_obj, 'fuzzy_score': fuzzy_score})

    cur.close()
    del cur
    conn.close()

    # Sort by search score if search string is present
    #logger.info(recipe_list)
    if (len(search_string)):
        recipe_list.sort(key=getFuzzyScore)
    else:
        recipe_list.sort(key=getName)

    response = {'item_count': len(recipe_list)}

    recipe_json_list = []
    for recipe in recipe_list:
        rdict = recipe['Recipe'].__dict__
        rdict['location'] = 'getRecipes/detail?recipeId={}'.format(rdict['recipe_id'])
        rdict.pop('recipe_id')
        recipe_json_list.append(rdict)

    response['items'] = recipe_json_list
    json_response = json.dumps(response, indent=4)
    logger.info(json_response)

    return json_response

def getFuzzyScore(e):
    return e['fuzzy_score']

def getName(e):
    return e['Recipe'].name

class Recipe:
    def __init__(self, conn_dict):
        self.recipe_id = conn_dict['recipe_id']
        self.name = conn_dict['name']
        self.description = conn_dict['description']
        self.image_link = conn_dict['image_link']
        self.calories = conn_dict['calories']

