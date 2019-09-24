#! code to load a list of links, attempt to extract ingredient list and store in a text file

from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import requests, bs4, sys, webbrowser, random, datetime, os, re

#########################

def isWPRM(thesoup):
    flag = False
    the_divs = thesoup.find_all('div')
    for div in the_divs:
        if "class" in   div.attrs:
            if "wprm-recipe" in div.attrs['class']: 
                flag = True
    return flag            

def isAllRecipes(searchURL):
    return ("allrecipes.com" in searchURL)

def isFoodNetwork(searchURL):
    return("foodnetwork.com" in searchURL)

def extractWPRecipe(theSoup):

    recipe_ul = theSoup.find_all('li')
    ingredientList = []

    for item in recipe_ul:
        if 'class' in item.attrs:
            if 'wprm-recipe-ingredient' in item.attrs['class']:
                    i_components = item.find_all('span') #this is wordpress specific
                    iList = {}
                    for element in i_components:
                        if 'wprm-recipe-ingredient-amount' in element.attrs['class']:
                            iList["amt"] = element.text.strip()
                        if 'wprm-recipe-ingredient-unit' in element.attrs['class']:
                            iList["unit"] = element.text.strip()    
                        if 'wprm-recipe-ingredient-name' in element.attrs['class']:
                            iList["name"] = element.text.strip() 
                    ingredientList.append(iList)                  
        
    return ingredientList

def scrapeAllRecipes(theSoup):
    recipe_span = theSoup.find_all('span')
    ingredientList = []

    for item in recipe_span:
        if 'itemprop' in item.attrs:
            if item.attrs['itemprop'] == "recipeIngredient":
                print(item.text)
                ingredientList.append(item.text)
    print("\n")
    return ingredientList

def scrapeFoodNetwork(theSoup):
    recipe_p =  theSoup.find_all('p')
    ingredientList = []
    for item in recipe_p:
        if "class" in item.attrs:
            if "o-Ingredients__a-Ingredient" in item.attrs["class"]: 
                print(item.text)
                ingredientList.append(item.text)
    print("\n")
    return ingredientList

def getTitle(theSoup):
    title =theSoup.find("title")
    if title:
        title = title.text.strip('\n\t')
        title = title.strip()
        return title
    else: 
        return Null

def extractUL(theSoup):
    pat = re.compile(r'\s+') #set up a pattern to recognize excess spaces in a string
    lists_as_text = []
    set_of_lists = theSoup.find_all("ul")
    for each_list in set_of_lists:
        the_list = []
        list_entries = each_list.find_all("li")
        for entry in list_entries:
            text_string = entry.text.strip('\n\t') #strip out tabs and newline characters 
            text_string2 = text_string.strip() #strip out leading and ending whitespace
            formatted_string = pat.sub(' ', text_string2) #replace any space that is more than one space with one space
            the_list.append(formatted_string)
        lists_as_text.append(the_list)
    return lists_as_text        

def filter_lists_by_length(lists_to_filter, lowThreshhold, highThreshhold): #define any rules you want to use to reject a list 
                                                                            #and not consider
    filtered_elements = []
    for item in range(len(lists_to_filter)):
        if len(lists_to_filter[item]) <= lowThreshhold or len(lists_to_filter[item]) >= highThreshhold: 
            filtered_elements.append(item)
    
    #to pop all the indices you want, order them in reverse, then pop in reversed order! 
    #no reindexing required! 
    filtered_elements.sort(reverse=True)
    for index in filtered_elements:
        lists_to_filter.pop(index)


#######################  
def numCount(thestring): #function to return the number of integer characters in a string
    hasNums = False
    numCount = 0
    for char in range(len(thestring)):
        try: 
            int(thestring[char])
            numCount += 1
            hasNums = True
        except: 
            continue
    return numCount 

def listNumStats(the_list): #take a list, return list of counts of numbers in each entry
    list_stats = []
    for item in the_list:
        list_stats.append(numCount(item))
    return list_stats

def listNumWeight(list_stats): #take the list stats returned from above and output percentage of items
                                # in list that contain numbers
    numerator = 0
    frac = 0
    for item in list_stats:
        if item > 0:
            numerator += 1
    if len(list_stats) != 0:        
        frac = numerator/len(list_stats)
        # print("{} of {} list entries have numbers in them".format(numerator, len(list_stats)))
    return frac

def maxIndex(the_list): # take a list of weights and return index of highest weight
    sorted_list = the_list.copy()
    sorted_list.sort()
    # print(sorted_list)
    return the_list.index(sorted_list[-1])

def highestNumWeight(list_of_lists):
    list_weights = []
    for each_list in list_of_lists:
        stats = listNumStats(each_list)
        weight=listNumWeight(stats)
        list_weights.append(weight)
        return maxIndex(list_weights)  

def measureWeight(listOfStrings): ##input a collection of lists.  
                                    ##give a weight to each list based on 
                                    ##percentage of entries in the list containing a measure word
    num_of_elements = len(listOfStrings)
    measure_string = "whole, half, cup, teaspoon, tablespoon, dash, lbs, pound, grams, ounce, oz, package, to taste".split(", ") 
    measured_elements = 0
    for entry in listOfStrings:
        for measure in measure_string: #see if entry contains at least one of the measure words. 
            if measure in entry:
                measured_elements +=1 
                break
    #returns percentages of elements in the lsit that have any of the measure words in them.
    return (measured_elements/num_of_elements)
          



#######################

def tSString(): #return a timestamp string for file naming
    currentDT = datetime.datetime.now()
    datelist = str(currentDT).split(" ")
    time = datelist[1].split(".")
    time2 = time[0].split(":")
    timestring = "-".join(time2)
    filename = datelist[0]+"-"+timestring
    return filename

#######################



#TESTCASES
#"http://www.myrecipes.com/recipe/avocado-shrimp-cocktail" #mistook caloric info because of numbers! 
#"https://www.tasteofhome.com/recipes/shrimp-cocktail/"#not in ordered list! 
if len(sys.argv) < 2:
    print("no file name entered")
    print("goodbye")
    exit()

else:
    filepath = sys.argv[1]


###load the link file and place links in a list

link_file = open(filepath, "r")
link_string = link_file.read()
link_file.close()
link_list = link_string.split('\n')



myoptions = Options()
myoptions.headless = True 
myoptions.incognito = True  



result_list = []

the_file_name = "_data/results_"+tSString() 
result_file = open(the_file_name, "w")  
print("attempting to scrape from {} different sites".format(len(link_list)))

for link in link_list:

    result_entry = []
    
    # result_entry.append(len(result_list))

    searchURL = link
    result_entry.append(searchURL)

    print("NOW SCRAPING {}\n".format(searchURL))
    
    driver = webdriver.Chrome(os.path.abspath('/Applications/chromedriver'),   options=myoptions)
    
    try:
        driver.get(searchURL)


    except: 
        result_entry.append("ERROR WILL ROBINSON")
        result_list.append(result_entry)
        for result_element in result_entry:
            result_file.write(str(result_element)+"\n")
            result_file.write("\n")
        continue
    the_html = driver.page_source
    driver.quit()
    

    SP = bs4.BeautifulSoup(the_html, features="html.parser")

    the_recipe = []

    title = getTitle(SP)
    if title:
        result_entry.append(title)

    if isWPRM(SP):
        print("this looks like a wordpress recipe; I'm going to try to extract it\n") 
        the_recipe = extractWPRecipe(SP)
        print("got the recipe")
        print(the_recipe)
        print("\n")
        result_entry.append(the_recipe)
    
    elif isAllRecipes(searchURL):
        print("this recipe is from allrecipes.com\n")
        the_recipe = scrapeAllRecipes(SP)
        print(the_recipe)
        print("\n")
        result_entry.append(the_recipe)

    elif isFoodNetwork(searchURL):
        print("this recipe is from foodnetwork.com\n")
        the_recipe = scrapeFoodNetwork(SP)
        print(the_recipe)
        print("\n")
        result_entry.append(the_recipe)

    else: ##parse generic HTML PAGES HERE... ie, not any particular template/site with known tags. 
        page_lists = []
        print("I don't think this is a known recipe format.")
        print("I'll try extracting unordered lists instead\n")
        page_lists = extractUL(SP)
        # print(page_lists)
        print("this recipe page contains {} unordered lists\n".format(len(page_lists)))
        filter_lists_by_length(page_lists, 4, 20) #method to remove really short or really long lists! 
        print("after filtering we will consider these {} unordered lists:\n".format(len(page_lists)))
        print("{}\n".format(page_lists))

        page_list_num_weights = []
        page_list_measure_weights = []
        page_list_weights = []
        

        ##########WEIGHTING IS HAPPENING HERE!!!!!!#######################

        for each_list in page_lists:
            page_list_num_weights.append(listNumWeight(listNumStats(each_list)))
            page_list_measure_weights.append(measureWeight(each_list))

            page_list_weights.append(page_list_num_weights[-1]+page_list_measure_weights[-1]*2)
        print("number weights: {}\n".format(page_list_num_weights))
        print("measurement weights: {}\n".format(page_list_measure_weights)) 
        print("weight vector: {}\n".format(page_list_weights))
        if len(page_list_num_weights) > 0:
            guess = maxIndex(page_list_weights)
            # if page_list_num_weights[guess-1]:
            #     if page_list_num_weights[guess] == page_list_num_weights[guess]:
            #         print: "we have a tie! for numWeights, let's break it with measurement weights"
                
            print("I'm guessing the index of the ingredient list is {}\n".format(guess))
            print(page_lists[guess])
            print("\n")
            #but what if it's not in a list. 

            result_entry.append(page_lists[guess])
        else:
            print("looks like all the lists are empty")
            result_entry.append("ALL LISTS EMPTY")    
    
    
    
    result_list.append(result_entry)
    
    # for result_element in result_entry:
    #     result_file.write(str(result_element)+"\n")
    # result_file.write("\n")

    for i in range(len(result_entry)):
        if i < (len(result_entry) - 1):
            result_file.write(str(result_entry[i])+"\n")
        else:
            result_file.write(str(result_entry[i]))
    result_file.write("\n")

driver.quit()

result_file.close()
    






