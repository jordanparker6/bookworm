import urllib.parse, urllib.request
import json
import spacy

#nlp.add_pipe("entityLinker", last=True) -- accuracy was poor, good API however

ENTITY_TYPES = ["human", "person", "company", "enterprise", "business", "geographic region",
                "human settlement", "geographic entity", "territorial entity type", "organization"]

class Wikifier:
    """
    A class to perform Entity Linking with the Wikidata Knowledge Graph.
    Leverages the Wikifier API
    """
    def __init__(self, api_key, threshold=0.8, config={}):
        self.key = api_key
        self.url = "http://www.wikifier.org/annotate-article"
        self.config = {
            "nTopDfValuesToIgnore": "100", 
            "nWordsToIgnoreFromList": "100",
            "wikiDataClasses": "true", 
            "wikiDataClassIds": "false",
            "support": "true", 
            "ranges": "false", 
            "minLinkFrequency": "2",
            "includeCosines": "false", 
            "maxMentionEntropy": "3",
            "lang": "en",
            "pageRankSqThreshold": "%g" %threshold,
            **config
        }
    
    def __call__(self, text):
        """Function that fetches entity linking results from wikifier.com API"""
        data = urllib.parse.urlencode({ "text": text, "userKey": self.key, **self.config })
        req = urllib.request.Request(self.url, data=data.encode("utf8"), method="POST")
        with urllib.request.urlopen(req, timeout=60) as f:
            response = f.read()
            response = json.loads(response.decode("utf8"))
        # Output the annotations.
        result = []
        for annotation in response["annotations"]:
            data = self._transform(text, annotation)
            if data:
                result.append(data)
        return result

    def _transform(self, text, annotation, entity_types=ENTITY_TYPES):
        if ('wikiDataClasses' in annotation) and (any([el['enLabel'] in entity_types for el in annotation['wikiDataClasses']])):
            # Specify entity label
            if any([el['enLabel'] in ["human", "person"] for el in annotation['wikiDataClasses']]):
                label = 'Person'
            elif any([el['enLabel'] in ["company", "enterprise", "business", "organization"] for el in annotation['wikiDataClasses']]):
                label = 'Organization'
            elif any([el['enLabel'] in ["geographic region", "human settlement", "geographic entity", "territorial entity type"] for el in annotation['wikiDataClasses']]):
                label = 'Location'
            else:
                label = None

            return {
                    'title': annotation['title'], 
                    'wikiId': annotation['wikiDataItemId'],
                    "text": [text[el['chFrom']:el['chTo'] + 1] for el in annotation['support']], 
                    'label': label,
                    'characters': [(el['chFrom'], el['chTo']) for el in annotation['support']],
                    'confidence': [el['prbConfidence'] for el in annotation['support']],
                    'pageRank': [el['pageRank'] for el in annotation['support']],
                    'entropy': [el['entropy'] for el in annotation['support']],
                    'dbpedia_url': annotation["dbPediaIri"],
                    'wiki_url': annotation["secUrl"]
                }

class DBPedia:
    """
    A class to perform Entity Linking with the DBPedia Knowledge Graph.
    Leverages a pretrained spacy model.
    """
    def __init__(self):
        self.nlp = spacy.load('en_core_web_trf')
        self.nlp.add_pipe('dbpedia_spotlight', config={'language_code': 'en', 'confidence': 0.75 })

    def __call__(self, text):
        doc = self.nlp(text)
        for ent in doc.ents:
            print({
                "id": ent.kb_id,
                "text": ent.text,
                "label": ent.label_,
                "dbpedia": ent._.dbpedia_raw_result,
            })
        