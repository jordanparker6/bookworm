import spacy
from spacy.parts_of_speech import CONJ, DET, NOUN, VERB, AUX
from spacy.tokens.span import Span as SpacySpan
from spacy import displacy
import itertools

OBJECT_DEPS = {'attr', 'dobj', 'dative', 'oprd' }
SUBJECT_DEPS = {'agent', 'csubj', 'csubjpass', 'expl', 'nsubj', 'nsubjpass' }
AUX_DEPS = {'aux', 'auxpass', 'neg'}
WH_WORDS = {"WP", "WP$", "WRB"}

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

def get_aux(sent: SpacySpan):
    """Return aux tokens that are a ROOT dependency."""
    return [tok for tok in sent if tok.pos == AUX and tok.dep_ == "ROOT"]

def get_conjuncts(tok):
    """Return conjunct dependents of the leftmost conjunct in a coordinated phrase, e.g. "Burton, [Dan], and [Josh] ..."."""
    return [right for right in tok.rights if right.dep_ == 'conj']

def get_subjects(verb):
    """Return all subjects of a verb according to the dependency parse."""
    subjs = [tok for tok in verb.lefts if tok.dep_ in SUBJECT_DEPS]
    subjs.extend(tok for subj in subjs for tok in get_conjuncts(subj))
    return subjs

def get_objects(verb):
    """Return all objects of a verb according to the dependency parse, including open clausal complements."""
    objs = [tok for tok in verb.rights if tok.dep_ in OBJECT_DEPS]
    objs.extend(tok for tok in verb.rights if tok.dep_ == 'xcomp') # get open clausal complements (xcomp)
    objs.extend(tok for obj in objs for tok in get_conjuncts(obj))
    return objs

def get_span_for_compound_noun(noun):
    """Return document indexes spanning all (adjacent) tokensin a compound noun."""
    min_i = noun.i - sum(1 for _ in itertools.takewhile(lambda x: x.dep_ == 'compound', reversed(list(noun.lefts))))
    return (min_i, noun.i)

####################################
## Relationship Extraction  ########
####################################

def extract_relations(doc):
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
        
        verbs = get_main_verbs(sent) + get_aux(sent)

        for verb in verbs:
            subjs = get_subjects(verb)
            if not subjs:
                continue
            objs = get_objects(verb)
            if not objs:
                continue

            verb_span = get_span_for_verb_auxiliaries(verb)
            verb = sent[verb_span[0] - start_i: verb_span[1] - start_i + 1]
            
            for subj in subjs:
                subj = sent[get_span_for_compound_noun(subj)[0] - start_i: subj.i - start_i + 1]
                for obj in objs:
                    if obj.pos == NOUN:
                        span = get_span_for_compound_noun(obj)
                    elif obj.pos == VERB:
                        span = get_span_for_verb_auxiliaries(obj)
                    else:
                        span = (obj.i, obj.i)
                    obj = sent[span[0] - start_i: span[1] - start_i + 1]

                    yield [subj, verb, obj]


if __name__ == "__main__":
    text = """
        Amundsen is a data discovery and metadata engine for improving the productivity of data analysts, data scientists and engineers when interacting with data.
        It does that today by indexing data resources (tables, dashboards, streams, etc.) and powering a page-rank style search based on usage patterns (e.g. highly queried tables show up earlier than less queried tables).
        Think of it as Google search for data. The project is named after Norwegian explorer Roald Amundsen, the first person to discover the South Pole.
    """
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text.strip())
    displacy.serve(doc, style="dep")
    for x in extract_relations(doc):
        print(f"tripple: {x}")

