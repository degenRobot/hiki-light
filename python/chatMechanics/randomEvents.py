
# random events that can happens 
# Wild CT Person Apprears 
# Another waifu interupts (random waifu you have interacted with before - i.e. might get jealous ???)
# Bird Poops on you lmeow - (other animals could also randomly come and interact w you and change the mood of the convo)
# Find items ??? (more for when actually walking around - but could be good to test this out - waifu's might even find stuff and just give to you)
# Random event that changes the mood of the character ? 
# Random event that changes the context of the conversation (could be shared SOW i.e. weather change / some other major event in Hikikomori Haven World)

### This could just be probability any random event happens between each message ? 
randomEventProb = 0.01

# TO DO - random events should also be location based - i.e. if in public place interruption more likely to happen.

# TO DO Seperate into categories i.e. in chat events vs new chat events 

randomEvents = {
    ### Would have to start new chat
    "Wild CT Person Appears" : {
        "description" : "A wild CT person appears",
        "newChat" : True,
        "probability" : 0.1,
        "message" : "A wild {char} appears",
        "context" : "{char} jumps out of nowhere and starts talking to {name} - completely interupting the conversation what name was doing."
    },
    ### Would have to start new chat + have some context 
    "Another Waifu Interupts" : {
        "description" : "Another waifu interupts",
        "newChat" : True,
        "probability" : 0.1,
        "message" : "{char} appears & interrupts your conversation",
        ### add in name of waifu that was interupts 
        "context" : """{char} interrupts conversation {name} is having. {char} is extremely jealous of the interaction {name} was just having."""
    },
    "Bird Poops on You" : {
        "description" : "Bird poops on you",
        "newChat" : False,
        "message" : "A wild bird just pooped on you",
        "probability" : 0.1,
        "context" : "A bird poops on {name}. {char} is amused & points it out to {name}."
    },
    "Find Item" : {
        "description" : "Find an item",
        "newChat" : False,
        "message" : "You find an item",
        "probability" : 0.1,
        "context" : "You find an item"
    },
    "Easter Egg" : {
        "description" : "Easter Egg",
        "newChat" : False,
        "message" : "Easter Egg",
        "probability" : 0.1,
        "context" : "TBD" #getEasterEgg()
    },

}