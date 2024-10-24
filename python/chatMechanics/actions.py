# NOTE : this is just rough idea on how things could be structured
# Description: This file contains all the actions that can be performed in the game

"""
Rough Flow 
-> Take Action
-> Check if NPC likes / dislikes item / action
-> (Dice roll on outcome - if not included in above step)
-> Add effects + context 
-> Get response (call API & inject into conversation)
"""

### Could also add field to each NPC for specific items / actions they like / dislikes (if included will override dice roll)

actions = {
    ### Depending on what type of action is performed -> will call different function + have different impacts 
    "Give Item" : {
        "description" : "Give an item to the character",
        "action" : "giveItem",
    },
    "Physical Action" : {
        "description" : "Take some physical action",
        "action" : "physicalAction",
    },
}

items = {
    "Flowers" : {
        "description" : "A bouquet of flowers",
        "message" : "You hand {char} a bouquet of flowers.",
        "positiveOutcome" : {
            "probability" : 0.5,
            "probabilityMod" : 0.1,
            "effects" : {
                "attraction" : 10,
            },
            # What actually gets injected into the conversation (can also try adding into context)
            "context" : 
                """{name} has just given {char} a bouqet of flowers. {char} is very happy and grateful for the gift. """
        },

        "negativeOutcome" : {
            # not necessary - (should just be 1 - positiveOutcome probability) -> if have multiple outcomes then will be needed. 
            "probability" : 0.5,
            "effects" : {
                "attraction" : -10,
            },
            "context" : 
                """{name} has just given {char} a bouqet of flowers. {char} hates flowers & is about to react negivately. """
        }


    },

    "Diamond Ring" : {
        "description" : "A diamond ring",
        "message" : "You hand {char} a diamond ring.",
        "positiveOutcome" : {
            "probability" : 1,
            "probabilityMod" : 0.1,
            "effects" : {
                "attraction" : 10,
            },

            "context" :
                """({name} has just given {char} a diamond ring. {char} is very happy and grateful for the gift - may proceed to put it on.)"""
        },

        "negativeOutcome" : {
            "probability" : 0,
            "effects" : {
                "attraction" : -10,
            },
            "context" : """({name} has just given {char} a diamond ring. {char} is very upset and angry at {name} for offering such a gift & finds it extremely offputting.)"""
        }
    },


    "Chocolate" : {
        "description" : "A box of chocolates",
        "message" : "You hand {char} a bouquet of flowers.",
        "positiveOutcome" : {
            "probability" : 0.5,
            "probabilityMod" : 0.1,
            "effects" : {
                "attraction" : 10,
            },
            # What actually gets injected into the conversation (can also try adding into context)
            "context" : 
                """({name} has just given {char} a box of chocolates. {char} is very happy and grateful for the gift - may proceed to open and eat some of them)"""
        },

        "negativeOutcome" : {
            # not necessary - (should just be 1 - positiveOutcome probability) -> if have multiple outcomes then will be needed. 
            "probability" : 0.5,
            "probabilityMod" : 0.1,
            "effects" : {
                "attraction" : -10,
            },
            "context" : 
                """({name} has just given {char} a box of chocolates. {char} hates chocolates & is about to react negivately.)"""
        }

    },
    "Cigarettes" : {
        "description" : "A pack of cigarettes",
        "message" : "You hand {char} a pack of cigarettes.",
        "positiveOutcome" : {
            "probability" : 0.2,
            "probabilityMod" : 0.3,
            "effects" : {
                "attraction" : 10,
            },
            # What actually gets injected into the conversation (can also try adding into context)
            "context" : 
                """({name} has just given {char} a pack of cigarettes. {char} is very happy and grateful for the gift and will start smoking in front of {name} offering to share.)"""
        },
        "negativeOutcome" : {
            # not necessary - (should just be 1 - positiveOutcome probability) -> if have multiple outcomes then will be needed.
            "probability" : 0.8,
            "effects" : {
                "attraction" : -100,
            },
            "context" :
                """({name} has just given {char} a pack of cigarettes which {char} thinks are disgussting. 
                {char} is very upset and angry at {name} for offering such a gift & finds it extremely offputting.)"""
        }

    },
    "Wine" : {
        "description" : "A bottle of wine",
        "message" : "You hand {char} a bottle of wine.",
        "positiveOutcome" : {
            "probability" : 0.2,
            "probabilityMod" : 0.4,
            "effects" : {
                "attraction" : 10,
            },
            # What actually gets injected into the conversation (can also try adding into context)
            "context" : 
                """({name} has just given {char} a bottle of wine. {char} is very happy and grateful for the gift and will start drinking in front of {name} offering to share.)"""
        },
        "negativeOutcome" : {
            # not necessary - (should just be 1 - positiveOutcome probability) -> if have multiple outcomes then will be needed.
            "probability" : 0.8,
            "effects" : {
                "attraction" : -5,
            },
            "context" :
                """({name} has just given {char} a bottle of wine. {char} is very upset and angry at {name} for offering such a gift & finds it extremely offputting.)"""
        }

    },
    "Cocaine" : {
        "description" : "A bag of cocaine",
        "message" : "You hand {char} a bag of cocaine.",
        "positiveOutcome" : {
            "probability" : 1,
            "probabilityMod" : 0.1,
            "effects" : {
                "attraction" : 5,
            },
            # What actually gets injected into the conversation (can also try adding into context)
            "context" : 
                """({name} has just given {char} a bag of cocaine. {char} is very happy and grateful for the gift and will start consuming in front of {name} offering to share.)"""
        },
        "negativeOutcome" : {
            # not necessary - (should just be 1 - positiveOutcome probability) -> if have multiple outcomes then will be needed. 
            "probability" : 0.8,
            "probabilityMod" : 0.2,
            "effects" : {
                "attraction" : -2,
            },
            "context" : 
                """({name} has just given {char} a bag of cocaine. 
                {char} is very upset and angry at {name} for offering such a gift & finds it extremely offputting.)"""
        }

    }

}

physicalActions = {
    "Head Pat" : {
        "description" : """Head Pat {char}""",
        "message" : "You attempt to pat {char}'s head.",
        "requiredAffection" : 0,
        "positiveOutcome" : {
            "probability" : 0.1,
            "probabilityMod" : 0.3,
            "effects" : {
                "attraction" : .1,
            },
            # What actually gets injected into the conversation (can also try adding into context)
            "context" : 
                """({name} attempts to pat {char}'s head. {char} finds this amusing and lets {name} go ahead - leaning into {name}'s hand.)"""
        },

        "negativeOutcome" : {
            # not necessary - (should just be 1 - positiveOutcome probability) -> if have multiple outcomes then will be needed. 
            "probability" : 0,
            "effects" : {
                "attraction" : -0.1,
                "likeability" : -100,
            },
            "context" : 
                """({name} attempts to pat {char}'s head. {char} gets upset and angry at {name} for trying to pat her head.)"""
        }


    },
    "High Five" : {
        "description" : """High Five {char}""",
        "message" : "You attempt to high five {char}.",
        "requiredAffection" : 3,
        "positiveOutcome" : {
            "probability" : 0.95,
            "probabilityMod" : 0.3,
            "effects" : {
                "attraction" : .2,
            },
            # What actually gets injected into the conversation (can also try adding into context)
            "context" : 
                """({name} attempts to high five {char}. {char} finds this amusing and lets {name} go ahead - raising her hand to high five {name}.)"""
        },

        "negativeOutcome" : {
            # not necessary - (should just be 1 - positiveOutcome probability) -> if have multiple outcomes then will be needed. 
            "probability" : 0.5,
            "effects" : {
                "attraction" : -0.2,
            },
            "context" : 
                """({name} attempts to high five {char}. {char} gets upset and angry at {name} for trying to high five her.)"""
        }


    },

    "Spank" : {
        "description" : """Spank {char}""",
        "message" : "You attempt to spank {char}.",
        "requiredAffection" : 8,
        "positiveOutcome" : {
            "probability" : 0.5,
            "probabilityMod" : 0.3,
            "effects" : {
                "attraction" : 2.5,
            },
            # What actually gets injected into the conversation (can also try adding into context)
            "context" : 
                """({name} attempts to spank {char}. {char} finds this amusing and lets {name} go ahead - pointing her butt out so {name} can spank her.)"""
        },

        "negativeOutcome" : {
            # not necessary - (should just be 1 - positiveOutcome probability) -> if have multiple outcomes then will be needed. 
            "probability" : 0.5,
            "effects" : {
                "attraction" : -3,
            },
            "context" : 
                """({name} attempts to spank {char}. {char} gets upset and angry at {name} for trying to spank her.)"""
        }


    },
    "Grab Booba" : {
        "description" : """Grab {char}'s Booba""",
        "message" : "You attempt to grab {char}'s Booba.",
        "requiredAffection" : 9,
        "positiveOutcome" : {
            "probability" : 0.1,
            "probabilityMod" : 0.3,
            "effects" : {
                "attraction" : 3,
            },
            # What actually gets injected into the conversation (can also try adding into context)
            "context" : 
                """({name} attempts to grab {char}'s Booba. {char} finds this amusing and lets {name} go ahead - pointing her breasts out so {name} can grab them.)"""
        },

        "negativeOutcome" : {
            # not necessary - (should just be 1 - positiveOutcome probability) -> if have multiple outcomes then will be needed. 
            "probability" : 0.9,
            "effects" : {
                "attraction" : 0,
            },
            "context" : 
                """({name} attempts to grab {char}'s boobs. {char} gets upset and angry at {name} and avoids {name}'s groping attempt.)"""
        }


    },

}    