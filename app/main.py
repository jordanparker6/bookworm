from fastapi import FastAPI
from app.ie.entity_linking import Wikifier, DBPedia
from app.ie.relationship_extraction import CoreNLPOpenIE



wiki = Wikifier("tearikqenfaaxnqpvksupwjjfpofvh")
#dbpedia = DBPedia()
openie = CoreNLPOpenIE()

text = r"""
Salesforce is experiencing a major outage to its cloud services due to a domain name system (DNS) issue, with no estimate of restoration available yet.

Multiple Salesforce services are impacted, the company said, including the core customer relationship management (CRM) platform, and its marketing, commerce, government and experience cloud services.

Customers attempting to log in were greeted with a "maintenance" page'
"""

app = FastAPI()

@app.get("/relationship_extraction")
async def root():
    doc = openie(text)
    print(doc)
    return {"message": "Hello World"}

#print(wiki(text))
#dbpedia(text)