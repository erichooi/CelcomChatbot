import jsonlines
import pickle

from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
from nltk.corpus import stopwords
from termcolor import cprint


stopword = stopwords.words("english")
X_train = []
y_train = []
X_test = []
y_test = []

with jsonlines.open("data/train.jsonl", "r") as reader:
    for line in reader:
        X_train.append(line["question"])
        y_train.append(line["label"])

with jsonlines.open("data/test.jsonl", "r") as reader:
    for line in reader:
        X_test.append(line["question"])
        y_test.append(line["label"])

text_clf = Pipeline([
    ("vectorizer", TfidfVectorizer(stop_words=stopword)),
    ("classifier", MultinomialNB())
])

text_clf.fit(X_train, y_train)
predicted = text_clf.predict(X_test)

cprint("Classifier", "red")
print("-------------------------------------------------------------------\n")
for i in text_clf.get_params()["steps"]:
    cprint(str(i) + "\n", "green")
cprint("Report", "red")
print("-------------------------------------------------------------------\n")
cprint(classification_report(y_test, predicted), "blue")

write_to_result = ""
create_model = ""
while True:
    write_to_result = input("Do you want to record the result? (yes/no) --> ")
    if write_to_result == "yes":
        with open("result.txt", "a") as f:
            f.write("\n")
            f.write("Classifier\n")
            f.write("------------\n")
            for i in text_clf.get_params()["steps"]:
                f.write(str(i) + "\n")
            f.write("\n")
            f.write("Report\n")
            f.write("------------\n")
            f.write(classification_report(y_test, predicted))
            f.write("\n")
            f.write("--------------------------------------------------------------------------------------" + "\n")
            break
    elif write_to_result == "no":
        break
    else:
        pass

while True:
    create_model = input("Do you want to export the model? (yes/no) --> ")
    if create_model == "yes":
        pickle.dump(text_clf, open("model.pickle", "wb"))
        break
    elif create_model == "no":
        break
    else:
        pass
