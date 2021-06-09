from typing import List
import spacy
from spacy.parts_of_speech import CONJ, DET, NOUN, VERB, AUX
from spacy.tokens.span import Span as SpacySpan
import itertools

OBJECT_DEPS = {'attr', 'dobj', 'dative', 'oprd', "pobj" }
SUBJECT_DEPS = {'agent', 'csubj', 'csubjpass', 'expl', 'nsubj', 'nsubjpass' }
AUX_DEPS = {'aux', 'auxpass', 'neg' }
VERB_DEPS = { "prep", "xcomp" }
WH_WORDS = {"WP", "WP$", "WRB"}

flatten = lambda t: [item for sublist in t for item in sublist]

###########################
## Utility Methods ########
###########################

def get_main_verbs(sent: SpacySpan):
    """Return the main (non-auxiliary) verbs in a sentence."""
    return [tok for tok in sent if tok.pos == VERB and tok.dep_ not in {'aux', 'auxpass'}]

def get_span_for_verb_auxiliaries(verb):
    """Return document indexes spanning all (adjacent) tokens around a verb that are auxiliary verbs or negations."""
    min_i = verb.i - sum(1 for _ in itertools.takewhile(lambda x: x.dep_ in AUX_DEPS, reversed(list(verb.lefts))))
    max_i = verb.i + sum(1 for _ in itertools.takewhile(lambda x: x.dep_ in AUX_DEPS, verb.rights))
    return (min_i, max_i)

def get_aux_deps(verb):
    """Return the sapn of all tokens around a verb that are auxiliary verbs or negations."""
    return [left for left in verb.lefts if left.dep_ in AUX_DEPS] + [verb]

def extend_main_verb(verb):
    """Returns the additional non-auxilary tokens associated with the main verb."""
    return [right for right in verb.rights if right.dep_ in VERB_DEPS]

def get_main_aux(sent: SpacySpan):
    """Return aux tokens that are a ROOT dependency."""
    return [tok for tok in sent if tok.pos == AUX and tok.dep_ == "ROOT"]

def get_conjuncts(tok):
    """Return conjunct dependents of the leftmost conjunct in a coordinated phrase, e.g. "Burton, [Dan], and [Josh] ..."."""
    return [right for right in tok.rights if right.dep_ == 'conj']

def get_conjuncts_dep(tok):
    """Returns the dependency type, with adjustment mades for conjuct tokens."""
    if tok.dep_ == "conj":
        return tok.head.dep_
    return tok.dep_

def get_subjects(verb):
    """Return all subjects of a verb according to the dependency parse."""
    subjs = [tok for tok in verb.lefts if tok.dep_ in SUBJECT_DEPS]
    subjs.extend(tok for subj in subjs for tok in get_conjuncts(subj))
    return subjs

def get_objects(verb):
    """Return all objects of a verb according to the dependency parse, including open clausal complements."""
    objs = [tok for tok in verb.rights if tok.dep_ in OBJECT_DEPS]
    #objs.extend(tok for tok in verb.rights if tok.dep_ == 'xcomp')
    objs.extend(tok for obj in objs for tok in get_conjuncts(obj))
    return objs

def get_span_for_compound_noun(noun):
    """Return document indexes spanning all (adjacent) tokensin a compound noun."""
    min_i = noun.i - sum(1 for _ in itertools.takewhile(lambda x: x.dep_ == 'compound', reversed(list(noun.lefts))))
    return (min_i, noun.i)

def spacy_list_to_string(items):
    return " ".join([str(x) for x in items])

####################################
## Relationship Extraction  ########
####################################

def extract_relations(doc, verbose=False):
    """
    Extract an ordered sequence of subject-verb-object (SVO) triples from a
    spacy-parsed doc. Note that this only works for SVO languages.
    Args:
        doc (``spacy.Doc`` or ``spacy.Span``)
    Yields:
        Tuple[``spacy.Span``, ``spacy.Span``, ``spacy.Span``]: The next 3-tuple
        of spans from ``doc`` representing a (subject, verb, object) triple,
        in order of appearance.
    """
    if isinstance(doc, SpacySpan):
        sents = [doc]
    else:  # textacy.Doc or spacy.Doc
        sents = doc.sents

    for sent in doc.sents:
        start_i = sent[0].i
        
        # The main verbs and ROOT auxiliary tokens establish the relationship
        verbs = get_main_verbs(sent) + get_main_aux(sent)

        
        for verb in verbs:
            # Append PREP dependencies to collect both direct and indirect relationships.
            verb_deps = extend_main_verb(verb)
            roots = [verb] + verb_deps

            subjs = flatten(list(map(lambda x: get_subjects(x), roots)))
            if not subjs:
                continue
            objs = flatten(list(map(lambda x: get_objects(x), roots)))
            if not objs:
                continue

            span = get_span_for_verb_auxiliaries(verb)
            full_verb = sent[span[0] - start_i: span[1] - start_i + 1]

            full_verb_deps = flatten([get_aux_deps(x) for x in verb_deps])
            verb_text = spacy_list_to_string([verb] + full_verb_deps)
            full_verb_text = spacy_list_to_string([tok for tok in full_verb] + full_verb_deps)

            for subj in subjs:
                full_subj = sent[get_span_for_compound_noun(subj)[0] - start_i: subj.i - start_i + 1]
                for obj in objs:
                    if obj.pos == NOUN:
                        span = get_span_for_compound_noun(obj)
                    elif obj.pos == VERB:
                        span = get_span_for_verb_auxiliaries(obj)
                    else:
                        span = (obj.i, obj.i)
                    full_obj = sent[span[0] - start_i: span[1] - start_i + 1]

                    full_subj = str(full_subj)
                    full_obj = str(full_obj)
                    
                    

                    if verbose:
                        yield (
                            { "name": full_subj, "dep": subj.dep_, "pos": subj.pos_ }, 
                            { "name": verb_text, "full_name": full_verb_text, "dep": verb.dep_, "pos": verb.pos_ },
                            { "name": full_obj, "dep": get_conjuncts_dep(obj), "pos": obj.pos_ }
                        )
                    else: 
                        yield (full_subj, verb_text, full_obj)

if __name__ == "__main__":
    nlp = spacy.load("en_core_web_sm")
    text = "Before the development of computing devices and machines, people had to manually collect data and impose patterns on it. Since the development of computing devices and machines, these devices can also collect data."
    doc = nlp(text.strip())
    #spacy.displacy.serve(doc, style="dep")
    for i in extract_relations(doc, verbose=False):
        print(i)
