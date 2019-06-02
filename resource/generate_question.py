#! /usr/bin/python
import json

from os.path import exists

if __name__ == "__main__":
    # check if the question.json exist
    # if exist, load the data
    # else create a new question.json
    questions = []
    if exists("questions.json"):
        print("Loading questions from questions.json")
        with open("questions.json", "r") as f:
            questions = json.load(f)
        print("Finish loading\n")
    no_question = int(input("Enter the number of question you want to generate: "))
    count = 0
    while count < no_question:
        print("--> Question " + str(count+1))
        question = input("Question: ")
        choices = []
        no_choice = int(input("Enter number of choice: "))
        for i in range(no_choice):
            choice = input("Choice " + str(i+1) + ": ")
            choices.append(choice)
        answer = int(input("Enter the position of answer(1-" + str(no_choice) + "): "))
        answer = answer - 1
        question_dict = {"question": question, "choices": choices, "answer": answer}
        questions.append(question_dict)
        count += 1
    print()
    print("Saving to questions.json")
    with open("questions.json", "w") as f:
        json.dump(questions, f)
    print("Done saving")
    print("Total question: " + str(len(questions)))
