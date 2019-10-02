##################
# JOE WINTER - Recipe Analysis
#
# CODE TO BUILD BASIC (SQL) TABLES CURRENTLY USED IN THIS VERSION OF THE PROJECT
# config variable at the stop would be set to your spefic SQL server set-up. You run this only once. 
#
##################

import mysql.connector


config = {
  'user': 'Joe',
  'password': 'testing',
  'host': 'localhost',
  'port': 8889, 
  'database': 'JWRecipes',
  'raise_on_warnings': True,
}

cnx = mysql.connector.connect(**config)
c = cnx.cursor()

c.execute("""CREATE TABLE recipes (
                recipe_id INTEGER AUTO_INCREMENT PRIMARY KEY, 
                recipe_name TEXT, 
                recipe_URL TEXT, 
                recipe_type TEXT);""")

c.execute('''CREATE TABLE ingredients (
            ingredient_id INTEGER AUTO_INCREMENT PRIMARY KEY , 
            ingredient_name TEXT)''')

c.execute('''CREATE TABLE ingredient_details (
            recipe_id INTEGER, 
            ingredient_id INTEGER, 
            list_order INTEGER, 
            amount TEXT, 
            unit TEXT, 
            PRIMARY KEY (recipe_id, ingredient_id),
            FOREIGN KEY (recipe_id) REFERENCES recipes (recipe_id), 
            FOREIGN KEY (ingredient_id) REFERENCES ingredients (ingredient_id))''')

cnx.close()