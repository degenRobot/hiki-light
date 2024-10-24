import asyncio
import datetime
import json
import sqlite3
import time
from typing import Any
import chromadb
from characters.playerOptions import getMood
from chat import (
    endOfInteractionSummary,
    genChatInputs,
    getChatPrompt,
    getConext,
    getInteractionTimeContextStr,
    manageConversationLength,
)
from helpers import createDoc
from server.types import ConvoMessage
from .db import get_conversation, get_summary, set_conversation, set_summary
from config import configuration
from chatMechanics.interactions import interactionDict
from pydantic import BaseModel
import replicate


async def gen_reply(
    character_card: dict[str, Any],
    user_name: str,
    user_message: str,
    user_address: str,
    con: sqlite3.Connection,
):
    char_name = character_card["Name"]
    char_id = character_card["id"]

    chroma_client = chromadb.PersistentClient()
    interactionChroma = chroma_client.get_or_create_collection(
        name="Interactions_" + char_id + "_" + user_address,
    )
    likesChroma = chroma_client.get_or_create_collection(
        name="Likes_" + char_id,
    )
    dislikesChroma = chroma_client.get_or_create_collection(
        name="Dislikes_" + char_id,
    )

    timestamp = time.time_ns() // 1_000_000  # milliseconds

    print("fetching conversation from db")

    prev_summary = get_summary(con=con, address=user_address, char_id=char_id)
    convo_messages = get_conversation(
        con=con,
        address=user_address,
        char_id=char_id,
        cutoff=prev_summary[1] if prev_summary else None,
    )
    user_convo_message = ConvoMessage(
        sender="user", message=user_message, timestamp=timestamp
    )
    convo_messages.append(
        user_convo_message,
    )

    conv_str_list = [message.format() + "\n" for message in convo_messages]
    conv_str = (prev_summary[0] + "\n") if prev_summary else "" + "".join(conv_str_list)

    chatInputs = genChatInputs(
        char=char_name,
        characterCard=character_card,
        conversation=conv_str,
        userName=user_name,
        response=user_message,
        placeInput="",
    )

    print("getting context")
    contextExists, context = getConext(
        char=char_name, name=user_name, interactionChroma=interactionChroma
    )
    interactionTimeContext, _ = getInteractionTimeContextStr(
        char=char_name, name=user_name, interactionChroma=interactionChroma
    )

    if contextExists:
        chatInputs["context"] = context
        chatInputs["context"] += interactionTimeContext
    chatInputs["lastResponse"] = user_message
    chatInputs["likes"], chatInputs["dislikes"] = get_likes_and_dislikes_prompt(
        characterCard=character_card,
        conversation=chatInputs["conversation"],
        likesChroma=likesChroma,
        dislikesChroma=dislikesChroma,
    )
    chatInputs["mood"] = getMood(character_card, chatInputs)
    _interactionData = interactionDict[
        "chat used to generate a response when character is having a normal conversation with another character"
    ]
    _interactionData["includeLikes"] = True
    _chatPrompt = getChatPrompt(_interactionData, chatInputs, character_card)
    print("calling replicate: " + _chatPrompt)

    full_output = ""

    deployment = replicate.deployments.get(configuration["replicateDeployment"])
    prediction = deployment.predictions.create(
        input={
            "prompt": _chatPrompt,
            "max_tokens": configuration["maxTokensOut"],
        },
        stream=True,
    )
    
    await asyncio.sleep(0.1)
    stream = prediction.async_output_iterator()
    async for item in stream:
        full_output += item
        yield {"data": item}
        await asyncio.sleep(0.1)

    print(full_output)

    ai_convo_message = ConvoMessage(
        sender="ai", message=full_output, timestamp=timestamp
    )
    convo_messages.append(ai_convo_message)
    conv_str += ai_convo_message.format() + "\n"

    rollup = await manageConversationLength(chatInputs=chatInputs, messages=convo_messages)

    if rollup:
        set_summary(
            con=con,
            address=user_address,
            char_id=char_id,
            summary=rollup[0],
            convo_cutoff=rollup[1],
        )
    set_conversation(
        con=con,
        address=user_address,
        char_id=char_id,
        messages=[user_convo_message, ai_convo_message],
    )

    chatInputs["conversation"], chatInputs["output"] = conv_str, full_output

    summary: str = await endOfInteractionSummary(chatInputs=chatInputs)
    interaction_id = interactionChroma.count() + 1
    doc = createDoc(out=summary, char=char_name, name=user_name)
    interactionChroma.add(
        ids=[str(interaction_id)],
        documents=[doc.page_content],
        metadatas=[{"time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}],
    )


def get_character(character_id: str) -> dict[str, Any] | None:
    with open("characters.json", "r") as fp:
        characters = json.load(fp)

    chars = characters.keys()
    for char in chars:
        if characters[char]["id"] == character_id:
            return characters[char]
    return


def get_likes_and_dislikes_prompt(
    characterCard: dict[str, Any],
    conversation: str,
    likesChroma: chromadb.Collection,
    dislikesChroma: chromadb.Collection,
    maxItems=2,
    minSimilarity=0,
    convItems=1,
) -> tuple[str, str]:
    char = characterCard["Name"]
    print("Getting Likes")

    out = ""
    n = min(convItems, len(conversation))

    for i in range(n):
        out += conversation[n - i - 1] + "\n"  # why the reverse?

    likes = ""
    dislikes = ""
    print(
        "Likes in collection "
        + str(likesChroma.count())
        + " Dislikes in collection "
        + str(dislikesChroma.count())
    )

    if likesChroma.count() > 0:
        _likes = likesChroma.query(query_texts=[out])
        # Check Score
        if _likes["documents"] is not None:
            assert _likes["distances"] is not None
            if _likes["distances"][0][0] > minSimilarity:
                likes += "List of things " + char + " likes : \n"
                for i in range(min(len(_likes["documents"][0]), maxItems)):
                    like = _likes["documents"][0][i]
                    likes += like + "\n"
                    print(like[0:10])
                    print("Score : " + str(_likes["distances"][0][i]))

    if dislikesChroma.count() > 0:
        _dislikes = dislikesChroma.query(query_texts=[out])
        if _dislikes["documents"] is not None:
            assert _dislikes["distances"] is not None
            if _dislikes["distances"][0][0] > minSimilarity:
                dislikes += "List of things " + char + " dislikes : \n"
                for i in range(min(len(_dislikes["documents"][0]), maxItems)):
                    dislike = _dislikes["documents"][0][i]
                    dislikes += dislike + "\n"
                    print(dislike[0:10])
                    print("Score : " + str(_dislikes["distances"][0][i]))
    return likes, dislikes


class UserMessage(BaseModel):
    message: str
