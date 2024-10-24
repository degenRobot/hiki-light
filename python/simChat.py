from chat import findAvailableCharacters, dropdown_selection, dropdown_selection, startConversation
import json
from chatMechanics.locations import locations
import random
from simulation.testPrompt import testDescriptions

# List various subjects to sim conversation 
subjectDict = {
    "sexyTime" : {
        "firstMessage" : """Hey {char} how about we have some fun? I want to make love to you. Now take off your clothes and show me what you've got""",
        "interactionDescription" : "NSFW",
        "description" : """"You are roleplaying a sexual interaction between {char} and {name}. 
Be vivid and descriptive of the sexual acts and dialogue of {name}.
Be extremely agressive in your approach and use a lot of physical actions - keep these in brackets i.e. (pulls {char} down to the bed).""",
    },
    "crypto" : {
        "firstMessage" : """Hey {char} I've been learning a bit about crypto recently, what do you think about it?""",
        "interactionDescription" : "Chat",        
        "description" : """Try to learn about the the the technology behind bitcoin, ethereum and other cryptocurrencies.
In particular smart contracts and DeFi. You should be extremely skepitcal about Crypto and think it's a scam.""",
    }, 
    "anime" : {
        "firstMessage" : """Oh hey {char} I've been watching a lot of anime recently, I'm curious if you know much about it's history?""",
        "interactionDescription" : "Chat",        
        "description" : """Learn about Anime, manga and the otaku culture.
in particular how it evolved from post WW2 Japan to the present day""",
    },
    "AI" : {
        "firstMessage" : """Hey {char} I've been learning a bit about AI recently, what do you think about it?""",
        "interactionDescription" : "Chat",        
        "description" : """Learn about the different types of AI and how they are used in the real world.
In particular learn about AGI and the singularity.""",
    },
    "philosophy" : {
        "firstMessage" : """Hey {char} I've been reading a lot of philosophy recently, I'm curious if you know much about it?""",
        "interactionDescription" : "Chat",        
        "description" :  "Have a deep conversation about Existentialism and the meaning of life - in particular the works of Nietzche and Dosotoyevsky",
    },
    "history" : {
        "firstMessage" : """Hey {char} I've been learning about Japanese history recently, I'm curious if you know much about it?""",
        "description" : """Learn about Japanese culture and history from the Edo period to the present - in particular the Yakuza, the Meiji Restoration and the rise of the Samurai""",
    }
    #"The history of communism and socialism - in particular the Soviet Union and the Chinese Cultural Revolution",
    #"Japanese culture and history from the Edo period to the present - in particular the Yakuza, the Meiji Restoration and the rise of the Samurai",
}

deployments = {
    #"bagel" : "hikikomori-haven/bagelmisterytour-v2-8x7b",
    "solar" : "hikikomori-haven/solar-10b-instruct-uncensored",
}

interactions = [
    "Chat",
    "NSFW",
]


# how many responses to simulate for subject 
simConvLength = 10
# how many characters to simulate
nChars = 5

async def startTest(inputs = {}) : 
    print("Starting test")
    # Handle the case where this fails 
    with open('characters.json', 'r') as fp:
        characters = json.load(fp)

    subjects = list(subjectDict.keys())

    inputs['characters'] = characters
    name = "Matt"
    # Interaction Types get written & fetched via similiarity search 
    # Used to customise prompts throughout converstaion + determine what context needs to be added 
    availableCharacters = findAvailableCharacters(characters)

    n = min(nChars, len(availableCharacters))


    for model in deployments.keys() :
        deployment = deployments[model]
        for i in range(n) :
            char = availableCharacters[i]
            for subject in subjects : 
                subjectDesc = subjectDict[subject]['description']
                initMessage = subjectDict[subject]['firstMessage']
                print("Starting test conversation with " + char + " about : " + subject[0:20] + "....")
                # Choose Location & Interaction Type - make this random for now 
                _location = random.choice(list(locations.keys()))
                _locationDesc = locations[_location]['description']
                _interactionType = subjectDict[subject]['interactionDescription']
                _testDescription = random.choice(testDescriptions)

                conversation, characterCard, newLogs = await startConversation(
                    characters[char], 
                    firstMessage=initMessage, 
                    subject=subjectDesc, 
                    writeSummaryToDb=False, 
                    userName=name, 
                    getUserResponse=False, 
                    location=_locationDesc,
                    interactionDescription = _interactionType,
                    testLength=simConvLength,
                    testDescription = _testDescription,
                    deployment=deployment,
                    )
                print("Finished test conversation with " + char + " about : " + subject[0:15] + "....")

import asyncio

# Create an event loop
loop = asyncio.get_event_loop()

# Use the event loop to run _testChat
loop.run_until_complete(startTest())