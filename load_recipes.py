import mysql.connector
import sys
import pickle

######################

#method to unpickle binary file with data to load to database
#(file generated in iAnalysis.py)
def loadProcessedRecipes(thefilepath):
    print("attempting to load file {}".format(thefilepath))

    with open(thefilepath, "rb") as recipe_file:
        recipe_list = pickle.load(recipe_file)
    
    return recipe_list
    
###method to extract the current set of ingredients loaded into database
#useful for seeing if data to upload contains any new ingredients
def getIngredientSet(cursor):
    ingredientSet = set()
    cursor.execute('''SELECT ingredient_name FROM ingredients''')
    results = cursor.fetchall()  
    print("there are currently {} ingredients in the database".format(len(results)))
    for item in results:
        ingredientSet.add(item[0])
    return ingredientSet

####method to check if a string is an ingredient name stored in the database (based on querying the specific string)
def ingredientFiled(iString, cursor):
    cursor.execute('''SELECT * FROM ingredients
                        WHERE ingredient_name = \'{}\''''.format(iString))
    result = cursor.fetchall()
    if result:
        return True
    else:
        return False

#see if a URL has already been uploaded to the database (this is the uniqueID of recipe table 
# prevents duplicte entries...)
def URLFiled(URLString, cursor):
    cursor.execute('''SELECT * FROM recipes
                        WHERE recipe_URL = \'{}\''''.format(URLString))
    result = cursor.fetchall()
    if result:
        return True
    else:
        return False

#####method loads a list of ingredients into databse (checks against duplicate entries)
def loadIngredients(i_list, cursor, connection):
    newIs = []
    oldIs = []
    for ingredient in i_list:
        if not ingredientFiled(ingredient, cursor):
            # print('trying to insert {} into database'.format(ingredient))
            insertString = '''INSERT INTO ingredients (ingredient_name) VALUES (\'{}\')'''.format(ingredient)
            # print(insertString)
            cursor.execute(insertString)
            newIs.append(ingredient)
        else:
            # print('{} already in database'.format(ingredient))
            oldIs.append(ingredient)

    connection.commit()
    if newIs:
        print("These ingredients were added to the database: {}".format(newIs))
    else:
        print("No new ingredients added to database")
    print("Tried to add these ingredients but they were already there: {}".format(oldIs))


#####method to load recipes into database. 
def loadRecipes(r_list, cursor, connection): 
    
    ##assume recipe list (r_list) contains lists with 4 elements:
    # 
    #  [[reecipe_title, recipe_URL, recipe_type, [Recipe Ingredient Dicts]], 
    #   [reecipe_title, recipe_URL, recipe_type, [Recipe Ingredient Dicts]],
    #   [reecipe_title, recipe_URL, recipe_type, [Recipe Ingredient Dicts]],  
    #   [reecipe_title, recipe_URL, recipe_type, [Recipe Ingredient Dicts]]
    #                                                                       ]    
    
    newRs = []
    oldRs = []
    
    IngredientsToAdd = set()
    
    for recipe in r_list:
        title = recipe[0]
        URL = recipe[1]
        rtype = recipe[2]
        ing_dicts = recipe[3]
        if not URLFiled(URL, cursor):
            #first load the recipe title, url, etc into recipe table
            insertString = '''INSERT INTO recipes (recipe_name, recipe_URL, recipe_type)
                                VALUES (\'{}\', \'{}\', \'{}\')'''.format(title, URL, rtype) 
            cursor.execute(insertString)
            newRs.append(title)
            #go through the recipe and try to add ingredients to a set of ingredients to upload to database
            #making this set avoids excess queries, saves them all till end. 
            for ingredient in ing_dicts:
                # print(ingredient)
                if 'gname' in ingredient.keys():
                    IngredientsToAdd.add(ingredient['gname'])
                elif 'name' in ingredient.keys():
                    IngredientsToAdd.add(ingredient['name'])
            #now load recipe ingredients into ingredients table:
        else:
            oldRs.append(title)
    IList = list(IngredientsToAdd)
    
    print("These recipes were added to the database:\n\n{}\n".format(newRs))
    print("Tried to add these recipes but they were already there: \n\n{}\n".format(oldRs))
    
    #load any new ingredients from these recipes into the ingredients table of DB
    loadIngredients(IList, cursor, connection)

    #now add info from the recipes to ingredient_details table
    for entry in r_list:
        
        #identify the recipe_id based on its URL
        URL = entry[1]
        query = '''SELECT recipe_id from recipes 
                WHERE recipe_URL=\'{}\''''.format(URL)  
        cursor.execute(query)
        results = cursor.fetchall()

        #this gives you the unique recipe_id
        the_r_id = results[0][0]
        
        #load up the list of dictionaries representing the recipe
        recipe = entry[3]
        
        #start a counter for the order in which ingredients appear
        order=1

        #go through each ingredient in the dictioary, get it's ingredient_id based on its name. 
        for ingredient in recipe:
            if 'gname' in ingredient.keys():
                iname = ingredient['gname']
            else:
                iname = ingredient['name']
            query = '''SELECT ingredient_id from ingredients
                        WHERE ingredient_name=\'{}\''''.format(iname)
            cursor.execute(query)
            results = cursor.fetchall()
            #this is the ingredient_id
            the_i_id = results[0][0]

            if 'amt' in ingredient.keys():
                amount = ingredient['amt']
                if amount == '':
                    amount = 0
            else: 
                amount = 0

            if 'unit' in ingredient.keys():
                unt = ingredient['unit']
            else: 
                unt = 'None'

            #insert into the table the (recipe_id, ingredient_id) tuple and the relevant info. 
            insertStatement = '''INSERT INTO ingredient_details (recipe_id, ingredient_id, amount, unit, list_order )
                                VALUES ({}, {}, \'{}\', \'{}\', {})'''.format(the_r_id, the_i_id, amount, unt, order)
            

            query = '''SELECT * from ingredient_details WHERE 
            recipe_id=\'{}\' AND ingredient_id = \'{}\''''.format(the_r_id, the_i_id)
            cursor.execute(query)
            results = cursor.fetchall()
            # print("results: {}".format(results))
            
            if not results:
                # print(insertStatement)
                cursor.execute(insertStatement)
                order+=1
        connection.commit()    

            ####need to get the recipe_name too! 



########################

if len(sys.argv) < 2:
    print("no filename specified to load... goodbye")
    exit()

else: 
    filepath = sys.argv[1]
    print("attempting to load file {}".format(filepath))

config = {
  'user': 'Joe',
  'password': 'testing',
  'host': 'localhost',
  'port': 8889, 
  'database': 'JWRecipes',
  'raise_on_warnings': True,
}

#open connection to database
cnx = mysql.connector.connect(**config)
c = cnx.cursor()

#load in binary file 
toLoad = loadProcessedRecipes(filepath)

#look for new data in the file and upload it to the DB
loadRecipes(toLoad, c, cnx)

cnx.close()



