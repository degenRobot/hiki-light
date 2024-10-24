import json
import os.path
import sqlite3

from characters.characterGen import genCharacters, writeAllTraitsToDb
from chatMechanics.interactions import interactionDict

from config import configuration
from scraping.scraper import scrapeTopics, topics
from scraping.processDocs import processDocs

from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
import chromadb

from server.db import init_db

# Scrape topics and write to DB
toProcessDocs = False

persistent_client = chromadb.PersistentClient()


def writeInteractionTypesToDb():
    interactionTypes = list(interactionDict.keys())

    n = len(interactionTypes)
    collection_name = "interactionTypes"

    try:
        persistent_client.get_collection("interactionTypes")
    except ValueError:
        return

    interactionTypeChroma = Chroma(
        client=persistent_client,
        collection_name="interactionTypes",
        embedding_function=configuration["embedding"],
    )

    for i in range(n):
        # collection.add(ids=[str(i)], documents=[interactionTypes[i]])
        doc = Document(page_content=interactionTypes[i])
        interactionTypeChroma.add_documents([doc], ids=[str(i)])


def setup(toProcessNews=False, toProcessDocs=False):
    file = "characters.json"
    if os.path.isfile(file):
        print("Characters already exist")
        with open(file, "r") as fp:
            newCharacters = json.load(fp)
    else:
        newCharacters, charList = genCharacters()

    writeAllTraitsToDb(newCharacters, persistent_client, configuration["embedding"])

    if toProcessNews:
        scrapeTopics(
            configuration["embedding"],
            topics=topics,
            useNews=True,
            persist_directory="chroma",
        )
    if toProcessDocs:
        processDocs(
            configuration["embedding"], loadDir="./docs", persist_directory="chroma"
        )

    writeInteractionTypesToDb()

    con = sqlite3.connect("aiwaifus.sqlite")

    init_db(con)
