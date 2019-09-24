#looking at ingredients in a recipe class

#first open the data file that has dictionaries of ingredients in this format:
#{amt: , unit:, name: }

import random
import operator
import sys
import ingParse as IP

noName = 0

#SYNONYMS = [['half and half', 'half-and-half', 'half & half'], ['breadcrumbs', 'bread crumbs']]
SYNONYMS = [['half and half', 'half-and-half', 'half & half'], ['breadcrumbs', 'bread crumbs'], ['ground beef', 'ground sirloin', 'ground chuck']]


def hasSynonyms(IGstring):
    for item in SYNONYMS:
        if IGstring in item:
            # print("found {} in {}".format(IGstring, item))
            return item

    return False

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



def groupIngredients(iDicts): #a list of dictionaries containing ingredients, then group them, and add group 'keys' to the relevant dictionaries
    

    #remove extra spaces from ingredient names... will do this back when links are harvested, but until then, do it here. 

    for recipe in iDicts:
        # print(type(recipe))
        for ingredient in recipe:
            if 'name' in ingredient.keys():
                ingredient['name'] = ingredient['name'].strip()
    
    nameless=0
    #make a set of unique ingredients // ie, this filters out already redundant strings
    ingredientSet = set()
    
    for recipe in iDicts:
        for ingredient in recipe:
            try:
                ingredientSet.add(ingredient['name']) #strip()  #.strip()) .... come back to this... want to strip ingredient strings before loading into this database
            except:
                nameless +=1
                print("nameless: {}".format(ingredient))
                continue

    #make a list of unique ingredient strings, sorted by length. 
    if '' in ingredientSet:
        ingredientSet.remove('')
    
    ingredient_list = sorted(list(ingredientSet), key = len)
    # print(ingredient_list)
    numIG = len(ingredient_list)

    print("initial consolidation shows {} distinct ingredient strings".format(numIG))

    groups = []
    ugroups = []
    for toMatch in ingredient_list: #consider 'unique' ingredient strings, ordered from shortest to longest
        # print("I think all these ingredients are the same as {}:".format(toMatch))
        matches = []
        toremove = []
        syns = hasSynonyms(toMatch)
        # syns = hasSynonyms(toMatch) #see if this ingredient has synonyms
        for item in ingredientSet:
            if toMatch in item: #should handle case if they are identical first --> is this where we're getting redundancy? 

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

        for item in toremove:
            if item in ingredientSet: 
                ingredientSet.remove(item)

        groups.append([matches, toMatch])
        

    for item in groups:
        if len(item[0]) > 0:
            ugroups.append(item)
            # print('ingredients groups as \'{}\' thing'.format(item[1]))
    
    # for item in ugroups:
        # print(item)     

    totalIs = 0 
    ugroups.sort(key=len)
    for item in ugroups:
        totalIs += len(item[0])
        # print(item)
    
   
    print("grouped {} ingredient strings into {} distinct ingredients".format(totalIs, len(ugroups)))  
    print("there were {} entries with no name-field".format(nameless))
    global noName 
    noName = nameless
    # print(ugroups)

    for group in ugroups:
        #each list in ugroups is a pair with group[0] a list of elements being grouped together under the 'gname' group[1]
    # if len(group[0]) > 1: #scan through all the dictionaries in iDict and add 'gname' element: 
        for string in group[0]:
            for recipe in iDicts:
                for ingredient in recipe:
                    if 'name' in ingredient.keys():
                        if string == ingredient['name']:
                            ingredient['gname'] = group[1].strip() 

    # print(iDicts)
    return iDicts


######################################
if len(sys.argv) < 2:
    print("no file name entered")
    print("goodbye")
    exit()

else:
    filepath = sys.argv[1]


ingredientFile = open(filepath, 'r')

masterURLs = []
masterIGs = []
masterTitles = []
entries = 0

# bigstring = ingredientFile.readlines()
lines = [line.rstrip('\n') for line in ingredientFile]

for count in range(len(lines)//3): #note: assumes number of lines is divisble by 3 and lines are URL, TITLE, INGREDIENTS
    
    masterURLs.append(lines[count*3])
    
    masterTitles.append(lines[count*3+1])
    
    if type(eval(lines[count*3+2].lower())[0]) == str:
        #print('parsing the string from {} into dictionaries:'.format(masterURLs[count//2]))
        # print(IP.PIList(eval(lines[count].lower())))

        ###quick fix to remove empty space items from list:
        thelist = eval(lines[count*3+2].lower())

        # if '' in thelist:
        #     print("FOUND EMPTY STRING IN THE LIST")
        while '' in thelist:
            thelist.remove('')
            # print("REMOVED AN EMPTY SPACE FROM LIST")
        masterIGs.append(IP.PIList(thelist)) ##convert non-wordpress ingredient list to dictionary format. 
    else:
        masterIGs.append(eval(lines[count*3+2].lower())) #made all strings lowercase to make matching less of a headache

ingredientFile.close()

print("looking at {} recipes".format(len(masterIGs)))
totalIs = 0
for item in masterIGs:
    totalIs += len(item)

print("original recipe list had a total of {} ingredient entries".format(totalIs))

GI = groupIngredients(masterIGs)  #output here can be used to load database along with list of URLs and titles. 
# print(masterTitles)
# print(masterURLs)
# print(GI)
#go through the master list and store the set of ingredients: 
ingredientSet = set()

for recipe in masterIGs:
    for ingredient in recipe:
        # thedict = eval(ingredient)
        # print(ingredient)
        if 'gname' in ingredient.keys(): 
            ingredientSet.add(ingredient['gname'])  #.strip()) .... come back to this... want to strip ingredient strings before loading into this database
        elif 'name' in ingredient.keys():    
            ingredientSet.add(ingredient['name'])


# print("found {} distinct ingredients".format(len(ingredientSet)))
# print(ingredientSet)
redundIGs = 0
ingredientCounts = {}
for item in ingredientSet:
    ingredientCounts[item] = 0
    recipeIndex = 0
    for recipe in masterIGs:
       
        recipeIcount = 0
        hasingredient = False
        for ingredient in recipe:
            if item in ingredient.values(): #here's where it's counting twice, since it will have gname and name the same
                hasingredient = True
                recipeIcount +=1
                # ingredientCounts[item] += 1 #move this line to reduce redundant recipe
        if hasingredient:
            ingredientCounts[item] += 1
        if recipeIcount > 1:
            # print("possible redundant ingredient {} in {}".format(item.upper(), masterURLs[recipeIndex]))
            redundIGs += (recipeIcount - 1)
            # print(recipe)
        recipeIndex+=1
# print(ingredientCounts)

total = 0
for key in ingredientCounts:
    total+=ingredientCounts[key]

print("this sorting acounts for {} of the original {} ingredient entries".format(total,totalIs))
print("and we found {} redundant ingredient entries".format(redundIGs))
leftover = totalIs - (total+redundIGs+noName)
print("{} + {} + {} = {}".format(total, redundIGs, noName, noName+total+redundIGs))
if leftover == 0: 
    print("nice sorting!")
else:
    print("you might have double-sorted some ingredients!")


#print(sorted(ingredientCounts, key=ingredientCounts.get, reverse=True))  this returns a list of keys, ordered by their value in reverse
# print("what is this: {}".format(sorted(ingredientCounts, key=ingredientCounts.get, reverse=True)[14]))
for ingredient in sorted(ingredientCounts, key=ingredientCounts.get, reverse=True):
    if ingredientCounts[ingredient] > 1:
        print("{} recipes contain {}".format(ingredientCounts[ingredient], ingredient))  
    else:
        print("{} recipe contains {}".format(ingredientCounts[ingredient], ingredient)) 

# print([len(masterIGs), len(masterTitles), len(masterURLs)])
# print(masterIGs)


# # ingredient_counts = {}
# # for item in ingredientSet:
# #     # print(item)
# #     ingredient_counts[item] = 0


# # #count occurances of each ingredient
# # for item in ingredientSet:
# #     for recipe in masterIGs:
# #         for ingredient in recipe:
# #             if item in ingredient.values():
# #                 ingredient_counts[item] += 1
# #                 # print("plus1")

# # ingredient_list = sorted(list(ingredientSet), key = len)

# # ## here we print the tally of what contains what... 

# # # print(ingredient_counts)
# # #print out the ingredient counts
# # # for key, value in ingredient_counts.items():
# # #     print("{} recipes contain {}".format(value, key))
# # # print(ingredientSet)

# # # for ingredient in ingredient_list:
# # #     print(ingredient)

# # # egg_items = []
# # # for item in ingredient_list:
# # #     if "egg" in item:
# # #         egg_items.append(item)

# # # print("I think all of these ingredients are actually the same (eggs): {}")
# # # for e in egg_items:
# # #     print(e)

# # consolodated_IL = []
# # IG_newcount = 0
# # for toMatch in ingredient_list:
# #     # print("I think all these ingredients are the same as {}:".format(toMatch))
# #     matches = []
# #     toremove = []
    
# #     for item in ingredientSet:
# #         if toMatch in item:
# #             matches.append(item)
# #             toremove.append(item) 
# #         # consolodated_IL.append(matches)       
    
# #     if len(toremove) > 1:
# #         IG_newcount +=1
# #         print(matches)

# #     for item in toremove:
# #         if item in ingredientSet: 
# #             ingredientSet.remove(item)
        

# #     # if len(matches) > 1:        
# #     #     print("here's a set of matches:")
# #     #     print(matches)

# # print("after consolidations, there are {} distinct ingredients".format(IG_newcount))    


# # print(random.choice(masterList))


