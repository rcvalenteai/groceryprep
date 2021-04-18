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
    recipe_url = event['recipeUrl']
    group_url = event['groupUrl']
    quantity = event['quantity']

    match = re.match(r".*?recipes/detail\?recipeId=(\d+)", recipe_url)
    if match is None:
        return {
            'errorMessage': 'Cannot extract recipeId from recipeUrl'
        }
    recipe_id = match.group(1)

    match = re.match(r".*?group\?groupId=(\d+)", group_url)
    if match is None:
        return {
            'errorMessage': 'Cannot extract groupId from groupUrl'
        }
    group_id = match.group(1)

    if not isinstance(quantity, int):
        return {
            'errorMessage': 'Quantity must be an int.'
        }

    logger.info("Recipe Id: {}".format(recipe_id))
    logger.info("Group Id: {}".format(group_id))

    try:
        conn = pymysql.Connect(host=rds_host, port=3306, user=name, passwd=password, db=db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    with conn.cursor() as cur:
        # Check the Recipe Exists
        cur.execute("SELECT * FROM GROCERY_PROJECT_DB.Recipes WHERE recipe_id = '{}'".format(recipe_id))
        recipe = cur.fetchone()
        if not recipe:
            return {
                'errorMessage': 'Recipe doesn\'t exist.'
            }
        logger.info("recipe Id: {}".format(recipe['recipe_id']))

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

        cur.execute("INSERT INTO GROCERY_PROJECT_DB.OrderHasRecipes (order_id, recipe_id, quantity) VALUES ('{}', '{}', {})".format(order['order_id'], recipe_id, quantity))
        conn.commit()

    cur.close()
    del cur
    conn.close()

    body = {
        'recipeLocation': 'recipes/detail?recipeId={}'.format(recipe_id),
        'orderLocation': 'orders/detail?orderId={}'.format(order['order_id']),
        'quantity': quantity
    }

    response = {
    'statusCode': 200,
    'body': body
    }
    logger.info(response)

    return response
