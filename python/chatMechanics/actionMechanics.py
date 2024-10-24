import random
from chatMechanics.actions import actions, items, physicalActions

from helpers import dropdown_selection

def giveItem(affection = 0, likes = [], dislikes = []) : 
    # in future should be based on what player has in inventory
    availableItems = items.keys()
    # choose item 
    _item = dropdown_selection(availableItems)
    desc = items[_item]["description"]
    # Check if item is in NPC's like / dislike list 
    if _item in likes : 
        outcome = items[_item]["positiveOutcome"]
        return item["message"], outcome, desc

    if _item in dislikes :
        outcome = items[_item]["negativeOutcome"]
        return item["message"], outcome, desc
    

    # get item details 
    item = items[_item]
    diceRoll = random.random()

    requiredP = item["positiveOutcome"]["probability"] + item["positiveOutcome"]["probabilityMod"]*affection

    if diceRoll < requiredP :
        outcome = item["positiveOutcome"]
    else : 
        outcome = item["negativeOutcome"]

    return item["message"], outcome, desc

def physicalAction(affection = 0, likes = [], dislikes = []) : 
    availableActions = physicalActions.keys()
    # choose item
    _action = dropdown_selection(availableActions)

    desc = physicalActions[_action]["description"]

    # Check if item is in NPC's like / dislike list 
    if _action in likes : 
        outcome = physicalActions[_action]["positiveOutcome"]
        return physicalActions["message"], outcome, desc
    if _action in dislikes :
        outcome = physicalActions[_action]["negativeOutcome"]
        return physicalActions["message"], outcome, desc

    action = physicalActions[_action]
    diceRoll = random.random()
    requiredP = action["positiveOutcome"]["probability"] + action["positiveOutcome"]["probabilityMod"]*affection



    if diceRoll < requiredP :
        outcome = action["positiveOutcome"]
    else :
        outcome = action["negativeOutcome"]
    
    return action["message"], outcome, desc



def takeAction() : 
    possibleActions = actions.keys()

    action = dropdown_selection(possibleActions)

    if action == "Give Item" :
        message, outcome, desc = giveItem()
    if action == "Physical Action" :
        message, outcome, desc = physicalAction()
    
    return action, message, outcome, desc


