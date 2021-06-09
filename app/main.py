import os
import spacy
from spacy import displacy
from fastapi import FastAPI
from app.entity_linking import Wikifier, DBPedia
from app.relationship_extraction import extract_relations

WIKIFIER_API_KEY: str = os.getenv("WIKIFIER_API_KEY", "xxxxx")

nlp = spacy.load("en_core_web_sm")
wiki = Wikifier()
#dbpedia = DBPedia()

text = r"""
Salesforce is experiencing a major outage to its cloud services due to a domain name system (DNS) issue, with no estimate of restoration available yet.

Multiple Salesforce services are impacted, the company said, including the core customer relationship management (CRM) platform, and its marketing, commerce, government and experience cloud services.

Customers attempting to log in were greeted with a "maintenance" page'
"""

app = FastAPI()

@app.get("/relationship_extraction")
async def rel_extraction():
    return {"message": list(extract_relations(nlp(text.strip()))) }

@app.get("/ner")
async def ner():
    result = wiki(text.strip)
    return {"message": list(extract_relations(nlp(text.strip()))) }

@app.get("/dep_tree")
async def dep_tree():
    return displacy.render(doc = nlp(text.strip()), style="dep")

#print(wiki(text))
#dbpedia(text)