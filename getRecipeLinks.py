#######################################
# JOE WINTER - Recipe Analysis
#
# This is a script to grab the URLs of recipes via google search
# the arguments it takes are in the form of a string for the food and the number of 
# recipe links we are hoping to store
#
# saves links in a "data" directory (makes it if it doesn't exit) as a text file
#
# for example, in the terminal, try "python3 cheescake 100"
#
# note/recent discovery: google doesn't seem to want to serve all bajillion of the results it claims exist for a given search.
# right now script conks out if you try to get more than about 150 links..... working on this....
#
########################################

from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import requests, bs4, sys, webbrowser, random, datetime, os

def validLinks(theSoup): ##currently filters out '#' links and links to cached content, in favor of
                        ###ORIGINAL URLS
    
    ##list of strings that are 'flags' that we've learned are not useful
    ## for example 'related' searches and video clips
    bad_strings = ["/search?q=related:", "webcache.googleusercontent.com", "related:", "youtube.com"]
    
    
    result_links = theSoup.select('.r a') #grab the search result links
    real_links=[]
    for link in result_links:  ###### Filter out dummy links.... 
        
        if isAlsoLookedLink(link): #don't add the link to the list if it's from the 'people also asked' section of search results
            continue   
        

        thelink = link.get('href')
        if thelink != "#":
            if not hasBadString(thelink, bad_strings): #filter out any links that have undesireable strings... 
                real_links.append(thelink)
    return(real_links)

def hasBadString(theString, badStringList):
    #if any of the 'bad words' are in the given string, return true
    for entry in badStringList:
        if entry in theString:
            return True
    #otherwise return false        
    return False 


#trying to filter out the links in the "people also searched for section"
#because these are the same at the bottom of every search page
#and generally aren't recipes
def isAlsoLookedLink(thelink):
    levelnum = 0
    clevel = thelink
    while clevel.parent: 
        if "class" in clevel.attrs:
            if "kp-blk" in  clevel.attrs["class"]:
                return True
        levelnum += 1
        clevel = clevel.parent
    return False  

def nextSP(the_driver, currentpage): #method to navigate to next page of search results
    next_page_link = driver.find_element_by_link_text(str(currentpage+1))
    next_page_link.click()

def tSString(): #return a timestamp string for unique file naming
                #(useful in development when testing the script a bunch of 
                # times in a row)
    currentDT = datetime.datetime.now()
    datelist = str(currentDT).split(" ")
    time = datelist[1].split(".")
    time2 = time[0].split(":")
    timestring = "-".join(time2)
    filename = datelist[0]+"-"+timestring
    return filename

###########################MAIN EVENT HERE#############

# parse arguments, which should be a food name and a number of results we want to store
if len(sys.argv) > 1:
   
    # Get arguments from command line.
    argstring = ' '.join(sys.argv[1:])
    # print("this is the string of arguments: {}".format(argstring))

    arglist = argstring.split()

    resultCount = None
    for arg in reversed(arglist):
            try:
                # print("{} is a number".format(int(arg)))
                resultCount = int(arg)
                arglist.remove(arg)
            except: 
                continue  
            if resultCount:
                break    

    if resultCount:
        print("we want this many search results: {}".format(resultCount))

    else: 
        resultCount = 100
        print("using default resultCount of {}".format(resultCount)) 

    
    foodstring = " ".join(arglist)
    searchString = "+".join(arglist) +"+recipe&filter=0"
    filename = "_".join(arglist)+"_"+tSString()
    
    #will store links collected in _data directory
    savefile = "data/"+filename


else: 
    print("No arguments entered. Let's find 100 meatloaf recipes. ")
    resultCount = 100
    searchString = "meatloaf+recipe"
    foodstring = "meatloaf"
    filename = "meatloaf_"+tSString()
    savefile = "data/"+filename


print("Locating and and storing {} links that match \"{}\"".format(resultCount, searchString))

searchURL = "http://www.google.com/search?q=" +searchString

linkList = []

### these 3 lines make the webdriver headless (ie, invisible)####
myoptions = Options()
myoptions.headless = True  
myoptions.incognito = True 
driver = webdriver.Chrome(os.path.abspath('/Applications/chromedriver'),   options=myoptions)
##########

####for non-headless driver, comment out the above and uncomment line below.
#driver = webdriver.Chrome()

driver.get(searchURL)
searchpage = 0

####perform the following operations until we've stored the desired number of links
while len(linkList) < resultCount:
    searchpage +=1
    the_html = driver.page_source

    SP = bs4.BeautifulSoup(the_html, features="html.parser")

    new_links = validLinks(SP) #grab the search result links
    print("found {} new links on search page {}".format(len(new_links), searchpage))

    i = 0 
    while (len(linkList) < resultCount) and (i < len(new_links)): 
        print("this is a link i found: {}".format(new_links[i]))
        linkList.append(new_links[i])
        i += 1
    if len(linkList) < resultCount: #load next page of search results
        nextSP(driver, searchpage)


#make sure we have a directory called 'data' otherwise make one
if not os.path.exists("data"):
    os.makedirs("data")

link_file = open(savefile, "w")

##save links in a text file, each link on a new line
link_file.write("\n".join(linkList))

link_file.close
print("went through {} pages of search results to extract {} recipes for {}".format(searchpage, resultCount, foodstring))









