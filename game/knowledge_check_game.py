import settings
import json
import pickle

from random import choice, sample
from fbmq import Template
from time import sleep

settings.init()
g_page = settings.page

# payload design
# {turn}_{total_turn}_{user answer}_{answer}_{mark}
@g_page.callback(['\d+_\d+_\d+_\d+_\d+$'], types=['POSTBACK'])
def compare_answer(payload, event):
    sender_id = event.sender_id

    correct_messages = [
        "Good job 😆",
        "Correct 👍",
        "You're on 🔥",
        "Nice 😁",
        "Well done"
    ]
    wrong_message = [
        "Try harder 🙈",
        "Nice try, you can do it better 💪",
        "Wrong, but good try!!"
    ]
    payload = payload.split("_")
    turn = int(payload[0])
    total_turn = int(payload[1])
    user_answer = int(payload[2])
    answer = int(payload[3])
    mark = int(payload[4])
    if user_answer == answer:
        g_page.send(sender_id, choice(correct_messages))
        g_page.typing_on(sender_id)
        sleep(2)
        mark += 1
    else:
        g_page.send(sender_id, choice(wrong_message))
        g_page.typing_on(sender_id)
        sleep(2)
    turn += 1
    if turn < total_turn:
        challenge(turn, total_turn, mark, sender_id)
    else:
        g_page.typing_on(sender_id)
        sleep(0.5)
        g_page.send(sender_id, "You had earned " + str(mark) + " mark.")
        g_page.typing_on(sender_id)
        sleep(0.5)
        if mark == total_turn:
            g_page.send(sender_id, "Woah 😱 You are unbelievable !!!")
            g_page.typing_on(sender_id)
            sleep(1)
            g_page.send(sender_id, "Go to challenge harder level. See you in the next level.")
        else:
            g_page.send(sender_id, "You can do better next time.")
            g_page.typing_on(sender_id)
            sleep(1)
            g_page.send(sender_id, "See you around soon !!")

def challenge(turn, total_turn, mark, sender_id):
    if turn == 0:
        with open("resource/questions.json") as f:
            questions = json.load(f)
    else:
        with open("questions.pickle", 'rb') as pinfile:
            questions = pickle.load(pinfile)
    random_question = sample(questions, 1)

    question = random_question[0]["question"]
    choices = random_question[0]["choices"]
    answer = random_question[0]["answer"]
    print("question: ", question)
    for i in questions:
        if i["question"] == question:
            questions.remove(i)
    with open("questions.pickle", "wb") as poutfile:
        pickle.dump(questions, poutfile)
    print("questions: ", questions)
    buttons = []
    for i in range(len(choices)):
        buttons.append(
            Template.ButtonPostBack(
                choices[i],
                str(turn) + "_" + str(total_turn) + "_" + str(i) + "_" + str(answer) + "_" + str(mark)
            )
        )
    g_page.send(sender_id, Template.Buttons(question, buttons))
