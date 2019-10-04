import nltk
from nltk.corpus import wordnet as wn 


def traceword():
    inputword= input("Enter the word you want to examine: \n")

    thesyns = wn.synsets(inputword)
    for syn in thesyns:
        theword=wn.synset(syn.name())
        paths = theword.hypernym_paths()
        for route in paths:
            #filter routes that don't go to the exact path. 
            # if  route[-1].name().split('.')[0] not in inputword: 
            #     continue
            linkage=""
            for item in route:
                linkage += item.name().split('.')[0] + " --> "
            print(linkage[:-4])
            # for item in reversed(route):
            #     if 'unit_of_measurement' in item.name():
            #         print("I think {} is a measure".format(inputword))                        
            #         return True
    moreinput = input("enter another word? y/n \n")
    if moreinput == "y":
        traceword()
    else:
        return

traceword()