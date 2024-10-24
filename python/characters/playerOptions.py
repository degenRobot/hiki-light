import random

# traits
"""
TO DO - have list of traits 

Appearance 
- Body (fat / normal / skinny / muscular)
- Face ( cute / ugly / pretty / handsome / average )
- Hair (long / short / bald / dyed / natural)
- Clothing (casual / formal ) 

Other
- Charisma (high / low)
- Intelligence (high / low)
- Wealth (rich / poor)
- Health (healthy / sick)
- Reputation 
"""

# TO DO -> for character card -> add in prefered traits + logic for how this impacts mood

playerTraits = {
    "appearance": {
        "body": "normal",
        "face": "average",
        "hair": "natural",
        "clothing": "casual",
    },
    "other": {
        "charisma": "high",  # Can make certain actions easier -> i.e. higher chance NPC is agreeable /
        "intelligence": "high",  # Could this impact certain mechanics
        "wealth": "poor",  # Is this necessary (could build over time) ?
        "health": "healthy",  # Could deteriorate over time if certain things aren't done ?
        "reputation": "good",  # Can this evolve over time based on player actions
    },
}

# Based on traits -> feed into chat prompt (different NPC's react differently based on traits)

# NOTE - scores should be stored in DB -> if not stored then generate (pseudo random)
# Have some functions to adjust score post interaction + based on traits + character card
def getMoodScores(characterCard, player = "") : 

    # TO DO - get scores from DB based on character card + player
    attraction = 0
    agreeableness = 0
    interest = 0
    trust = 0

    scores = {
        "attraction" : attraction,
        "agreeableness" : agreeableness,
        "interest" : interest,
        "trust" : trust
    }

    return scores



def getAttraction(traits, characterCard, randomScore=False, defaultScore=10):
    # Score this on scale of 1 - 10
    attractionScore = defaultScore
    if randomScore:
        attractionScore = 10 * random.random()
    # Can make this fully random for testing + add some randomness based on traits so not deterministic
    # I.e. certain characters prefer certain traits -> can just add to random score or multiply by a certain factor

    # TO DO - Make adjustments based on character card + traits

    if attractionScore < 5:
        attractionStr = "Not at all sexually attracted to {name} - will decline any sexual advances made by {name}. If this happens they will likely tell them they'll need to a lot to change their mind."
    elif attractionScore < 7:
        attractionStr = "Is indifferent in terms of attraction to {name} - is neither repulsed nor attracted will most decline any sexual advances beyond anything such as hugging. If this happens will ask for gifts from {name} to prove their affection."
    else:
        attractionStr = "is very sexually attracted to {name} - extremely attracted based on their appearance."

    return attractionStr


def getAgreeableness(traits, characterCard, randomScore=False, defaultScore=10):
    # Score this on scale of 1 - 10

    # Can make this fully random for testing + add some randomness based on traits so not deterministic
    agreeablenessScore = defaultScore
    if randomScore:
        agreeablenessScore = 10 * random.random()
    # TO DO - Make adjustments based on character card + traits

    if agreeablenessScore < 5:
        agreeablenessStr = "Is extremely disagreeable - will be confrontational with {name} and argue with them. Will not agree with anything {name} tries to do."
    elif agreeablenessScore < 7:
        agreeablenessStr = (
            "Is indifferent in terms of agreeableness - will behave normally."
        )
    else:
        agreeablenessStr = "Is extremely agreeable - will agree with pretty much everything {name} says or convinces {char} to do."

    return agreeablenessStr


def getInterest(traits, characterCard, randomScore=False, defaultScore=10):
    ### TO DO - takes in traits and character card to feed in INTEREST in chat prompt (this drives conversation)

    # Can make this fully random for testing + add some randomness based on traits so not deterministic
    interest = defaultScore
    if randomScore:
        interest = 10 * random.random()
    if interest < 5:
        interestStr = "Is extremely uninterested in {name} and what they have to say. - will be extremely disengaged in the conversation."
    elif interest < 7:
        interestStr = "Is indifferent in terms of interest in {name} being neither engaged or disengaged."
    else:
        interestStr = "Is extremely interested in {name} and what they have to say - will be highly engaged in the conversation. "

    return interestStr


def getTrust(characterCard, traits=playerTraits, randomScore=False, defaultScore=10):
    # Can make this fully random for testing + add some randomness based on traits so not deterministic
    trust = defaultScore
    if randomScore:
        trust = 10 * random.random()
    # TO DO - Make adjustments based on character card + traits

    if trust < 5:
        trustStr = "Does not trust {name} at all - will be extremely suspicious of their motives."
    elif trust < 7:
        trustStr = "Is indifferent in terms of trust in {name} being neither trusting or suspicious."
    else:
        trustStr = "Is extremely trusting of {name} - will be very open and honest in the communication."

    return trustStr

# NOTE : maybe only parts of the mood are injected based on interaction ??? 
# Note : Based on traits -> can also unlock certain "interaction types" (used interactionType Dict to drive conversation)
def getMood(characterCard, chatInputs, traits=playerTraits, score=0):
    ### TO DO - takes in traits and character card to feed in MOOD / REACTION in chat prompt (this drives conversation)

    attraction = getAttraction(traits, characterCard, defaultScore=score)
    agreeability = getAgreeableness(traits, characterCard, defaultScore=score)
    interest = getInterest(traits, characterCard, defaultScore=score)
    trust = getTrust(traits, characterCard, defaultScore=score)

    outMood = agreeability + "\n" + interest + "\n" + trust + "\n" + attraction

    return outMood.format(**chatInputs)
