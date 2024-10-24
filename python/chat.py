from characters.characterGen import BackstoryOptions, writeAllTraitsToDb
from helpers import *
from chatMechanics.promptBuilder import (
    summaryTemplate,
    midConversationTemplate,
    moodUpdateTemplate,
    interactionTemplate,
    builReplydPrompt,
    formatPrompt,
    getLikesAndDislikesPrompt,
    fakeItemChecker,
)
from chatMechanics.interactions import interactionDict
from config import configuration

from characters.playerOptions import getMood, getMoodScores
from chatMechanics.locations import locations
from chatMechanics.actionMechanics import takeAction


from chatMechanics.interactionsNew import interactionData, getAvailableInteractions 

import ollama
import time

import random
import replicate

from langchain.vectorstores import Chroma
import chromadb

from simulation.testPrompt import getTestPrompt, firstMessage

# TO DO - test out all LLM calls on replicate
persistent_client = chromadb.PersistentClient()

inputs = {}


def getInteractionTypes():
    out = ""
    interactionTypes = list(interactionDict.keys())

    for i in range(len(interactionTypes)):
        out += str(i) + " : " + interactionTypes[i] + "\n"

    return out


def getConext(char, name, interactionChroma):
    try : 
        nInteractions = interactionChroma.count()
    except :
        nInteractions = interactionChroma._collection.count()

    if (nInteractions) > 0:
        _interaction = interactionChroma.get(ids=[str(nInteractions)])
        return True, _interaction["documents"][0]
    else:
        return False, ""


# Used to get the time of the first, last interaction & total number of interactions with a character
def getInteractionTimeContextStr(char, name, interactionChroma: chromadb.Collection):
    try : 
        nInteractions = interactionChroma.count()
    except :
        nInteractions = interactionChroma._collection.count()


    if nInteractions > 1:
        # Get first interaction where id = 1
        _interactions = interactionChroma.get(ids=[str(1), str(nInteractions)])
        timeSinceFirstInteraction = datetime.now() - datetime.strptime(
            _interactions["metadatas"][0]["time"], "%Y-%m-%dT%H:%M:%S"
        )
        timeSinceLastInteraction = datetime.now() - datetime.strptime(
            _interactions["metadatas"][1]["time"], "%Y-%m-%dT%H:%M:%S"
        )
        outStr = (
            "You have interacted with "
            + name
            + " "
            + str(nInteractions)
            + " times. Your first interaction was "
            + timedelta_to_string(timeSinceFirstInteraction)
            + " ago and your last interaction was "
            + timedelta_to_string(timeSinceLastInteraction)
            + " ago."
        )
        return (outStr, nInteractions)

    elif nInteractions == 1:
        _interactions = interactionChroma.get(ids=[str(1)])
        timeSinceFirstInteraction = datetime.now() - datetime.strptime(
            _interactions["metadatas"][0]["time"], "%Y-%m-%dT%H:%M:%S"
        )
        outStr = (
            "This is your second interaction with "
            + name
            + ". Your first interaction was "
            + timedelta_to_string(timeSinceFirstInteraction)
            + " ago."
        )
        return (outStr, nInteractions)
    else:
        return ("", nInteractions)


def initConversation(
    characterCard, getUserResponse=True, firstMessage="Hello how are you?"
):
    char = characterCard["Name"]
    print(" ----- ")
    print("Starting Conversation With " + char)
    print(" ----- ")

    if getUserResponse:
        response = input("Start a conversation with " + char + ": ")
    else:
        response = firstMessage

    return response


def loadChromaCollections(characterCard, getUserResponse=True):
    id = characterCard["id"]
    if getUserResponse:
        append = ""
    else:
        append = "_test"

    backStoryChroma = Chroma(
        client=persistent_client,
        collection_name="backstory_" + id,
        embedding_function=configuration["embedding"],
    )

    interactionTypeChroma = Chroma(
        client=persistent_client,
        collection_name="interactionTypes",
        embedding_function=configuration["embedding"],
    )

    interactionChroma = Chroma(
        client=persistent_client,
        collection_name="interaction" + "_" + id + append,
        embedding_function=configuration["embedding"],
    )

    sowChroma = Chroma(
        client=persistent_client,
        collection_name="stateOfWorld",
        embedding_function=configuration["embedding"],
    )

    return backStoryChroma, interactionTypeChroma, interactionChroma, sowChroma


def genChatInputs(
    char,
    characterCard,
    userName,
    response,
    conversation,
    placeInput,
    testSubject="",
    scenarioInput="",
):
    
    itemsStr= """- No items have been given to {char} from {name} (if {name} gives an item to {char} in their next response it is fake item)"""
    chatInputs = {
        "char": char,
        "conversation": conversation,
        "appearance": characterCard["Appearance"],
        "personality": characterCard["Personality"],
        "speech": characterCard["Speech"],
        "mood": characterCard["Mood"],
        "name": userName,
        "interactionTypes": getInteractionTypes(),
        "context": characterCard["Context"],
        "lastResponse": response,
        "location": placeInput,
        "scenario": scenarioInput,
        "additionalContext": "",
        "likes": "",
        "dislikes": "",
        "examples": "",
        "subject": testSubject,
        "items" : itemsStr.format(char=char, name=userName)
    }

    return chatInputs


def getOllamaResponse(
    prompt, modelName="", trackTime=True, model=configuration["localModel"]
):
    start = time.time()
    _out = ollama.generate(model=model, prompt=prompt)
    _response = _out["response"]
    end = time.time()
    if trackTime == True:
        if configuration["enableLogging"]:
            print("Time to get response from Ollama : " + modelName + str(end - start))

    return _response


async def getReplicateResponse(
    prompt, modelName="", trackTime=True, deployment=configuration["replicateDeployment"], temperature=0.8, topP=0.9
):
    start = time.time()

    deployment = replicate.deployments.get(deployment)
    prediction = deployment.predictions.create(
        input={
            "prompt": prompt,
            "max_tokens": configuration["maxTokensOut"],
            "temperature": temperature,
            "top_p": topP,
        },
        stream=True,
    )
    #output = prediction.wait()
    await prediction.async_wait()
    #output = prediction.output()
    #print(prediction)
    out = ""
    for item in prediction.output:
        # item is generator object -> can be streamed to UI
        out += str(item)
    end = time.time()
    if trackTime == True:
        if configuration["enableLogging"]:
            print(
                "Time to generate response from replicate server : "
                + modelName
                + str(end - start)
            )

    return out


def determineInteractionType(chatInputs, interactionTypeChroma):
    _in = formatPrompt(interactionTemplate, chatInputs)
    if configuration["useOllama"]:
        interactionTypeQuery = getOllamaResponse(
            _in, " (Interaction Type Determination) "
        )
    else:
        interactionTypeQuery = getReplicateResponse(
            _in, " (Interaction Type Determination) "
        )
    start = time.time()
    interactionType = interactionTypeChroma.similarity_search(interactionTypeQuery)
    end = time.time()

    if configuration["enableLogging"]:
        print("Time to get interaction type from DB : " + str(end - start))
    if configuration["enableLogging"]:
        print("Interaction Type : " + interactionType[0].page_content)

    _interactionData = interactionDict[interactionType[0].page_content]

    return _interactionData


def retriveAdditionalContext(chatInputs, _interactionData, characterCard):
    id = characterCard["id"]
    _retriveType = _interactionData["retrivalType"]
    start = time.time()

    if _retriveType == "stateOfTheWorld":
        _retriveCollection = "stateOfTheWorld"
    elif _retriveType == "backstory":
        _retriveCollection = "backstory_" + id
    elif _retriveType == "previousInteractions":
        _retriveCollection = "interaction_" + id

    _retriveChroma = Chroma(
        client=persistent_client,
        collection_name=_retriveCollection,
        embedding_function=configuration["embedding"],
    )

    maxDocsIn = 2

    # If collection has relevant records then retrive them and add to additional context
    if _retriveChroma._collection.count() > 0:
        _retriveQuery = chatInputs[
            "lastResponse"
        ]  # Check if it works doing user + last AI response (last n responses of conversation)
        _retriveDocs = _retriveChroma.similarity_search(_retriveQuery)
        # Could also filter by score i.e. _retriveChroma.similarity_search_with_score(_retriveQuery) & only include if > threshold
        retrivedContext = _interactionData["promptContext"]
        n = min(len(_retriveDocs), maxDocsIn)
        for i in range(n):
            retrivedContext += (
                "\n"
                + " - "
                + convert_to_normalized_sentence(_retriveDocs[i].page_content)
            )
        if configuration["enableLogging"]:
            print("Retrieved Additional Context : " + retrivedContext)
        if configuration["enableLogging"]:
            print("Retrieved Additional Context : " + retrivedContext)
        end = time.time()
        print("Time to retrive additional context : " + str(end - start))
    else:
        retrivedContext = ""

    return retrivedContext


def updateMood(chatInputs):
    _prompt = formatPrompt(moodUpdateTemplate, chatInputs)
    if configuration["useOllama"]:
        _out = getOllamaResponse(_prompt, " (Update Mood) ")
    else:
        _out = getReplicateResponse(_prompt, " (Update Mood) ")
    return _out


async def midConversationSummary(chatInputs, deployment = configuration['replicateDeployment']) -> str:
    _prompt = formatPrompt(midConversationTemplate, chatInputs)
    if configuration["useOllama"]:
        _out = getOllamaResponse(_prompt, " (Mid Conversation Summary) ")
    else:
        _out = await getReplicateResponse(_prompt, " (Mid Conversation Summary) ", deployment=deployment)
    return _out


async def endOfInteractionSummary(chatInputs, deployment = configuration['replicateDeployment']):
    _prompt = formatPrompt(summaryTemplate, chatInputs)
    if configuration["useOllama"]:
        _out = getOllamaResponse(_prompt, " (End Of Conversation Summary) ")
    else:
        _out = await getReplicateResponse(_prompt, " (End Of Conversation Summary) ", deployment=deployment)
    return _out

async def manageConversationLengthOld(conversation, convList, response, chatInputs, out, char, userName) :
    conversation += userName + ": " + response + "\n"
    conversation += char + ": " + out + "\n"

    convList.append(userName + ": " +response + "\n")
    convList.append(char + ": " + out + "\n")

    if (configuration['enableLogging']) : 
        print("Conversation Length : " + str(countTokens(conversation)))
    
    if (countTokens(conversation) > configuration['maxConervationLength']) : 
        n = len(conversation)
        nToRemove = int(n * configuration['summaryPercent'])

        summaryInput = ""
        i = 0

        while (len(summaryInput) < nToRemove) :
            summaryInput += convList[i]
            i += 1

        chatInputs["conversationIn"] = summaryInput
        summary = await midConversationSummary(chatInputs) 

        # Would this work better in additional context field ??? 
        conversation = summary        
        if (configuration['enableLogging']) : 
            print("Mid Conversation Summary : " + summary)

        newConvList = convList[i:]
        n = len(newConvList)
        # Loop from i to n and add to conversation
        for i in range(n) : 
            conversation += newConvList[i]

        convList = [summary] + newConvList

    return conversation, convList


def getChatPrompt(_interactionData, chatInputs, characterCard):
    id = characterCard["id"]

    if _interactionData["retriveAddedContext"] == True:
        chatInputs["additionalContext"] = retriveAdditionalContext(
            chatInputs, _interactionData, characterCard
        )

    (
        _includeLikes,
        _includeExamples,
        _includeScenario,
        _includeAdditionalContext,
    ) = _interactionData["promptInclusions"]
    if _interactionData["promptInclusions"]["includeExamples"] == True:
        chatInputs["examples"] = _interactionData["Example Message"]
    if _interactionData["promptInclusions"]["includeScenario"] == True:
        chatInputs["scenario"] = _interactionData["Scenario Input"]
    """
    if (_interactionData['promptInclusions']['includeLikes'] == True) :
        likesChroma = Chroma(client=persistent_client,collection_name="Likes" + "_" + id, embedding_function=configuration['embedding'])
        dislikesChroma = Chroma(client=persistent_client,collection_name="Dislikes" + "_" + id, embedding_function=configuration['embedding'])
        chatInputs['likes'], chatInputs['dislikes'] = getLikesAndDislikesPrompt(characterCard, chatInputs['conversation'], likesChroma, dislikesChroma)
    """

    if chatInputs["location"] != "":
        _includeLocation = True
    else :
        _includeLocation = False

    _chatPrompt = builReplydPrompt(
        includeLikes=_interactionData["promptInclusions"]["includeLikes"],
        includeExamples=_interactionData["promptInclusions"]["includeExamples"],
        includeScenario=_interactionData["promptInclusions"]["includeScenario"],
        includeAdditionalContext=_interactionData["promptInclusions"][
            "includeAdditionalContext"
        ],
        includeLocation=_includeLocation,
        interactionLogBeforeSpeech = False
    )

    _chatPrompt = formatPrompt(_chatPrompt, chatInputs)

    ### Handle case if prompt is too long -> loop through conversation and only include last n responses

    if configuration["enableLogging"]:
        print("Prompt Length : " + str(countTokens(_chatPrompt)))

    return _chatPrompt


async def startConversation(
    characterCard,
    interactionDescription = "Chat",
    firstMessage="Hello how are you?",
    subject="",
    updatedMood=True,
    writeSummaryToDb=True,
    userName="Chad",
    getUserResponse=True,
    testLength=20,
    initPrompt="",
    conversation="",
    location="",
    deployment=configuration["replicateDeployment"],
    testDescription = "",
):
    convList = []
    char = characterCard["Name"]
    logs = []
    nResponses = 0
    # Load up DB Info
    (
        backStoryChroma,
        interactionTypeChroma,
        interactionChroma,
        sowChroma,
    ) = loadChromaCollections(characterCard, getUserResponse=getUserResponse)
    # Get dictionary to be passed into prompt template

    _initMessage = firstMessage.format(char=char)
    response = initConversation(
        characterCard, getUserResponse, firstMessage=_initMessage
    )

    chatInputs = genChatInputs(
        char,
        characterCard,
        userName,
        response,
        conversation,
        location,
        testSubject=subject,
    )

    if characterCard['calcMood']:
        chatInputs["mood"] = getMood(characterCard=characterCard, chatInputs=chatInputs, score=characterCard["AffectionScore"])
        #print("Mood : " + chatInputs["mood"])
    else : 
        chatInputs["mood"] = characterCard["Mood"]

    # Grab Latest Context from DB
    contextExists, context = getConext(char, userName, interactionChroma)
    # Get Interaction Time Context

    # TO DO - create function that grabs all relevant context
    interactionTimeContext, intNumber = getInteractionTimeContextStr(
        char, userName, interactionChroma
    )
    chatInputs["chatId"] = char + "_" + userName + "_" + str(intNumber)
    chatInputs["model"] = deployment

    if configuration["enableLogging"]:
        print("Interaction Time Context : " + interactionTimeContext)

    if contextExists:
        chatInputs["context"] = context
        chatInputs["context"] += interactionTimeContext

    _interactionData = interactionData[interactionDescription]
    #interactionType = "chat used to generate a response when character is having a normal conversation with another character"

    while response != "/exit":

        chatInputs["lastResponse"] = response
        chatInputs["conversation"] += "User" + ": " + response + "\n"

        likesChroma = Chroma(
            client=persistent_client,
            collection_name="Likes" + "_" + characterCard["id"],
            embedding_function=configuration["embedding"],
        )
        dislikesChroma = Chroma(
            client=persistent_client,
            collection_name="Dislikes" + "_" + characterCard["id"],
            embedding_function=configuration["embedding"],
        )

        chatInputs["likes"], chatInputs["dislikes"] = getLikesAndDislikesPrompt(
            characterCard, chatInputs["conversation"], likesChroma, dislikesChroma
        )

        _interactionData["includeLikes"] = True
        # Based on interaction type choose which chain to use + fetch any required additional context
        _chatPrompt = getChatPrompt(_interactionData, chatInputs, characterCard)
        chatInputs["prompt"] = _chatPrompt

        #print(_chatPrompt)

        # Check Prompt Length 
        maxPromptLength = 2000
        if countTokens(_chatPrompt) > maxPromptLength :

            while countTokens(_chatPrompt) > maxPromptLength :
                # Dumb down version just to make sure don't break model again
                convList = convList[1:]
                conversation = ""
                for i in range(len(convList)) : 
                    conversation += convList[i]
                chatInputs["conversation"] = conversation
                _chatPrompt = getChatPrompt(_interactionData, chatInputs, characterCard)
                
            chatInputs["prompt"] = _chatPrompt

        # check for fake items 
        """
        fakeItemInput = formatPrompt(fakeItemChecker, chatInputs)
        fakeItemOut = await getReplicateResponse(fakeItemInput, " (Fake Item Checker) ", deployment=deployment)
        if len(fakeItemOut) > 10 : 
            chatInputs["lastResponse"] +=  "\n ### System: \n " + fakeItemOut 
            _chatPrompt = getChatPrompt(_interactionData, chatInputs, characterCard)
        """
        out = await getReplicateResponse(_chatPrompt, " (Chat Prompt) ", deployment=deployment)

        # clean up resonse -> remove char : 
        out = out.replace(char + ": ", "")

        print(" ----- ")
        print(char + ": " + out)
        # Update conversation + chatinputs
        conversation, convList = await manageConversationLengthOld(
            conversation, convList, response, chatInputs, out, char, userName
        )

        (
            chatInputs["conversation"],
            chatInputs["output"],
            chatInputs["responseNumber"],
        ) = conversation, out, nResponses + 1
        print(" ----- ")

        chatInputs["time"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _newLog = chatInputs.copy()
        logs.append(_newLog)

        if getUserResponse:
            response = input("Your Response : ")

            if response == "/action" : 
                
                action, actionMessage, outcome, desc = takeAction()

                # Update mood 

                characterCard["AffectionScore"] += outcome["effects"]["attraction"]
            
                print("New Attraction : " + str(characterCard["AffectionScore"]))
                if action == "Give Item" :
                    chatInputs["items"] += desc
                
                chatInputs["mood"] = getMood(characterCard=characterCard, chatInputs=chatInputs, score=characterCard["AffectionScore"])
                #print(action)
                #print(outcome)
                print("Action Taken ----- : ")
                response = actionMessage + " " + outcome["context"]
                # outcome["context"] -> could also be added to context field ??? 
                # TO DO - experiment to see which way works best 
                # arrest probability 
                pArrest = .1
                p = random.random()
                response = formatPrompt(response, chatInputs)  
                print(formatPrompt(action, chatInputs))

                ### should also only happen if action outcome is negatve / or could do pArrest from outcome["effects"]???
                if (p < pArrest) :
                    print("You have been arrested for being a creep")
                    characters = json.load(open("characters.json", "r"))
                    fbiAgent = characters["fbi"]
                    char = "fbi"
                    characterCard = fbiAgent
                    arrestReason = await endOfInteractionSummary(chatInputs)


                    subject = "(You have just arrested " + userName + " for being a creep - he was previously doing " + arrestReason + ")"
                    response += " " + subject
                    chatInputs = genChatInputs(
                        "fbi",
                        fbiAgent,
                        userName,
                        "",
                        "",
                        location,
                        testSubject=subject,
                    )
                ### Should also do update of mood based outcome["effects"]             

        else:
            if nResponses < testLength:
                nResponses += 1
                testCharPrompt = getTestPrompt(chatInputs["subject"], testDescription=testDescription)
                userSimPrompt = formatPrompt(testCharPrompt, chatInputs)
                response = await getReplicateResponse(userSimPrompt)
                print("Response Number : " + str(nResponses))
                print("User simulated response : " + response)

            else:
                response = "/exit"

    summary = await endOfInteractionSummary(chatInputs)

    # Update context based on previous interaction
    if writeSummaryToDb:
        characterCard["Context"] = summary
        if configuration["enableLogging"]:
            print("Adding Summary to DB")
        id = interactionChroma._collection.count() + 1
        doc = createDoc(summary, char, userName)
        interactionChroma.add_documents([doc], ids=[str(id)])

    # Log conversation to json
    updateLogs(logs, getUserResponse)

    if configuration["enableLogging"]:
        print("There are", interactionChroma._collection.count(), "in the collection")

    return conversation, characterCard, logs


def waifuChatSetUp(characters) : 
    availableLocations = findAvailableLocations(locations)
    # This should be based on actual location of character in game -> for testing purposes we will just use a dropdown
    #location = dropdown_selection(availableLocations + [""])
    location = "Hotel"
    locationDescription = locations[location]["description"]
    # TO DO - make this function of location (i.e. each char has set location on map)
    availableCharacters = findAvailableCharacters(characters)
    char = dropdown_selection(availableCharacters + ["/exit"])



    # TO DO - choose interaction type
    characterCard = characters[char]
    # Randomly initialize between 7 & 3
    characterCard["AffectionScore"] = 7 - (4 * random.random())   


    if characterCard["calcMood"]:
        scores = getMoodScores(characters[char])
        availableInteractions = getAvailableInteractions(scores, location)        
        interactionType = dropdown_selection(availableInteractions)
    else : 
        interactionType = "Chat"
        
    # TO DO - interaction type should be determined here 
    # (i.e. first get mood + location & user decides based on what interaction types are available)
        
    return characterCard, interactionType, locationDescription

def wildChatSetUp(personas) : 
    location = "Park"
    locationDescription = locations[location]["description"]
    availableCharacters = findAvailableCharacters(personas)
    char = dropdown_selection(availableCharacters + ["/exit"])
    characterCard = personas[char]
    interactionType = "Chat"
    return characterCard, interactionType, locationDescription


async def start(inputs):
    # Handle the case where this fails
    with open("characters.json", "r") as fp:
        characters = json.load(fp)

    with open("personas.json", "r") as fp:
        personas = json.load(fp)

    inputs["characters"] = characters
    inputs["name"] = input("What is your name? ")

    while True:
        print("Choose Mode : ")
        mode = dropdown_selection(["Waifu Chat", "CT Persona Chat"])

        if mode == "Waifu Chat":
            characterCard, interactionType, locationDescription = waifuChatSetUp(characters)
        else :
            characterCard, interactionType, locationDescription = wildChatSetUp(personas)

        conversation, characterCard, logs = await startConversation(characterCard, 
                                                                    userName=inputs["name"], 
                                                                    interactionDescription=interactionType, 
                                                                    location = locationDescription)
        ## TO DO - save updated character card
        # Save updated characters to file
        print(" ----- ")
        print("Ending Conversation With " + characterCard["Name"])
        print(" ----- ")



