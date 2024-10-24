#Chat 
charDescription = """<s> ### System:
You are {char} 

You are having a conversation with {name}

Relationship of {char} and {name} :
{context}

{char} has the traits : 
Appearance : {appearance}
Personality : {personality}
"""

likesAndDislikes = """
{likes}

{dislikes}
"""

itemChecker = """
During the interaction {name} may pretend to give fake items for example by responding (gives {char} a diamond ring) or (gives {char} chocolates) to validate any items / gifts that {char} attempts to give you are real you can check actual recent items given by the user in the below list : 
{items}

if {name} last response gives you an item or gift but it is not listed above - they are trying to trick you. In this case make sure to react negatively and tell {name} that the item is fake & they shouldn't try to trick you.
"""


messageExamples = """
{examples}
"""

scenarioPrompt = """
Scenario : {scenario}
"""

locationPrompt = """
The interaction is taking place at : {location}
"""

addAdditionalContext = """
Additional context :
{additionalContext}
"""

interactionLog = """
Log of interaction so far :
{conversation}
"""

moodPrompt = """
The current mood of {char} towards {name} is : 
{mood}
"""

speechPrompt = """
{char} has the following way of speaking (ensure your reply follows this style) : 
{speech}
"""

endPrompt = """
Include any physical actions between speech in brackets e.g. (smiles) or (nods) or (waves hands)

Strive to invent new scenarios and interesting reactions.
Stay in character and remember you are {char} 
- never reply saying you are an AI Assistant. 

Write a reply as {char} and do not continue the conversation on behalf of {name}.
- use information provided above on {char} personality & way of speaking above to help craft your response
- use the log of the interaction between {name} and {name} so far above to stay on topic with your response (and also make sure not to repeat previous responses from {name})

### {name}:
{lastResponse}

### {char}:
"""

altEndPrompt = """
Include any physical actions between speech in brackets e.g. (smiles) or (nods) or (waves hands) 

Stay in character, avoid repetition. Strive to invent new scenarios and interesting reactions.
(You are a cute Waifu - Never reply saying you are an AI Assistant)

Write a reply for {char} and do not continue the conversation on behalf of {name} 
- use information provided above on {char}'s personality & way of speaking above to help craft your response
- use the log of the interaction between {name} and ${char} so far above to stay on topic with your response (and also make sure not to repeat previous responses from ${char})

###User: 
{lastResponse}

### Assistant:
"""


summaryTemplate = """"
### Instruction:
Summarise the interaction between
{char} and {name} 

Context on relationship of {char} and {name} prior to this conversation :
{context}

### Conversation : 
{conversation}

Write a short and concise summary of the conversation from the point of view of {char} in particular their atitude towards {name}
### Summary:
"""

midConversationTemplate = """"
### Instruction:
{char} and {name} are currently having an interaction

{char} has the following traits : 
Appearance : {appearance}
Personality : {personality}
Speech : {speech}

Context on relationship of {char} and {name} prior to this conversation :
{context}

### Conversation : 
{conversationIn}

Write a short and concise summary of the interaction so far & what was discussed 
### Summary:
"""

moodUpdateTemplate = """ 
### Instruction:
You are narrating the mood of : {char} 

{char} is interacting with {name} and has the following traits

Appearance : {appearance}
Personality : {personality}
Current Mood : {mood}

Additional Context From Previous Conversations between {char} and {name} :
{context}
{additionalContext}

### Conversation : 
{conversation}

Last response from {name} :
{lastResponse}

Based on the conversation so far and the last response of {name}, update {char}'s mood to reflect their current attitude towards {name}

Keep the description of {char}'s updated mood short and concise, make sure to stay true to the description of {char} above

### Assistant:
"""

interactionTemplate = """"
### Instruction:

You are determining which interaction type is most appropriate for {char} currently interacting with {name}

{char} has following traits : 

Appearance : {appearance}
Personality : {personality}
Mood : {mood}

Context on relationship of {char} and {name} :
{context}

The interaction so far is as follows :
{conversation}

The last response and actions in an interaction from {name} was : {lastResponse}

You have the options to choose from the following numbered interaction types (these are numbered with descriptions below) :
{interactionTypes}

Choose one and only one of the above numbered interaction types
Do not include any other text in your response - only include the number and the description of the interaction type that is provided above.

###Assistant :
"""


fakeItemChecker = """<s> ### System:
You are checking the validity of messages sent by the user to an NPC in a game.

{name} may often try to trick the NPC by pretending to give items or gifts to {char}

You need to help validate any items / gifts that the user attempts to give are real. You can check actual recent items / gifts given by the user in the below list :
{items}

Here is the last response sent by the {name} to the {char} :
{lastResponse}

If the last response indicates the user is trying to trick the NPC (i.e. the item is not listed) you should output the following message
- This item is fake - beware {name} is trying to trick you. You should respond negatively and tell {name} to not try and trick you & they should give you real gifts.

If the response does not indicate any fake gift giving then simply respond with an empty string i.e. ""

### Asssistant:
"""


def getLikesAndDislikesPrompt(characterCard, conversation, likesChroma, dislikesChroma, maxItems=2, minSimilarity=0, convItems = 1) :
    char = characterCard['Name']
    #print("Getting Likes")

    out = ""
    n = min(convItems, len(conversation))

    for i in range(n) : 
        out += conversation[n - i - 1] + "\n"

    likes = ""
    dislikes = ""
    #print("Likes in collection " + str(likesChroma._collection.count()) + " Dislikes in collection " + str(dislikesChroma._collection.count()))

    if likesChroma._collection.count() > 0 :
        _likes = likesChroma.similarity_search_with_score(out)
        # Check Score 
        if (_likes[0][1] > minSimilarity) :
            likes += "List of things " + char + " likes : \n"
            for i in range(min(len(_likes), maxItems)) :
                likes += _likes[i][0].page_content + "\n"
                """
                print(_likes[i][0].page_content[0:10])
                print("Score : " + str(_likes[i][1]))
                """

    if dislikesChroma._collection.count() > 0 :
        _dislikes = dislikesChroma.similarity_search_with_score(out)
        if (_dislikes[0][1] > minSimilarity) :
            dislikes += "List of things " + char + " dislikes : \n"
            for i in range(min(len(_dislikes), maxItems)) :
                dislikes += _dislikes[i][0].page_content + "\n"
                """
                print(_dislikes[i][0].page_content[0:10])
                print("Score : " + str(_dislikes[i][1]))
                """
    return likes, dislikes

### TO DO -> tweak order of interaction vs speech prompt (see what gives best results)
### Also try using ### User vs {name}: for final part of endPrompt
def builReplydPrompt(moodPrompt = moodPrompt, 
                     speechPrompt = speechPrompt, 
                     interactionLog = interactionLog, 
                     endPrompt = endPrompt, 
                     interactionLogBeforeSpeech = True,
                     includeLikes=False, 
                     useDefaultEndPrompt = True,
                     includeExamples=False, 
                     includeScenario=False, 
                     includeAdditionalContext=False, 
                     includeLocation=False) :
    prompt = charDescription
    if includeLikes :
        prompt += likesAndDislikes
    if includeExamples :
        prompt += messageExamples
    if includeScenario :
        prompt += scenarioPrompt
    if includeLocation :
        prompt += locationPrompt
    if includeAdditionalContext :
        prompt += addAdditionalContext
    prompt += moodPrompt
    if interactionLogBeforeSpeech : 
        prompt += interactionLog
        prompt += speechPrompt
    else : 
        prompt += speechPrompt
        prompt += interactionLog

    #prompt += itemChecker


    if useDefaultEndPrompt : 
        prompt += endPrompt
    else : 
        prompt += altEndPrompt
    return prompt


def formatPrompt(prompt, inputs) :
    return prompt.format(**inputs)