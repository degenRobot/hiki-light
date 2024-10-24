import json

def cleanDbChars():

    ### open charactersDb.json
    with open('charactersDb.json') as f:

        data = json.load(f)

    newDict = {}

    for char in data : 
        newKey = char['name_long']
        newDict[newKey] = char

    with open('newCharacters.json', 'w') as f:
        json.dump(newDict, f, indent=4)

cleanDbChars()