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
        if event['filter']:
            tag_filters = event['filter']
            tags = tag_filters.split(',')
    logger.info(tags)

    ingredient_list = []

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        base_query = "SELECT * FROM GROCERY_PROJECT_DB.Ingredients I " 
        if tags:
            intersect_query = " AND I.ingredient_id IN ".join(["(SELECT IT.ingredient_id FROM GROCERY_PROJECT_DB.IngredientTag IT WHERE IT.tag = '{}')".format(tag) for tag in tags])
            base_query += "WHERE I.ingredient_id IN {};".format(intersect_query)
        logger.info(base_query)

        cur.execute(base_query)
        ingredients = cur.fetchall()

        for ingredient in ingredients:
            ingredient_obj = Ingredient(ingredient)
            cur.execute("select * from GROCERY_PROJECT_DB.Ingredients I WHERE I.ingredient_id = '{}'".format(ingredient_obj.ingredient_id))
            ingredients = cur.fetchone()

            cur.execute("""SELECT IT.tag FROM GROCERY_PROJECT_DB.IngredientTag IT WHERE IT.ingredient_id = '{}'""".format(ingredient_obj.ingredient_id))
            tag_dict_list = cur.fetchall()
            logger.info("IngredientID {} Tags: {}".format(ingredient_obj.ingredient_id, tag_dict_list))
            tags = [tag_dict.get('tag') for tag_dict in tag_dict_list]

            #logger.info(ingredient)
            fuzzy_score = fuzz.partial_ratio(ingredient['iname'], search_string)
            if (len(search_string) == 0):
                ingredient_list.append({'Ingredient': ingredient_obj, 'Tags': tags, 'fuzzy_score': 100})
            elif (len(search_string) and fuzzy_score > 65):
                ingredient_list.append({'Ingredient': ingredient_obj, 'Tags': tags, 'fuzzy_score': fuzzy_score})

    cur.close()
    del cur
    conn.close()

    # Sort by search score if search string is present
    #logger.info(ingredient_list)
    if (len(search_string)):
        ingredient_list.sort(key=getFuzzyScore)
    else:
        ingredient_list.sort(key=getName)

    ingredient_json_list = []
    response = {'item_count': len(ingredient_list)}
    for ingredient in ingredient_list:
        idict = ingredient['Ingredient'].__dict__
        idict['tags'] = ingredient['Tags']
        idict['location'] = 'ingredients?ingredientId={}'.format(idict['ingredient_id'])
        idict.pop('ingredient_id')
        ingredient_json_list.append(idict)

    response['items'] = ingredient_json_list
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

