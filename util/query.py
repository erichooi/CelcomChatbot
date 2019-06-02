import os

from rdflib.graph import Graph
from rdflib.namespace import RDFS, RDF, OWL, XSD
from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import Namespace
from rdflib.term import URIRef

celcom = Namespace("http://www.celcom.com.my/ontology#")

g = Graph()
g.parse(os.path.join(os.path.dirname(__file__), "../resource/celcom_protege.owl"))

def search_objects(subject, predicate):
    answer = []
    subject = URIRef(celcom + subject)
    rdfs = ["label", "comment", "subPropertyOf"]
    rdf = ["type"]
    if predicate in rdfs:
        q = prepareQuery('SELECT ?o WHERE { ?s namespace:%s ?o . }' % (predicate), initNs={"namespace": RDFS})
    elif predicate in rdf:
        q = prepareQuery('SELECT ?o WHERE { ?s namespace:%s ?o . }' % (predicate), initNs={"namespace": RDF})
    else:
        q = prepareQuery('SELECT ?o WHERE { ?s namespace:%s ?o . }' % (predicate), initNs={"namespace": celcom})
    for row in g.query(q, initBindings={'s': subject}):
        answer.append(row[0])
    return answer

def search_predicate(subject):
    subject = URIRef(celcom + subject)
    predicates = []
    q = prepareQuery('SELECT ?p WHERE { ?s ?p ?o . }')
    for row in g.query(q, initBindings={'s': subject}):
        predicate_clean = row[0].split("#")[1]
        if predicate_clean not in predicates:
            predicates.append(predicate_clean)
    return predicates
