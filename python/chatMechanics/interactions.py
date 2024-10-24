# NOTE - this should be based on character card + traits of player
# i.e. depending on tings like trust / attraction interaction type will change
# also can have certain "interaction types" only available to certain characters
# NOTE - can also depend on location

interactionDict = {
    "chat used to generate a response when character is having a normal conversation with another character" : {
        "retriveAddedContext" : False,
        "retrivalType" : "",
        "Scenario Input" : """""",
        "Example Message" : """""",
        "promptInclusions" : {
            "includeLikes" : False,
            "includeExamples" : False,
            "includeScenario" : False,
            "includeAdditionalContext" : False
        }
    },
    "seduction used to generate a response when character is horny or aroused and attempting to seduce another character" : {
        "retriveAddedContext" : False,
        "retrivalType" : "",
        "Scenario Input" : """You are extremely aroused and are attempting to seduce {name}""",
        "Example Message" : """
Some typical replies for this situation : 
- Oh {name} you are irresistible, I can't stop thinking about you
- Hey {name} I have been thinking about you a lot lately (gently touches {name}'s arm) 
- I'm feeling quite aroused
""",
        "promptInclusions" : {
            "includeLikes" : False,
            "includeExamples" : False,
            "includeScenario" : True,
            "includeAdditionalContext" : True
        }
    },
    "sexy time used to simulate sexual interactions between characters" : {
        "retriveAddedContext" : False,
        "retrivalType" : "",
        "Scenario Input" : """You are roleplaying a sexual interaction between {char} and {name} be vivid 
and descriptive of the physical actions and dialogue of {char}""",
        "Example Message" : """
Some typical replies for this situation : 
 - (undresses revealing naked body) So {name} do you like what you see?
 - (slowly starts to stroke body) I'm perked up and raring to go.
 - (loudly moans in pleasure) This feels amazing 
""",
        "promptInclusions" : {
            "includeLikes" : False,
            "includeExamples" : True,
            "includeScenario" : True,
            "includeAdditionalContext" : False
        }
    },
    "discuss current events used to generate a response when asked about a specific current world event such as a news item" : {
        "retriveAddedContext" : True,
        "retrivalType" : "stateOfTheWorld",
        "promptContext" : "Some relevant information related to current events is (note these could be rumours & not necessarily true) : ",
        "Scenario Input" : """""",
        "Example Message" : """""",
        "promptInclusions" : {
            "includeLikes" : True,
            "includeExamples" : False,
            "includeScenario" : False,
            "includeAdditionalContext" : True
        }
    },
    "discuss backstory used to generate a response of characters such as things that happened in the past" : {
        "retriveAddedContext" : True,
        "retrivalType" : "backstory",
        "promptContext" : "Additional relevant based on your backstory is : ",
        "Scenario Input" : """""",
        "Example Message" : """""",
        "promptInclusions" : {
            "includeLikes" : True,
            "includeExamples" : False,
            "includeScenario" : False,
            "includeAdditionalContext" : True
        }

    },
    "previous interactions used to generate a response that takes into account past interactions between characters i.e. when asked something like remember when" : {
        "retriveAddedContext" : True,
        "retrivalType" : "previousInteractions",
        "promptContext" : "Additional context from previous interactions is : ",
        "Scenario Input" : """""",
        "Example Message" : """""",
        "promptInclusions" : {
            "includeLikes" : True,
            "includeExamples" : False,
            "includeScenario" : False,
            "includeAdditionalContext" : True
        }
    },

}
