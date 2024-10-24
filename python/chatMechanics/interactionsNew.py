
# NOTE : making example of how this could work
# Example use -> start of interaction determine which interaction types are available -> 
# Feeds into conversation (retrives info + determines prompt type)

interactionData = {
    "Chat" : {
        "Scenario Input" : "", 
        "requiredTrust" : 0,
        "requiredAttraction" : 0,
        "requiredInterest" : 0,
        "requiredAgreeableness" : 0,
        "retriveAddedContext" : False,
        "retrivalType" : "",
        "promptInclusions" : {
            "includeLikes" : False,
            "includeExamples" : False,
            "includeScenario" : False,
            "includeAdditionalContext" : False
        }
    },
    "NSFW" : {
        "Scenario Input" : """You are roleplaying a sexual interaction between {char} and {name} be vivid and descriptive of the physical actions and dialogue of {char}""",
        "requiredTrust" : 7,
        "requiredAttraction" : 7,
        "requiredInterest" : 7,
        "requiredAgreeableness" : 7,
        "retriveAddedContext" : False,
        "retrivalType" : "",
        "promptInclusions" : {
            "includeLikes" : False,
            "includeExamples" : False,
            "includeScenario" : True,
            "includeAdditionalContext" : False
        }
    }



}

def getAvailableInteractions( moodScores, location ) : 

    interactions = interactionData.keys() 
    availableInteractions = []

    for int in interactions : 
        interaction = interactionData[int]
        attraction = moodScores["attraction"] >= interaction['requiredAttraction']
        trust = moodScores["trust"] >= interaction['requiredTrust']
        interest = moodScores["interest"] >= interaction['requiredInterest']
        agreeableness = moodScores["agreeableness"] >= interaction['requiredAgreeableness']

        availableInLocation = True

        if (attraction & trust & interest & agreeableness & availableInLocation) :
            #print("Interaction " + int + " is available")
            availableInteractions.append(int)

    
    return availableInteractions