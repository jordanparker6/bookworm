import spacy
import pytest
from relationship_extraction import extract_relations

nlp = spacy.load("en_core_web_sm")

def test_rel_ext_case_1():
    text = """
        Amundsen is a data discovery and metadata engine for improving the productivity of data analysts, data scientists and engineers when interacting with data.
    """
    rel = list(extract_relations(nlp(text.strip()), verbose=False))
    assert rel == [
        ("Amundsen", "is", "data discovery"), 
        ("Amundsen", "is", "metadata engine")
    ]

def test_rel_ext_case_1_verbose():
    text = """
        Amundsen is a data discovery and metadata engine for improving the productivity of data analysts, data scientists and engineers when interacting with data.
    """
    rel = list(extract_relations(nlp(text.strip()), verbose=True))
    assert rel == [
        (
            {'name': 'Amundsen', 'dep': 'nsubj', 'pos': 'PROPN'}, 
            {'name': 'is', 'full_name': 'is', 'dep': 'ROOT', 'pos': 'AUX'}, 
            {'name': 'data discovery', 'dep': 'attr', 'pos': 'NOUN'}
        ),
        (
            {'name': 'Amundsen', 'dep': 'nsubj', 'pos': 'PROPN'}, 
            {'name': 'is', 'full_name': 'is', 'dep': 'ROOT', 'pos': 'AUX'}, 
            {'name': 'metadata engine', 'dep': 'attr', 'pos': 'NOUN'}
        )
    ]

def test_rel_ext_case_2():
    text = """
        Cypress has been made specifically for developers and QA engineers, to help them get more done.
    """
    rel = list(extract_relations(nlp(text.strip()), verbose=False))
    print(rel)
    assert rel == [
        ("Cypress", "made for", "developers"), 
        ("Cypress", "made for", "QA engineers"),
    ]


def test_rel_ext_case_2_verbose():
    text = """
        Cypress has been made specifically for developers and QA engineers, to help them get more done.
    """
    rel = list(extract_relations(nlp(text.strip()), verbose=True))
    print(rel)
    assert rel == [
        (
            {'name': 'Cypress', 'dep': 'nsubjpass', 'pos': 'PROPN'}, 
            {'name': 'made for', 'full_name': 'has been made for', 'dep': 'ROOT', 'pos': 'VERB'}, 
            {'name': 'developers', 'dep': 'pobj', 'pos': 'NOUN'}
        ),
        (
            {'name': 'Cypress', 'dep': 'nsubjpass', 'pos': 'PROPN'},
            {'name': 'made for', 'full_name': 'has been made for', 'dep': 'ROOT', 'pos': 'VERB'},
            {'name': 'QA engineers', 'dep': 'pobj', 'pos': 'NOUN'}
        )
    ]