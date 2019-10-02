############################################
# JOE WINTER - Recipe Analysis
#
# Helper functions for parsing ingredient data. 
# (try to) separate an arbitrary 'ingredient string' into 'amount', 'unit', and 'name'
#
############################################

import re

#dictionary to convert unicode fractionc characters to normal strings with ints and a slash
fracTable = {'¼':' 1/4', '½': ' 1/2', '¾': ' 3/4', '⅛': ' 1/8', '⅓': ' 1/3', '⅔':' 2/3', '⅜':' 3/8'}

##### NOTE2SELF: TO TO GET MORE FRACTIONS:
# (in case we need to add more unicode fractions)
# 
# import unicodedata
# unicodedata.lookup(vf + "THREE EIGHTHS")
#
############################################

####We use this if there are unicode fraction characters in a string 
def convertSFractions(ingredientString):
    for item in fracTable.keys():
        if item in ingredientString:
            # print("{} became:".format(ingredientString))
            ingredientString = ' ' + ingredientString.replace(item, fracTable[item])
            # print(ingredientString)
    return ingredientString

###special code for wordpress recipes already parsed as Dicts: they use a lot of unicode fraction characters
def convertWPSFractions(wp_list):
    for ingDict in wp_list:
        for item in fracTable.keys():
            if 'amt' in ingDict.keys():
                if item in ingDict['amt']:
                # print("{} became:".format(ingredientString))
                    ingDict['amt'] = fracTable[item]
                # print(ingredientString)
    return wp_list

# slightly awkward function to try to parse the difference in the usage of the '-' character 
# in various contexts, ie, 8-10 eggs vs 1-1/2 cups... 
# right now guess its a range of quantities (and store the average of the endpoints of the rage)
# if there's a '-' but no '/' character in the string
def isRange(thestring):
    if '/' in thestring:
        return False
    elif '-' or '–' in thestring:
        newstring = thestring.replace('-', ' ')
        newstring = newstring.replace('–', ' ')
        numlist = newstring.split()
        

        avg = 0
        for item in numlist:
            try: 
                avg = avg + int(item)
            except:
                continue
        if len(numlist) > 1:
           
            return avg/len(numlist)

#method to extract the (numeric) quantiity in an ingredient string
def extractQuantity(thestring):
    #make sure we don't have extra whitespace:
    thestring = convertSFractions(thestring)
    sstring=thestring.strip()
    # print(sstring)

    #generate a string of same length that only contains numeric characters and the front slash
    newstring = ''.join((ch if ch in '-–0123456789/' else ' ') for ch in sstring)
    # print(newstring)

    #replace spaces more than 2 with a not-likely-to-occur-randomly string
    pat = re.compile('[ ]{2,}')
    formatted_string = pat.sub('--splithere--', newstring)

   
    #split into the component parts
    
    numlist = formatted_string.split('--splithere--')
    # print(numlist)

    quantity = None    
    
    #make sure there were actually numbers in the string

    #right now we assume the quanity is the first numerical element in the string, 
    #but we get a list of all numbers here, and can revisit when we want to parse better. 

    if len(numlist[0]) > 0 :
       
        Q_stripped_string = thestring.replace(numlist[0], '')
        first_num = numlist[0]
        #replace empty space character with plus operator
        # so something like '1 1/2' becomes 1+1/2 
        rangeavg = isRange(numlist[0])
        if rangeavg:
            quantity = rangeavg
        
        else: 
            to_eval = first_num.replace(' ', '+')
            to_eval = to_eval.replace('–', '+')
            to_eval = to_eval.replace('-', '+')

            # print(to_eval)

            try: 
                quantity = eval(to_eval)
            except:
                pass
        
    if quantity: 
        return [quantity, Q_stripped_string.strip()]
    
    else:
        return [False, thestring]

#method to extract the measure unit of an ingredient
def parseMeasure(ingredientString):
    IS = ingredientString
    measure_list = "whole, half, cup(s), cups, cup, can, cans, can(s), slice, slices, teaspoons, teaspoon, quart, quarts, tsps, tsps., tsp., tsp, tablespoons, tablespoon, tbs., tbs, tbsp., tbsp, dash, qts., qt., lbs., lbs, lb., lb, pound, pounds, grams, ounces, ounce, oz., oz, package, packages, packet, packets, to taste".split(", ")
    ML = sorted(measure_list, key=len, reverse=True)
    for measure in ML:
      
        ##potential PROBLEM, what if measurewords are embedded in ingredient words. example: "pint" \in "pinto beans"
        ##could solve this by...
        mstring = measure+" " #add a space to make sure it's not embedded in something. 
        if mstring in ingredientString: #this returns the first measure the method detects
            # print(IS)
            strippedIS = IS.replace(mstring, '')
            # print(strippedIS)
            return([measure, strippedIS])

    
    return ["NONE", IS]

### Parse Ingredient List by chunking it into amount, unit, and ingredient name and outputting each
## ingredient as a python dictionary with those keys
def PIList(theList):
    ingredientList = []
    for item in theList:

        Quantity_Parsed = extractQuantity(item)
        Unit_Ing_Parsed = parseMeasure(Quantity_Parsed[1])

        if Quantity_Parsed[0]:
            quantity = Quantity_Parsed[0]
        else:
            quantity = "NONE"
        
        unit = Unit_Ing_Parsed[0]
        name = Unit_Ing_Parsed[1]

        ingDict = {'amt': quantity, 'unit': unit , 'name': name.lower()}
        ingredientList.append(ingDict)


    return ingredientList

