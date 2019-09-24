# Recipe_Analysis
Building a Better Meatloaf... 

![I know how Jeanne Dielman feels...](splash.jpg)

This is a long(ish) term project based on applying data analysis, web scraping, and other computational methods to a strategy I use for cooking in everyday life. When considering making a food (for example, meatloaf) for the first time, I often quickly google recipes, open anywhere between 5 and 10 different recipes in browser tabs, and try to get a broad overview of the food. What ingredients are absolutely essential? Which can be varied or skipped? Which recipes seem "standard" and which are interesting variations. 

I wondered what kind of insight I could glean, or how I might choose recipes differently, if I could expand this strategy and apply it to, say, 1000 recipes? Sure, there might be some good recipes on the first few pages of google, but what if there are some hidden gems on page 100? 

This project attempts to build a large data set of recipes for a single food, then allow a user to navigate it by looking at the ways in which elements in the data set converge or diverge from some kind of 'norm.' The backend is built in Python.  

## Current Status / Code Modules:## 
* **getRecipeLinks.py**  runs from the command line with arguments (foodname, num_results). For example, when you've downloaded the code and are in the correct directory, type "python meatloaf 100" to get generate a textfile with 100 unique links from the google search results for "meatloaf+recipe"* 
* **scrapeLinks.py** 
* **ingParse.py**

## Forthcoming: ##

#Front end! Working on getting this online so that users can query the database I am constructing and visualize some of the results. 
