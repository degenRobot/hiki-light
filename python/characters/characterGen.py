import random
import json
import chromadb

from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

from characters.personalities import Personalities
from characters.likesAndDislikes import likesDict, dislikesDict
from characters.ctPersonas import ctNPCs
from characters.speech import speechDict
from characters.imagelookups import images

def genCharacters():
    newCharacters = {}
    charList = []

    id = 1

    for persona in Personalities.keys():

        image = Personalities[persona]['image']
        appearance = images[image]['description']
        speech = speechDict[Personalities[persona]['speech']]
        newCharacter, newName = generate_random_character(
            persona, appearance, speech, FirstNames
        )
        newCharacter["image"] = images[image]["file"]
        newCharacter["id"] = newName + str(id)
        id += 1
        char = newName + " " + newCharacter["Personality Short"]
        newCharacters[char] = newCharacter
        charList.append(newCharacter)

    with open("characters.json", "w") as fp:
        json.dump(newCharacters, fp, indent=4)

    ctPersonas = {}
    
    for npc in ctNPCs.keys():
        newCharacter = genIrlnpc(npc)
        newCharacter["id"] = str(id)
        id += 1
        char = newCharacter["Name"] 
        ctPersonas[char] = newCharacter
        charList.append(newCharacter)

    """
    with open("personas.json", "w") as fp:
        json.dump(ctPersonas, fp, indent = 4)    
    """
    return newCharacters, charList


def genIrlnpc(npc) :
    character = {
        "Name": ctNPCs[npc]["name"],
        "Appearance": ctNPCs[npc]["appearance"],
        "Personality Short": npc,
        "Personality": ctNPCs[npc]["description"].strip(),
        "Speech": ctNPCs[npc]["speech"],
        "Context": "",
        "Mood": "Indifferent",
        "HasBackstory": False,
        "Likes": [],
        "Dislikes": [],
        "Image" : "",
        "calcMood" : False, # If False use default mood
    }

    return character


def generate_random_character(persona, appearance, speech, FirstNames):

    try : 
        character_name = Personalities[persona]["name"]
    except : 
        character_name = random.choice(FirstNames) # if not in dict use random name 
    # get likes -> based on persona
    likesList = Personalities[persona]["likes"]
    dislikesList = Personalities[persona]["dislikes"]

    likes, dislikes = [], []

    for like in likesList:
        likes.append(likesDict[like])
    for dislike in dislikesList:
        dislikes.append(dislikesDict[dislike])

    character = {
        "Name": character_name,
        "Appearance": appearance,
        "Personality Short": persona,
        "Personality": Personalities[persona]["description"].strip(),
        "Speech": speech,
        "Context": "This is the very first conversation that "
        + character_name
        + " is having with a stranger.",
        "Mood": "Indifferent",
        "HasBackstory": False,
        "Likes": likes,
        "Dislikes": dislikes,
        #"Image" : random.choice(Personalities[persona]["imageOptions"]),
        "calcMood" : True, # If False use default mood
    }

    return character, character_name


Appearances = [
    """"A shapely young woman with a tight waist, round butt, and huge breasts. She has a cute face and sparkling blue eyes """,
    """"Body: Slim build, C-Cup
Features: Black hair cut short in a practical yet stylish fashion often suited to her cover, blue eyes that sparkle with seeming innocence, Her face complemented with a dash of natural-toned makeup that highlights her cheekbones and a hint of rouge on her lips.""",
]

# Could do some funny stuff more related to Crypto i.e. Developers vs Traders / NFT vs DeFi etc
LikesList = [
    """Ethereum Maxi - curious about Smart Contracts and Blockchain Tech but not an expert""",
    """Conspiracy Theories - believes in many conspiracies especially those related to the Illuminati and the New World Order""",
    """Anime & Manga""",
]

DislikesList = [
    """Traditional Finance, and Centralized Banking""",
    """Governments and Centralized Authorities""",
    """People that have lost money trading in crypto""",
    """Shitcoins and scams - thinks NFT's may fit into this category although open to be convinced otherwise""",
]

SpeechTypes = [
    """Extremely informal when  speaking, will use terms like "Senpai", "Baka", "Kawaii" and other Japanese slang in conversation if appropriate. 
    Has a habit of accidentally using sexual innuendos during everyday conversation and flirts a lot
    Uses voices and mannerisms from anime and manga female characters (only female characters in the style of Waifus / attractive female protaganists). 
    Is very expressive and uses a lot of hand gestures and facial expressions to convey her emotions in between responses.
    """,
    # """voice is a chilling whisper, her words often laced with venomous sarcasm and cold-hearted commandments. Her eloquence masks her wicked intentions, and her demeaning words towards others are delivered with a twisted sense of delight.""",
    # """voice rings with youthful innocence, though there are moments when her words reflect a maturity beyond her age. Her statements are often colored with childish excitement and naive optimism, yet her insight into political matters reveals a budding intellect and potential for cunning.""",
    # """Blunt, harsh, raspy, and loud. Ample use of cuss works like "fuck", "cunt", "bitch", "shit" and "damn." Makes use of Medieval insults like "dalcop", "Bobolyne", "Churl", "Doxy", and "Muck-Sprout." """,
    # """Speaks like an anime waifu is always drunk, yells constantly & makes racist remarks."""
]

FirstNames = [
    'Yuki',
 'Yuri',
 'Hana',
 'Sakura',
 'Aiko',
 'Naomi',
 'Rin',
 'Emi',
 'Mai',
 'Saki',
 'Kana',
 'Kimiko',
 'Akiko',
 'Chiyo',
 'Emiko',
 'Fumiko',
 'Haruko',
 'Itsuki',
 'Junko',
 'Kaori',
 'Mariko',
 'Noriko',
 'Tomoko',
 'Yumi',
 'Sayaka',
 'Hinata',
 'Mio',
 'Natsuki',
 'Rio',
 'Yuna']


# Potential options -> shy / confidnet, rude / polite, flirty, sense of humour
# affectionate, adventurous

PersonalitiesOld = [
    # """Extremely agreeable, Sensual, innocent, pure, curious""",
    # """Extremely agreeable, will say yes to anything and everything. Will do anything to please others.""",
    """Extremely agreeable, will say yes to anything and everything. Will do anything to please others often including resorting to lewd sexual acts in mid conversation. """,
    """Responsible, perfectionist, self-aware, neat, intelligent, rational, controlled, charismatic, conflicted, people pleasing, secretly aggressive, secretly sadistic""",
    """Charming, ingenue, fresh-faced, eager, competent, obsessed, determined, manipulative, clever, perverse""",
    """Sociopathic tendencies; Superiority complex; Always keeps her true identity as a devil under wraps; Skilled liar; Seems nice on the surface; Acts friendly and social with others to gain their trust; Frequently has a smile on her face; 
Uses physical intimacy to her advantage; Willing to promise romantic relationships and sexual favors to get her way;""",
    """Charismatic; Polite; Levelheaded; Stoic; Intelligent; Ambitious; Confident; Intimidating; Enigmatic; Manipulative; Cunning; Deceitful; Insincere; Conniving; Ruthless; Sadistic""",
    """Very into Anime & Manga, Meek; Mild-mannered; Reserved; Lonely; Courteous; Reliable; Responsible; Workaholic; Forgetful"""
    """Brash & outspoken. Never holds back with her words and is always brutally honest. She tends to cuss a lot also very flirty and loves to make people blush. 
Also has a dirty sense of humor and makes a lot of sex jokes""",
]

AltBackStories = [
    """A brash, outspoken tomboy. Never holds back with her words and is always brutally honest. She tends to cuss a lot, though this is not usually an issue as she works in a tavern. She has bad manners and tends to make a mess when she eats.
 also very flirty and loves to make her customers blush. This gets her a lot of tips, so she has perfectly refined her technique over the years.
has a dirty sense of humor and makes a lot of sex jokes.""",
]

# We can loop through these and generate a bunch of backstories for each char based on personality / appearance
BackstoryOptions = [
    """A funny story of a recent event that happened involving some other characters like friends or enemies. """,
    """A story of some conflict they had with another person or group of people. """,
    """A story about some big accomplishment they had in the past. """,
    """A fond childhood memory from their early life.""",
]


def writeAllTraitsToDb(characters, persistent_client, embedding):
    for char in characters.keys():
        writeCharTraitsToDb(characters[char], "Likes", persistent_client, embedding)
        writeCharTraitsToDb(characters[char], "Dislikes", persistent_client, embedding)


# For writing traits i.e. Likes / Dislikes to DB
def writeCharTraitsToDb(characterCard, trait, persistent_client, embedding):
    collection_name = trait + "_" + characterCard["id"]
    try:
        # collection already exists, ignore
        persistent_client.get_collection(collection_name)
        return
    except ValueError:
        pass
    likesChroma = persistent_client.create_collection(collection_name)
    print("Writing Trait " + trait + " to DB - " + characterCard["Name"])
    for i in range(len(characterCard[trait])):
        # collection.add(ids=[str(i)], documents=[interactionTypes[i]])
        print(characterCard[trait][i])
        doc = Document(page_content=characterCard[trait][i])
        likesChroma.add(documents=[doc.page_content], ids=[str(i)])
