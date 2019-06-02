import pickle
from termcolor import colored, cprint

model = pickle.load(open("model.pickle", "rb"))

while True:
    question = input("Enter the question: ")
    confidence = model.predict_proba([question])
    postpaid_confidence = confidence[0][0]
    prepaid_confidence = confidence[0][1]
    print("postpaid confidence: " + colored(str(postpaid_confidence), "green"))
    print("prepaid confidence: " + colored(str(prepaid_confidence), "green"))
    if prepaid_confidence > 0.7:
        label = "prepaid"
    elif postpaid_confidence > 0.7:
        label = "postpaid"
    else:
        label = "Unknown"
    cprint(label, "blue")
