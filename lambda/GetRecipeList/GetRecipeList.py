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
    search_string = ""
    if 'search' in event:
        search_string = event['search']
    logger.info("Search string: {}".format(search_string))

    tags = []
    if 'filter' in event:
        tag_filters = event['filter']
        tags = tag_filters.split(',')
    logger.info(tags)

    recipe_list = []

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        base_query = "SELECT * FROM GROCERY_PROJECT_DB.Recipes R " 
        if tags:
            intersect_query = " AND R.recipe_id IN ".join(["(SELECT RT.recipe_id FROM GROCERY_PROJECT_DB.RecipeTag RT WHERE RT.tag = '{}')".format(tag) for tag in tags])
            base_query += "WHERE R.recipe_id IN {};".format(intersect_query)
        logger.info(base_query)
                        
        cur.execute(base_query)
        recipes = cur.fetchall()
        for recipe in recipes:
            #logger.info(recipe)
            fuzzy_score = fuzz.partial_ratio(recipe['name'], search_string)
            recipe_obj = Recipe(recipe)
            # calc calories
            if (recipe_obj.calories is None):
                cur.execute(""" SELECT sum(IIR.quantity * I.calories) as calories 
                                FROM GROCERY_PROJECT_DB.IngredientsInRecipe IIR, GROCERY_PROJECT_DB.Ingredients I 
                                WHERE recipe_id = '{}' and IIR.ingredient_id = I.ingredient_id;""".format(recipe_obj.recipe_id))
                calories = cur.fetchone()
                recipe_obj.calories = int(calories['calories'])

            cur.execute("""SELECT RT.tag FROM GROCERY_PROJECT_DB.RecipeTag RT WHERE RT.recipe_id = '{}'""".format(recipe_obj.recipe_id))
            tag_dict_list = cur.fetchall()
            logger.info("RecipeID {} Tags: {}".format(recipe_obj.recipe_id, tag_dict_list))
            tags = [tag_dict.get('tag') for tag_dict in tag_dict_list]

            if (len(search_string) == 0):
                recipe_list.append({'Recipe': recipe_obj, 'Tags': tags, 'fuzzy_score': 100})
            elif (len(search_string) and fuzzy_score > 65):
                recipe_list.append({'Recipe': recipe_obj, 'Tags': tags,  'fuzzy_score': fuzzy_score})

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
        rdict['Tags'] = recipe['Tags']
        rdict['location'] = 'recipes/detail?recipeId={}'.format(rdict['recipe_id'])
        rdict.pop('recipe_id')
        recipe_json_list.append(rdict)

    response['items'] = recipe_json_list
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

