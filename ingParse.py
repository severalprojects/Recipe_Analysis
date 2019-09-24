#method to take a string and try to parse it as an ingredient entry [quantity, measuement, ingredient]

import re

testlist = ['2/3 teaspoon sugar', '1/4 cup shortening', '1 large egg, room temperature', '1 teaspoon vanilla extract', '1/4 teaspoon salt', '1-1/2 cups all-purpose flour', '2 teaspoons baking powder', '1/2 cup whole milk', '1 cup heavy whipping cream, whipped', '1-1/2 quarts fresh or frozen strawberries, sliced']
testlist2 = ['2/3 cup sugar', '1/4 cup shortening', '1/4 teaspoon salt', '1-1/2 cups all-purpose flour', '1/2 cup whole milk', '1-1/2 quarts fresh or frozen strawberries, sliced', '2 large things']
testlist3 = ['1-1/2 pounds Ground Beef (93% lean or leaner)', '3/4 cup Panko bread crumbs', '3/4 cup ketchup, divided', '1/2 cup minced onion', '1 egg', '1 tablespoon Worcestershire sauce', '2 teaspoons minced garlic', '1 teaspoon dried thyme leaves', '3/4 teaspoon pepper', '1/2 teaspoon salt']
testlist4 = ['2 lbs. lean ground beef', '1 cup Italian breadcrumbs', '2 eggs', '1/2 cup onion, diced', '2 tsp garlic powder', '2 tsp chopped parsley', '1 tsp salt', '1 tsp pepper', '1/2 cup bbq sauce']
testlist5 =  ['1/2 teaspoon salt', '1 cup unsalted butter', '1 cup crunchy peanut butter', '1 cup white sugar', '1 cup packed brown sugar', '2 eggs', '2 1/2 cups all-purpose flour', '1 teaspoon baking powder', '1 1/2 teaspoons baking soda']
testlist6 = ['1 tablespoon good olive oil', '3 cups chopped yellow onions (3 onions)', '1 teaspoon chopped fresh thyme leaves', '2 teaspoons kosher salt', '1 teaspoon freshly ground black pepper', '3 tablespoons Worcestershire sauce', '1/3 cup canned chicken stock or broth', '1 tablespoon tomato paste', '2 1/2 pounds ground chuck (81 percent lean)', '1/2 cup plain dry bread crumbs (recommended: Progresso)', '2 extra-large eggs, beaten', '1/2 cup ketchup (recommended: Heinz)']

fracTable = {'¼':'1/4', '½': '1/2', '¾': '3/4', '⅛': '1/8', '⅓': '1/3', '⅔':'2/3', '⅜':'3/8', '½':'1/2' }


#####TO GET MORE FRACTIONS:
# 
# import unicodedata
# unicodedata.lookup(vf + "THREE EIGHTHS")
#
############################################


def intIndices(theString): #returns the indices of positions in a string that hold integers
    the_indices = []
    index = 0
    while index < len(theString):
        intInList = index
        try:
            int(theString[index])
            the_indices.append(intInList)
            index += 1
        except:
            index +=1

    
    element = 0
    rangeList = []
    
    while element < len(the_indices):
        seqList = [element, element]
        # print(seqList)
        if element < len(the_indices):
            if (element+1) < len(the_indices):
                while the_indices[element+1] == the_indices[element] + 1:
                    # print("{} equals {}".format(the_indices[element+1], the_indices[element] + 1))
                    seqList[1] = element+1
                    element +=1 
                    if element+1 >= len(the_indices):
                        break
                rangeList.append(seqList)
                # print("innerLoop")
                # print(seqList)
            else: 
                rangeList.append(seqList)
        element+=1       

    numRanges = []
    for item in rangeList:
        # print("testing {}:{}".format(item[0], item[1]))
        newRange = [the_indices[item[0]], the_indices[item[1]]+1]    
        numRanges.append(newRange)      
    # for item in the_indices:
        # print("this is in the_indices:{}".format(item))   
    return [the_indices, rangeList, numRanges]


def getFractions(indices_list, theString):
    fracList = []
    ND_List = []
    if len(indices_list) > 1: #make sure there's more than one integer in the string
        for index in range(len(indices_list)-1):
            if (indices_list[index][1] == (indices_list[index+1][0] - 1)) : #check if the last entry in the first integer is one place
                                                                        #away from first entry in next integer
                if theString[indices_list[index][1]] == "/":
                    # print("detected a fraction: {}".format(theString[indices_list[index][0]: indices_list[index+1][1]]))
                    fracList.append([indices_list[index][0], indices_list[index+1][1]])
                    ND_List.append([indices_list[index], indices_list[index+1]]) #store fractions as pairs of lists of ranges
    #return fracList   
    return ND_List             

          
def getMixedFractions(int_indices, frac_indices, theString):
    
    if not frac_indices: # if we pass the function an empty list of fractions, do nothing. 
        return int_indices
    MF = [] #list to store mixed fractions (or just restore non-mixed fractions if they aren't)
    MF_count = 0
    
    for interval in frac_indices:
        MF.append(interval)
        for element in int_indices:
            if interval[0][0] == element[1] + 1:
                #print("found a mixed fraction: {}".format(theString[element[0]:interval[1][1]]))
                MF[MF_count].insert(0, element)
        MF_count+=1
    return MF

def stripMixedFractions(MF_list, theString):
    stringList = list(theString)
    #print(stringList)
    stripList = MF_list
    #print(stripList)
    stripList.reverse()
    # print("the striplist: {}".format(stripList))
    

    #######block of code deletes ALL the numbers from the string########## yields some problems if there are multiple numbers in string
    # for item in stripList:
    #     #print("thestriplist: {}".format(stripList))
    #     #print("the item: {}".format(item))
    #     if len(stripList) == 1:
    #         # print("item type: {}".format(type(item[0])))
    #         try:
                
    #             del stringList[item[0]:item[-1]] 
    #             #print("its an int")
    #         except: 
    #             del stringList[item[0][0]:item[-1][1]]
    #     else: 
    #         # print("try to delete stringList[{}:{}]".format(item[0][0],item[-1][1]))
    #         try: 
    #             del stringList[item[0][0]:item[-1][1]]
    #         except: 
    #             del stringList[item[0]:item[-1]]
    ###########################################

    ###this block of code assumes that the quantity is the first number that appears in the ingredient string. 
    if stripList:
        quantity = stripList[-1]
        try:
            del stringList[quantity[0][0]:quantity[-1][1]]
                    #print("its an int")
        except: 
            del stringList[quantity[0]:quantity[-1]]
        
    
    return ''.join(stringList)

def pullFractions(theString):

    fIndices = intIndices(theString)
    #print(fIndices[2])
    fractions = getFractions(fIndices[2], theString)
    #print(fractions)
   
    if fIndices[2]:
        mixedFractions = getMixedFractions(fIndices[2], fractions, theString) 
    else:
        # print("in the else")
        mixedFractions = getMixedFractions(fIndices[1], fractions, theString) 

    strippedString = stripMixedFractions(mixedFractions.copy(), theString.strip())
    
    #strip excess space created by deletion. 
    pat = re.compile(r'\s+')
    formatted_string = pat.sub(' ', strippedString)
    
    return([mixedFractions, formatted_string])


####gotta convert wordpress dictionaries too! 
def convertSFractions(ingredientString):
    for item in fracTable.keys():
        if item in ingredientString:
            # print("{} became:".format(ingredientString))
            ingredientString = ingredientString.replace(item, fracTable[item])
            # print(ingredientString)
    return ingredientString

def convertWPSFractions(wp_list):
    for ingDict in wp_list:
        for item in fracTable.keys():
            if 'amt' in ingDict.keys():
                if item in ingDict['amt']:
                # print("{} became:".format(ingredientString))
                    ingDict['amt'] = fracTable[item]
                # print(ingredientString)
    return wp_list

def parseQuantity(ingredientString):
    ingredientString = convertSFractions(ingredientString)
    input = pullFractions(ingredientString) #function will return a list, separating numbers, then the string with numbers removed
    
    MF = input[0].copy()
    parsedNums = []
    for frac in MF:
        entries = frac.copy()
        
        entries.reverse()
        
        #print("entries: {}".format(entries))
        whole = 0
        part = 0
        if len(entries) == 3:
            # print("thre entriess!")
            whole += int(ingredientString[entries[2][0]:entries[2][1]])
            #print(whole)
            part = int(ingredientString[entries[1][0]:entries[1][1]])/int(ingredientString[entries[0][0]:entries[0][1]])
        elif len(entries) == 2: 
            try:
                part = int(ingredientString[entries[1][0]:entries[1][1]])/int(ingredientString[entries[0][0]:entries[0][1]])
            except:
                whole = int(ingredientString[entries[1]]) 
        elif (entries[0] - entries[1]) == 1:
            #print("entries[0]: {}".format(entries[0]))
            whole = int(ingredientString[entries[1]])    

        parsedNums.append(whole+part)
    if parsedNums:
        output = [parsedNums[0], input[1]]
    else:
        output = ["", input[1]]

    # if len(parsedNums) == 1:
    #     output = [parsedNums[0], input[1]] 
    # else: 
    #     output = [parsedNums, input[1]]   
    return output

# print(parseQuantity("testing 1 1/2 cups flour"))
#print(parseQuantity("2 or 3 eggs"))

def parseMeasure(ingredientString):
    IS = ingredientString
    measure_list = "whole, half, cup(s), cups, cup, can, cans, can(s), slice, slices, teaspoons, teaspoon, quart, quarts, tsps, tsps., tsp., tsp, tablespoons, tablespoon, tbs., tbs, tbsp., tbsp, dash, qts., qt., lbs., lbs, lb., lb, pound, pounds, grams, ounces, ounce, oz., oz, package, to taste".split(", ")
    ML = sorted(measure_list, key=len, reverse=True)
    for measure in ML:
      
        ##potential PROBLEM, what if measurewords are embedded in ingredient words. example: "pint" \in "pinto beans"
        ##could solve this by getting the indxe 
        mstring = measure+" " #add a space to make sure it's not embedded in something. 
        if mstring in ingredientString: #this returns the first measure the method detects
            # print(IS)
            strippedIS = IS.replace(mstring, '')
            # print(strippedIS)
            return([measure, strippedIS])

    
    return ["NONE", IS]

def PIList(theList):
    ingredientList = []
    for item in theList:
        parsedAMT = parseQuantity(item)
        parsedUandI = parseMeasure(parsedAMT[1].strip()) #.strip()
        # print("amt: {} | unit: {} | ingredient: {}".format(parsedAMT[0], parsedUandI[0], parsedUandI[1]))
        ingDict = {'amt': parsedAMT[0], 'unit': parsedUandI[0] , 'name': parsedUandI[1].lower()}
        ingredientList.append(ingDict)
    return ingredientList



#
# ingredientList = []

# for item in testlist6:
#     print(item)
#     parsedAMT = parseQuantity(item)
#     parsedUandI = parseMeasure(parsedAMT[1].strip()) #.strip()
#     # print("amt: {} | unit: {} | ingredient: {}".format(parsedAMT[0], parsedUandI[0], parsedUandI[1]))
#     ingDict = {'amt': parsedAMT[0], 'unit': parsedUandI[0] , 'name': parsedUandI[1]}
#     ingredientList.append(ingDict)

# print(ingredientList)


# print(parseMeasure("cup applesauce"))