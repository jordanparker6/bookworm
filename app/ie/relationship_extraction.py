import stanza
import os
from stanza.server import CoreNLPClient

stanza.install_corenlp()

class CoreNLPOpenIE:
    def __init__(self):
        self.annotators = ["openie"]

    def __call__(self, text):
        with CoreNLPClient(annotators=self.annotators, be_quiet=False) as client:
            doc = client.annotate(text)
            for sentence in ann.sentence:
                for triple in sentence.openieTriple:
                    print(triple)
        return doc


"""
# Import from generic model and tokenizer classes
from transformers import AutoModel, AutoTokenizer

# Define the model name in transformers repository
model_name = "DAIR/OpenIE-6"

# Pytorch model and tokenizer
model = AutoModel.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Get input tokens and apply to the model
inputs = tokenizer("Hello world!", return_tensors="pt")
outputs = model(**inputs
"""