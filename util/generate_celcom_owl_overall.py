import pickle
import query

from rdflib.graph import Graph
from rdflib.namespace import Namespace
from argparse import ArgumentParser
from pyfiglet import print_figlet

celcom = Namespace("http://www.celcom.com.my/ontology#")

g = Graph()
g.parse("../resource/celcom_protege.owl")

datatypes = []
objects = []
individuals = []
classes = []

for subject, predicate, obj in g:
    try:
        subject_clean = subject.split("#")[1]
        if "DatatypeProperty" in obj:
            if subject_clean not in datatypes:
                datatypes.append(subject_clean)
        elif "ObjectProperty" in obj:
            if subject_clean not in objects:
                objects.append(subject_clean)
        elif "NamedIndividual" in obj:
            if subject_clean not in individuals:
                individuals.append(subject_clean)
        elif "Class" in obj:
            if subject_clean not in classes:
                classes.append(subject_clean)
    except IndexError as e:
        # print("Index Error: ", e)
        # print(subject, predicate, obj)
        pass

def Parser():
    parser = ArgumentParser(description=print_figlet("COG", "doom"))
    parser.add_argument("-o",
                        "--output",
                        help="pickle file name that generate",
                        required=True)
    parser.add_argument("-d",
                        "--datatype",
                        help="use datatype property list to create pickle",
                        action="store_true")
    parser.add_argument("-b",
                        "--object",
                        help="use object property list to create pickle",
                        action="store_true")
    parser.add_argument("-n",
                        "--name",
                        help="use named individuals list to create pickle",
                        action="store_true")
    parser.add_argument("-c",
                        "--class",
                        help="use class list to create pickle",
                        action="store_true",
                        dest="class_rep")
    parser.add_argument("--combine",
                        help="use one of the combination to create pickle file",
                        choices=["name_predicate", "class_predicate"])
    return parser

def generate_pickle(filename, type):
    data = []
    if type == "datatypeProperty":
        data = datatypes
    elif type == "objectProperty":
        data = objects
    elif type == "namedIndividual":
        data = individuals
    elif type == "class":
        data = classes
    elif type == "name_predicate":
        for individual in individuals:
            predicates = query.search_predicate(individual)
            if not predicates:
                pass
            else:
                for predicate in predicates:
                    data.append(individual + "_" + str(predicate))
    elif type == "class_predicate":
        for c in classes:
            predicates = query.search_predicate(c)
            if not predicates:
                pass
            else:
                for predicate in predicates:
                    data.append(c + "_" + str(predicate))
    if not data:
        raise ValueError("data is empty")
    else:
        print(data)
        pickle.dump(data, open(filename + ".pickle", "wb"))

if __name__ == "__main__":
    parser = Parser()
    args = parser.parse_args()
    type = ""
    if args.datatype:
        type = "datatypeProperty"
    elif args.object:
        type = "objectProperty"
    elif args.name:
        type = "namedIndividual"
    elif args.class_rep:
        type = "class"
    else:
        type = args.combine
    if type == "":
        print("Please provide one of the ['-c', '-d', '-b', '-n', '--combine']")
    else:
        generate_pickle(args.output, type)
