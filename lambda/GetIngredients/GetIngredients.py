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

    item_count = 0
    ingredient_list = []

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        cur.execute('select * from GROCERY_PROJECT_DB.Ingredients')
        ingredients = cur.fetchall()
        for ingredient in ingredients:
            item_count += 1
            #logger.info(ingredient)
            fuzzy_score = fuzz.partial_ratio(ingredient['iname'], search_string)
            if (len(search_string) and fuzzy_score > 65):
                ingredient_list.append({'Ingredient': Ingredient(ingredient), 'fuzzy_score': fuzzy_score})
            else:
                ingredient_list.append({'Ingredient': Ingredient(ingredient), 'fuzzy_score': 100})

    cur.close()
    del cur
    conn.close()

    # Sort by search score if search string is present
    #logger.info(ingredient_list)
    if (len(search_string)):
        ingredient_list.sort(key=getFuzzyScore)
    else:
        ingredient_list.sort(key=getName)

    response = {'item_count': len(ingredient_list)}
    response['items'] = [ingredient['Ingredient'].__dict__ for ingredient in ingredient_list]
    json_response = json.dumps(response, indent=4)
    logger.info(json_response)

    return json_response

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

