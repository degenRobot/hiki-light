from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

localEmbedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
openAiEmbedding = OpenAIEmbeddings(model="text-embedding-ada-002")

togetherEmbedding = "'togethercomputer/m2-bert-80M-8k-retrieval'"

useOpenAIEmbedding = False

if useOpenAIEmbedding :
    embedding = openAiEmbedding
else :
    embedding = localEmbedding

localModel = "tinyllama"
solar10b = "hazelnutcloud/solar-10.7b-instruct-uncensored"
miq70b = "spuuntries/miqumaid-v1-70b-gguf:a96238fcd221a71cedbaf76b254030f16575146c3bc59344ec7fc923e13deb31"
mythoMax =  "smoosh-sh/mythomax-l2-13b-gptq:6eff74ceed40afe8e8910e2eaa050c0889a586e2f2a7dc6fa68a4a0cba5c2708"
bagel = "hazelnutcloud/bagelmisterytour-v2-8x7b:e4eda504fbe4ef51d10aa27c422e54481c5ff218fd2cd96112ed98a0b76f236e"

solarDeploy = "hikikomori-haven/solar-uncensored"
bagelDeploy = "hikikomori-haven/bagelmisterytour-v2-8x7b"


maxConervationLength = 500 
summaryPercent = 0.6 # what percent of the conversation to strip out & summarise mid conversation

maxTokensOut = 300 # max tokens to generate from the model

configuration = {
    "localModel" : localModel,
    "replicateModel" : solarDeploy,
    "replicateDeployment": solarDeploy,
    "maxConervationLength" : maxConervationLength,
    "summaryPercent" : summaryPercent,
    "maxTokensOut" : maxTokensOut,
    "useOllama" : False,
    "embedding" : embedding,
    "enableLogging" : False,
}