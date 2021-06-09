import spacy
#import neuralcoref      https://github.com/huggingface/neuralcoref awaiting for space 3.0 compatability


nlp = spacy.load('en_core_web_trf')
nlp.add_pipe('coreferee')

def resolve(text: str):
    doc = nlp(text)
    doc._.coref_chains.print()