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

    meal_plan_list = []

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        base_query = "SELECT * FROM GROCERY_PROJECT_DB.MealPlans MP " 
        if tags:
            intersect_query = " AND MP.meal_plan_id IN ".join(["(SELECT MPT.meal_plan_id FROM GROCERY_PROJECT_DB.MealPlanTag MPT WHERE MPT.tag = '{}')".format(tag) for tag in tags])
            base_query += "WHERE MP.meal_plan_id IN {};".format(intersect_query)
        logger.info(base_query)
                        
        cur.execute(base_query)
        meal_plans = cur.fetchall()
        for meal_plan in meal_plans:
            #logger.info(meal_plan)
            fuzzy_score = fuzz.partial_ratio(meal_plan['name'], search_string)
            meal_plan_obj = MealPlan(meal_plan)
            logger.info(meal_plan_obj.description)

            cur.execute("""SELECT MPT.tag FROM GROCERY_PROJECT_DB.MealPlanTag MPT WHERE MPT.meal_plan_id = '{}'""".format(meal_plan_obj.meal_plan_id))
            tag_dict_list = cur.fetchall()
            logger.info("meal_planID {} Tags: {}".format(meal_plan_obj.meal_plan_id, tag_dict_list))
            tags = [tag_dict.get('tag') for tag_dict in tag_dict_list]

            if (len(search_string) == 0):
                meal_plan_list.append({'meal_plan': meal_plan_obj, 'Tags': tags, 'fuzzy_score': 100})
            elif (len(search_string) and fuzzy_score > 65):
                meal_plan_list.append({'meal_plan': meal_plan_obj, 'Tags': tags,  'fuzzy_score': fuzzy_score})

    cur.close()
    del cur
    conn.close()

    # Sort by search score if search string is present
    #logger.info(meal_plan_list)
    if (len(search_string)):
        meal_plan_list.sort(key=getFuzzyScore)
    else:
        meal_plan_list.sort(key=getName)

    response = {'item_count': len(meal_plan_list)}

    meal_plan_json_list = []
    for meal_plan in meal_plan_list:
        mpdict = meal_plan['meal_plan'].__dict__
        mpdict['Tags'] = meal_plan['Tags']
        mpdict['location'] = 'mealplan/detail?mealPlanId={}'.format(mpdict['meal_plan_id'])
        mpdict.pop('meal_plan_id')
        meal_plan_json_list.append(mpdict)

    response['items'] = meal_plan_json_list
    logger.info(response)

    return response

def getFuzzyScore(e):
    return e['fuzzy_score']

def getName(e):
    return e['meal_plan'].name

class MealPlan:
    def __init__(self, conn_dict):
        self.meal_plan_id = conn_dict['meal_plan_id']
        self.name = conn_dict['name']
        self.description = conn_dict['description'].decode("utf-8")
        self.image_link = conn_dict['image_link']

