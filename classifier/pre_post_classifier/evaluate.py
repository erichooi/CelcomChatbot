import pickle
import jsonlines
import pandas

from sklearn import model_selection
from sklearn.metrics import confusion_matrix, classification_report

model = pickle.load(open("model.pickle", "rb"))
X_test = []
y_test = []
with jsonlines.open("data/test.jsonl", "r") as reader:
    for line in reader:
        X_test.append(line["question"])
        y_test.append(line["label"])

cv = 5

print("Classification Accuracy")
print("------------------------------")
result = model_selection.cross_val_score(model, X_test, y_test, cv=cv, scoring='accuracy')
print("Accuracy: %.3f (%.3f)" %(result.mean(), result.std()))
print()
print("Logarithmic Loss")
print("------------------------------")
result = model_selection.cross_val_score(model, X_test, y_test, cv=cv, scoring="neg_log_loss")
print("Logloss: %.3f (%.3f)" %(result.mean(), result.std()))
print()
#print("Area Under ROC Curve")
#print("------------------------------")
#result = model_selection.cross_val_score(model, X_test, y_test, cv=cv, scoring="roc_auc")
#print("AUC: %.3f (%.3f)" %(result.mean(), result.std()))
#print()
print("Confusion Matrix")
print("------------------------------")
predicted = model.predict(X_test)
matrix = confusion_matrix(y_test, predicted)
print(matrix)
print()
print("Classification Report")
print("------------------------------")
report = classification_report(y_test, predicted)
print(report)
