import nltk
from nltk.corpus import wordnet as wn 

def isFood(inputword):
    isfood = 0
    thesyns = wn.synsets(inputword.lower())
    for syn in thesyns:
        if isfood > 0:
            break
        theword=wn.synset(syn.name())
        paths = theword.hypernym_paths()
        for route in paths:
            if  route[-1].name().split('.')[0] not in inputword.lower(): #filter out hierarchies that are to not the exact word. 
                continue
            # print(route)
            for item in route:
                if 'food' in item.name():
                    print("{} is probably a food.\n".format(inputword.upper()))
                    return
        
    print("I don't think {} is a food.\n".format(inputword.upper()))


def isthisafood():
    
    ingredient = input("\nEnter a string: \n")
    
    ingredient = nltk.word_tokenize(ingredient)
    
    POS =nltk.pos_tag(ingredient)
    
    print(POS)
    print("\n")

    for word in ingredient:
        isFood(word)

    choice = input("\nIs there something else that might be a food? y/n?\n")
    if choice == 'y':
        isthisafood()
    else:
        return

print("Not sure if it's a food? Maybe I can help!")
isthisafood()