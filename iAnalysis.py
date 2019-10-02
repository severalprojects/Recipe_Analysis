#######################################
# JOE WINTER - Recipe Analysis
#
# CODE TO CONSOLIDATE scraped recipe data
# attempts to group ingredients (described with a variety of non-matching strings). 
# 
# Allows for user corrections to automated ingredient sorting/matching and save binary file to upload to database
#
# Gives preliminary report showing the frequency of ingredients in recipes for the given food. 
#
########################################

import pickle, random, operator, sys
from collections import defaultdict

import ingParse as IP

ingredient_groups = []

nonIEntries = 0

# noName = 0

#hardcoded synonyms.... not really a sustainable model, prob need some NLP methods here... or rather HUMAN INTELLIGENCE
#Mostly used for development/testing
SYNONYMS = [['half and half', 'half-and-half', 'half & half'], ['breadcrumbs', 'bread crumbs'], ['ground beef', 'ground sirloin', 'ground chuck']]

def hasSynonyms(IGstring):
    for item in SYNONYMS:
        if IGstring in item:
            # print("found {} in {}".format(IGstring, item))
            return item

    return False

#some hardcoded rules and exceptions
def rules_and_exceptions(toMatch, item):
    if toMatch == 'salt' and ('salted' or 'butter') in item:
        return False
    
    if toMatch == 'pepper' in item:
        
        if 'green' in item:
                return False

        if 'red' in item:
                return False
        if 'bell' in item:
                return False
        if 'cayenne' in item:
                return False
        else:
            return True

    if toMatch == 'butter' and 'peanut' in item:
        return False

    if toMatch == 'sugar' and 'brown' in item:
        return False
    
    # if toMatch == 'breadcrumbs' or toMatch == 'bread crumbs':
    #     if 'panko' in item:
    #         return False
        
            
                
    
    else:
        return True


#method to automate consolidation of ingredients, ie, grouping together ingredients that we actually/probably want
#to consider "the same" for the purposes of analysis. for example: "butter," "unsalted butter," and "salted butter" will all
#get the group name (key = gname) "butter"

def groupIngredients(iDicts): 
    
    #code to remap ingredient groups goes here
    
    #this block executes only the second time this function is called
    #which is after user input adds a new group name to help consolidate 
    #the ingredient list
    if len(ingredient_groups) > 0:
        for recipe in iDicts:
            for ingredient in recipe:
                if ingredient_groups[-1] in ingredient['name']:
                    ingredient['gname'] = ingredient_groups[-1]
                    ingredient['name'] = ingredient['name'].strip()
        
        
        

    else:
        for recipe in iDicts:
            for ingredient in recipe:
                if 'name' in ingredient.keys():
                    ingredient['name'] = ingredient['name'].strip()
        
        nameless=0
        nonIngredEntries=0
        
        #make a set of unique ingredients // ie, this filters out already redundant strings (ie exact matches)
        ingredientSet = set()
        
        for recipe in iDicts:
            for ingredient in recipe:
                try:    
                    ingredientSet.add(ingredient['name']) 
                
                except:
                    nameless +=1

                    continue

        #quick fix to pull out erroneous empty ingredients 
        if '' in ingredientSet:
            ingredientSet.remove('')
        
        if 'NONE' in ingredientSet:
            ingredientSet.remove('NONE')

        #sort by length
        ingredient_list = sorted(list(ingredientSet), key = len)

        numIG = len(ingredient_list)

        print("initial consolidation shows {} distinct ingredient strings".format(numIG))

        groups = []
        ugroups = []
        for toMatch in ingredient_list: #consider 'unique' ingredient strings, ordered from shortest to longest
            
            matches = []
            toremove = []
            syns = hasSynonyms(toMatch)
            # syns = hasSynonyms(toMatch) #see if this ingredient has synonyms
            for item in ingredientSet:
                if toMatch in item: 
                    if rules_and_exceptions(toMatch, item):
                        matches.append(item)
                        toremove.append(item)
                #check for tricky synonyms
                elif syns: 
                    for term in syns:
                        if term in item:
                            # print("{} is a synonym for {}".format(item, toMatch))
                            matches.append(item)
                            toremove.append(item)
                            break #leave the loop if you've matched one synonym
                    

                # consolodated_IL.append(matches)       

            #remove items that have been matched from the set so we don't keep trying to match them
            
            for item in toremove:
                if item in ingredientSet: 
                    ingredientSet.remove(item)

            groups.append([matches, toMatch])
            

        for item in groups:
            if len(item[0]) > 0:
                #earlier in the process 'NONE' is assigned to unfilled keys in dict. Don't want to treat 'NONE' as an ingredient to match
                if item[1] is not 'NONE':
                    ugroups.append(item)
    

        totalIs = 0 
        ugroups.sort(key=len)
        for item in ugroups:
            totalIs += len(item[0])
            # print(item)
        
    
        print("automatically grouped {} ingredient strings into {} distinct ingredients".format(totalIs, len(ugroups)))  
    
        # global noName 
        # noName = nameless
        # print(ugroups)

        for group in ugroups:
            #each list in ugroups is a pair with group[0] a list of elements being grouped together under the 'gname'
            #stored in group[1]
            
            if len(group[0]) > 1: #scan through all the dictionaries in iDict and add 'gname' element: 
                for string in group[0]:
                    for recipe in iDicts:
                        for ingredient in recipe:
                            if 'name' in ingredient.keys():
                                if string == ingredient['name']:
                                    ingredient['gname'] = group[1].strip() 

    
    return iDicts

#once groups are established, this method goes through the recipes and tallies how many recipes contain each unique ingredient
#after code does its work, allows human input to compensate for machine error
#as seemingly unique ingredients are the first indicator of imperfect sorting/grouping

def binIngredients():
    global nonIEntries
    ingredientSet = set()
    nonameoramt = 0
     

    uniqueIngs = []
    recipeIndex = -1

    nonIngs = defaultdict(list)

    for recipe in masterIGs:
        recipeIndex +=1
        ingIndex = -1
        for ingredient in recipe:
            ingIndex +=1
            # thedict = eval(ingredient)
            # print(ingredient)


            if 'gname' in ingredient.keys(): 
                ingredientSet.add(ingredient['gname'])  #.strip()) .... come back to this... want to strip ingredient strings before loading into this database
            
            elif  (ingredient['amt'] == 'NONE' and ingredient['unit'] == 'NONE'): 
                    # print(ingredient)
                    nonIEntries +=1
                    nonIngs[recipeIndex].append(ingIndex)
                    continue 
            
            elif 'name' in ingredient.keys():
                #these are the (possibly) unique ingredients:
                ingredientSet.add(ingredient['name'])
                uniqueIngs.append([recipeIndex, ingIndex])

            else:
                nonameoramt +=1


    # print("found {} distinct ingredients".format(len(ingredientSet)))
    # print(ingredientSet)
    # print(ingredientSet)

    redundIGs = 0

    ingredientCounts = {}


    #remove the suspicious (non) ingredients. later we can add user input to review if we want to toss these.
    for key in nonIngs:
        poplist = sorted(nonIngs[key], reverse=True)
        for item in poplist:
            masterIGs[key].pop(item)


    for item in ingredientSet:

        #initialize counts for an ingredient
        ingredientCounts[item] = 0
  
        for recipe in masterIGs:
        
            recipeIcount = 0
            hasingredient = False
            for ingredient in recipe:
                if item in ingredient.values(): 
                    hasingredient = True
                    recipeIcount +=1
                    
            if hasingredient:
                ingredientCounts[item] += 1
            if recipeIcount > 1:
                #redundant ingredients are caught when a recipe has same ingredient in more than one place
                redundIGs += (recipeIcount - 1)


    total = 0

    for key in ingredientCounts:
        total+=ingredientCounts[key]

    print("this sorting acounts for {} of the original {} ingredient entries".format(total,totalIs))
    print("and we found {} redundant ingredient entries".format(redundIGs))
    print("and {} ingredients missing name or amt".format(nonameoramt))
    print("and {} entries were probably not ingredients".format(nonIEntries))
    leftover = totalIs - (nonameoramt+total+redundIGs+nonIEntries)
    print("{} + {} + {} + {}= {}".format(total, redundIGs, nonameoramt, nonIEntries, nonameoramt+total+redundIGs+nonIEntries))
    if leftover == 0: 
        print("nice sorting!")
    else:
        print("you might have double-sorted some ingredients!")
    print("---------------------")

   
    print("##########################")
    print("## CONSOLIDATION REPORT ##")
    print("##########################")

    for ingredient in sorted(ingredientCounts, key=ingredientCounts.get, reverse=True):
        if ingredientCounts[ingredient] > 1:
            print("{} recipes contain {}".format(ingredientCounts[ingredient], ingredient))  
        else:
            print("{} recipe contains {}".format(ingredientCounts[ingredient], ingredient)) 
    print("---------------------------")
    # print("There are {} unique ingredients that haven't been edited.".format(len(uniqueIngs)))
    print("AUTOMATED ingredient consolodation remains IMPERFECT.")
    toEdit = input("Do you want to leverage HUMAN INTELLIGENCE? y/n?\n".format(len(uniqueIngs)))
    if toEdit == "y":
        editMode = input("Type \'c\' to change the name of an ingredient. Type \'g\' to make new group\n")
        if editMode == 'g':
            newgroup = input("add the name of a new group that will help consolidate ingredient list: \n")
            ingredient_groups.append(newgroup)
            groupIngredients(masterIGs)
      
        if editMode == 'c':
            tochange = input("ingredient name you wish to change: \n")
            changeto = input("new name: \n")
            for recipe in masterIGs:
                for ingredient in recipe:
                    if 'gname' in ingredient.keys():
                        if ingredient['gname'] == tochange:
                            ingredient['gname'] = changeto
                    elif ingredient['name'] == tochange:
                        ingredient['name'] = changeto
        else: 
            print("improper input")
        print("---------------------------")            
        print("Reconsolidating recipe ingredients based on HUMAN INTELLIGENCE: \n")
        return binIngredients()
    
    else:
        print("OK, let's hope this is properly sorted.")
        print("Formatting and writing info to file for future database update.")
        return masterIGs

######################################LOADING THE FILE AND PARSING IT 

#expecting a file name argument
if len(sys.argv) < 2:
    print("no file name entered")
    print("goodbye")
    exit()

else:
    filepath = sys.argv[1]

#first open the data file that has dictionaries of ingredients in this format:
#{amt: , unit:, name: }

ingredientFile = open(filepath, 'r')

masterURLs = []
masterIGs = []
masterTitles = []
entries = 0



lines = [line.rstrip('\n') for line in ingredientFile]

#reading in lines of a text document to make various lists
#to-do: re-do this with pickled binary, instead of text file

for count in range(len(lines)//3): #note: assumes number of lines is divisble by 3 and  every 3 lines are URL, TITLE, INGREDIENTS
    
    masterURLs.append(lines[count*3])
    
    masterTitles.append(lines[count*3+1])
    masterTitles[-1].replace('\'', '')
    masterTitles[-1].replace('\'', '')
    
    #if the ingredients are formatted as a list (not a dict), this will just be a string
    #and we know its a non-wordpress recipe.

    # reimplement with pickled data from previous step (instead of using 'eval' on text file... more secure/better)

    if type(eval(lines[count*3+2].lower())[0]) == str:
        thelist = eval(lines[count*3+2].lower())

        while '' in thelist:
            thelist.remove('')
        masterIGs.append(IP.PIList(thelist)) ##convert non-wordpress ingredient list to dictionary format. 
    
    else: #this entry was from a wordpress site so already parsed as dictionary format
        masterIGs.append(eval(lines[count*3+2].lower())) #made all strings lowercase to make matching less of a headache
        
        #MAKE SURE THESE WP DICTS HAVE ALL THE SAME KEYS AS OUR PARSED LISTS
        for ingredient in masterIGs[-1]:
            if 'amt' not in ingredient.keys():
                ingredient['amt'] = 'NONE'
                # print("FOUND NON AMT")
            if 'unit' not in ingredient.keys():
                ingredient['unit'] = 'NONE'
                # print("FOUND NON UNIT")
                # print(ingredient)
            if 'name' not in ingredient.keys():
                ingredient['name'] = 'NONE'
                # print("FOUND NON NAME")

ingredientFile.close()

##################################################### FILE IS PARSED NOW GROUP/SORT/ANALYSE INGREDIENTS
print("---------------------")
print("looking at {} recipes".format(len(masterIGs)))
totalIs = 0
for item in masterIGs:
    totalIs += len(item)

print("original recipe list had a total of {} ingredient entries".format(totalIs))

GI = groupIngredients(masterIGs)  #output here can be used to load database along with list of URLs and titles. 

#main preliminary look at distribution of ingredients in the recipes happens here, 
#along with opportunity to correct errors, etc, before saving sorted data for uploading to DB
final_sorted_IGs = binIngredients()

recipe_type = input("Enter the recipe type (eg \"meatloaf\"):\n")
# [[reecipe_title, recipe_URL, recipe_type, [Recipe Ingredient Dicts]],

save_data = []

for i in range(len(final_sorted_IGs)):
    entry = [masterTitles[i], masterURLs[i], recipe_type, final_sorted_IGs[i]]
    save_data.append(entry)
    # To_Upload_File.write(str(entry)+"\n")
    # To_Upload_File.write(str(masterTitles[i]) + "\n")
    # To_Upload_File.write(str(masterURLs[i]) + "\n")
    # To_Upload_File.write(recipe_type+"\n")
    # To_Upload_File.write(str(final_sorted_IGs[i]))

#save the sorted/organized data as a binary, to use in load_recipes.py script
with open("data/upload_"+recipe_type, 'wb') as TOSAVE:
    pickle.dump(save_data, TOSAVE)




