import pickle
import tensorflow as tf
import string
import settings

from urllib.parse import  urlencode
from termcolor import cprint
from flask import Flask, request
from fbmq import QuickReply, Template
from time import sleep
from random import sample
from util import format_sentence, classify, query, message, connect_db
from game import knowledge_check_game

settings.init()
page = settings.page
app = Flask(__name__)
available_subjects = pickle.load(open("resource/subject.pickle", "rb"))
available_subject_predicate = pickle.load(open("resource/name_predicate.pickle", "rb"))

timestamp = 0

@app.route('/webhook', methods=['POST'])
def post_webhook():
    page.handle_webhook(request.get_data(as_text=True))
    return "ok"

# change persistent menu (deprecated)
@page.callback(['COMMAND'], types=['POSTBACK'])
def available_command(payload, event):
    sender_id = event.sender_id

    page.typing_on(sender_id)
    sleep(1)
    page.send(sender_id, "You must be 🤔 wondering what are the other 🆒 things that I can do right?")
    page.typing_on(sender_id)
    sleep(2)
    page.send(sender_id, "the command that currently available to use are \"tabot\" and \"help\". More will be available in the future")
    page.typing_on(sender_id)
    sleep(1)
    page.send(sender_id, "just text any of those command to start a fun 😊 conversation with me")

@page.handle_message
def message_handler(event):
    clf = pickle.load(open("resource/model/pre_post_model.pkl", "rb"))
    sender_id = event.sender_id
    message = event.message_text
    global timestamp

    if event.quick_reply:
        pass
    elif message.lower() == "tabot":
        quick_replies = [
            QuickReply(title="quiz", payload="GAME"),
            QuickReply(title="explore", payload="D_SEARCH"),
            QuickReply(title="ask question", payload="Q_SEARCH")
        ]
        page.send(sender_id,
                  "Hi, What would you like to do?",
                  quick_replies=quick_replies)
    # use timestamp to trace whether user had choose to ask question or just normal questioning
    elif timestamp != 0:
        question = event.message_text
        question_type = classify.predict_pre_post(clf, question, 0.7)

        tfidf = pickle.load(open("resource/model/tfidf.pkl", "rb"))
        tf_model = "resource/model/model.ckpt.meta"
        with tf.Session() as sess:
            saver = tf.train.import_meta_graph(tf_model)
            saver.restore(sess, tf.train.latest_checkpoint('resource/model/'))
            formatted_question = clean_question(question)
            formatted_question = tfidf.transform([formatted_question])
            question_location = classify.predict_web_com(sess, formatted_question, 0.75)
        # print(question_type)
        # print(question_location)
        if question_location == "community":
            base_url = "https://community.celcom.com.my/t5/forums/searchpage/tab/message?"
            params = {
                "advanced": "false",
                "allow_punctuation": "false",
                "q": question
            }
            search_url = base_url + urlencode(params)
            page.send(sender_id, Template.Generic([
                Template.GenericElement(question,
                                        item_url=search_url,
                                        buttons=[
                                            Template.ButtonWeb("Get Answer", search_url)
                                        ])
            ]))
        elif question_location == "website":
            if question_type == "prepaid":
                quick_replies = [
                    QuickReply(title="yes", payload="PREPAID_YES"),
                    QuickReply(title="no", payload="PREPAID_NO")
                ]
                page.send(sender_id,
                          "Are you asking question about prepaid plan?",
                          quick_replies=quick_replies)
            elif question_type == "postpaid":
                quick_replies = [
                    QuickReply(title="yes", payload="POSTPAID_YES"),
                    QuickReply(title="no", payload="POSTPAID_NO")
                ]
                page.send(sender_id,
                          "Are you asking question about postpaid plan?",
                          quick_replies=quick_replies)
            else:
                # format the question
                payload_question = question.replace(" ", "-")
                page.send(sender_id,
                          "😅 I do not understand the question! But I am improving every day, and hopefully I can answer this question in near future.")
                page.typing_on(sender_id)
                buttons = [
                    Template.ButtonPostBack("prepaid", "PREPAID" + "-" + payload_question),
                    Template.ButtonPostBack("postpaid", "POSTPAID" + "-" + payload_question),
                    Template.ButtonPostBack("other", "OTHER" + "-" + payload_question)
                ]
                # TODO kawkawsquad format cannot pass
                page.send(sender_id,
                          Template.Buttons("The question that you are asking, is it about prepaid plan or postpaid plan or other?",
                                           buttons))
        else:
            page.send(sender_id, "😱 cannot find any answer related to the question!")
            page.typing_on(sender_id)
            page.send(sender_id, "🤔 Maybe you can ask the question in our community")
            page.send(sender_id, Template.Generic([
                Template.GenericElement("Ask Question",
                                        subtitle="Ask New Question",
                                        item_url="https://community.celcom.com.my/",
                                        image_url="https://smpiu66958.i.lithium.com/html/assets/placeholder-banner.png",
                                        buttons=[
                                            Template.ButtonWeb("Ask question", "https://community.celcom.com.my/")
                                        ])
            ]))
        timestamp = 0
    elif message.lower() == "help":
        page.typing_on(sender_id)
        sleep(2)
        page.send(sender_id,
                  "👋 I am Tabot, a 🤖 to help you find answer for some of the questions and provide more information about the celcom package to you.")
        page.typing_on(sender_id)
        sleep(1)
        page.send(sender_id, "to start any conversation with me, just text \"tabot\" to me")
        page.typing_on(sender_id)
        sleep(1)
        page.send(sender_id, "then you can choose from one of the following actions\n➡️explore\n➡️ask question\n➡️game")
        page.typing_on(sender_id)
        sleep(1)
        page.send(sender_id, "feel free to explore yourself.")
        page.typing_on(sender_id)
        sleep(1)
        page.send(sender_id, "💤 resting now...")
    else:
        page.typing_on(sender_id)
        sleep(1)
        page.send(sender_id, "😅 I'm not sure what you are saying.")
        page.typing_on(sender_id)
        sleep(1)
        page.send(sender_id, "You can always text \"tabot\" to start the conversation! Cheer 😎")

@page.callback(['PREPAID-.*', 'POSTPAID-.*', 'OTHER-.*?'], types=['POSTBACK'])
def save_question_label(payload, event):
    sender_id = event.sender_id

    question = " ".join(payload.split("-")[1:])
    label = payload.split("-")[0]
    if label.lower() == "prepaid":
        label = 1
    elif label.lower() == "postpaid":
        label = 2
    elif label.lower() == "other":
        label = 3
    connect_db.add_question(question, label)
    page.send(sender_id, "Thank you 😇 your answer")
    page.typing_on(sender_id)
    sleep(2)
    quick_replies = [
        QuickReply(title="ask question", payload="Q_SEARCH"),
        QuickReply(title="game", payload="GAME"),
        QuickReply(title="nothing", payload="NO")
    ]
    page.send(sender_id,
              "Is there anything that I can still help you?",
              quick_replies=quick_replies)

@page.callback(['NO'], types=['QUICK_REPLY'])
def no_callback(payload, event):
    sender_id = event.sender_id

    page.send(sender_id, "OK, Hope you enjoy the experience!")
    page.typing_on(sender_id)
    sleep(1)
    page.send(sender_id, "See you soon 👋")

@page.callback(['GET_START'])
def start_callback(payload, event):
    sender_id = event.sender_id

    page.typing_on(sender_id)
    sleep(1)
    page.send(sender_id, "🤗 I am TaBot and I am here to help you to know more about Celcom package")
    page.typing_on(sender_id)
    sleep(1)
    quick_replies = [
        QuickReply(title="quiz", payload="GAME"),
        QuickReply(title="explore", payload="D_SEARCH"),
        QuickReply(title="ask question", payload="Q_SEARCH")
    ]
    page.send(sender_id,
              "Choose one of the actions below 👇 to start the conversation",
              quick_replies=quick_replies)

@page.callback(['START'], types=['POSTBACK'])
def start_callback(payload, event):
    sender_id = event.sender_id

    quick_replies = [
        QuickReply(title="quiz", payload="GAME"),
        QuickReply(title="explore", payload="D_SEARCH"),
        QuickReply(title="ask question", payload="Q_SEARCH")
    ]
    page.send(sender_id,
              "What would you like to do now?",
              quick_replies=quick_replies)

@page.callback(['HELP'], types=['POSTBACK'])
def help_callback(payload, event):
    sender_id = event.sender_id

    page.typing_on(sender_id)
    sleep(2)
    page.send(sender_id,
              "👋 I am Tabot, a 🤖 to help you find answer for some of the questions and provide more information about the celcom package to you.")
    page.typing_on(sender_id)
    sleep(1)
    page.send(sender_id, "to start any conversation with me, just text \"tabot\" to me")
    page.typing_on(sender_id)
    sleep(1)
    page.send(sender_id, "then you can choose from one of the following actions\n➡️explore\n➡️ask question\n➡️game")
    page.typing_on(sender_id)
    sleep(1)
    page.send(sender_id, "feel free to explore yourself.")
    page.typing_on(sender_id)
    sleep(1)
    page.send(sender_id, "💤 resting now...")

@page.callback(["D_SEARCH"], types=['QUICK_REPLY'])
def d_search_callback(payload, event):
    sender_id = event.sender_id

    subjects = ["xpax", "musicWalla", "videoWalla"]

    # this part will limit the number of subject to choose from (deprecated)
    # if len(subjects) > 11:
    #     subjects = sample(subjects, 11)
    # else:
    #     pass

    quick_replies = [QuickReply(title=format_sentence.format_quick_reply_title(subject), payload=subject) for subject in subjects]
    page.send(sender_id,
              "Select the topic that you would like to explore.",
              quick_replies=quick_replies)

@page.callback(available_subjects, types=['QUICK_REPLY'])
def predicate_search(payload, event):
    sender_id = event.sender_id

    annotation_list = ["label", "comment", "type"]
    predicates = query.search_predicate(payload)
    for annotation in annotation_list:
        if annotation in predicates:
            predicates.remove(annotation)

    if len(predicates) > 11:
        predicates = sample(predicates, 11)
    else:
        pass
    quick_replies = [QuickReply(title=format_sentence.format_quick_reply_title(predicate), payload=payload+"_"+predicate) for predicate in predicates]
    page.send(sender_id,
              "Select the information that you would like to know. ☺️",
              quick_replies=quick_replies)

@page.callback(available_subject_predicate, types=['QUICK_REPLY'])
def object_search(payload, event):
    sender_id = event.sender_id

    subject, predicate = payload.split("_")
    answers = query.search_objects(subject, predicate)
    if answers:
        send_payload = []
        for answer in answers:
            answer_split = answer.split("#")
            if answer_split[0] == "http://www.celcom.com.my/ontology":
                send_payload.append(answer_split[1])
            elif len(answer_split) == 1:
                # this will handle end of conversation with datatype
                if answer_split[0].startswith("http"):
                    page.send(sender_id, Template.Generic([
                        Template.GenericElement(
                            format_sentence.format_answer(subject),
                            subtitle=format_sentence.format_answer(subject) + " " + format_sentence.format_answer(predicate),
                            image_url="https://www.celcom.com.my/sites/default/files/images/banner/xpax_product_bemorewalla_md.jpg",
                            buttons=[
                                Template.ButtonWeb("Click me 😆", answer_split[0])
                            ]
                        )
                    ]))
                elif not query.search_objects(predicate, "subPropertyOf"):
                    page.send(sender_id, format_sentence.format_answer(predicate) + " is " + format_sentence.format_answer(answer_split[0]))
                else:
                    if query.search_objects(predicate, "subPropertyOf")[0].split("#")[1] == "dial":
                        page.send(sender_id, format_sentence.format_answer(predicate) + " by dialing " + format_sentence.format_answer(answer_split[0]))
        if not send_payload:
            page.send(sender_id, "If you still have any question, type 'tabot' to start the conversation again")
        else:
            send_pretty_list = [format_sentence.format_answer(text) for text in send_payload]
            page.send(sender_id, "🤗 these are the answers: " + ", ".join(send_pretty_list))
            # this will mark the end of message if user ask about NRIC or passport
            if 'nric' in send_payload or 'passport' in send_payload:
                page.send(sender_id, "If you still have any question, type 'tabot' to start the conversation again")
            else:
                yes_payload = "YES_" + "_".join(send_payload)
                buttons = [
                    Template.ButtonPostBack("Yes", yes_payload),
                    Template.ButtonPostBack("No", "NO")
                ]
                page.send(sender_id, Template.Buttons("Continue to explore?", buttons))
    else:
        page.send(sender_id, "No information to show anymore!!")

@page.callback(['YES_.*', 'NO'], types=['POSTBACK'])
def continue_explore(payload, event):
    sender_id = event.sender_id

    if "YES" in payload:
        subjects = payload.split("_")[1:]
        quick_replies = [QuickReply(title=format_sentence.format_quick_reply_title(subject), payload=subject) for subject in subjects]
        page.send(sender_id,
                  "What is the next thing you would like to know? 🤔",
                  quick_replies=quick_replies)
    else:
        page.send(sender_id, "Feel free to type 'tabot' to start the conversation again 😉")

@page.callback(["Q_SEARCH"], types=['QUICK_REPLY'])
def q_search_callback(payload, event):
    sender_id = event.sender_id
    global timestamp

    page.send(sender_id, "What is the question that you would like to ask?")
    timestamp = event.timestamp

@page.callback(['(PREPAID|POSTPAID)_(YES|NO)'], types=['QUICK_REPLY'])
def determine_web_com(payload, event):
    sender_id = event.sender_id
    plan = payload.split("_")[0]

    if "YES" in payload :
        page.send(sender_id, "Ok, wait a minute. I will get the answer now")
        page.typing_on(sender_id)
        if plan == "PREPAID":
            page.send(sender_id, Template.Generic([
                Template.GenericElement(
                    "Prepaid FAQ",
                    subtitle="Faq about prepaid plan",
                    item_url="https://www.celcom.com.my/support/faq/personal",
                    buttons=[
                        Template.ButtonWeb("Get Answer", "https://www.celcom.com.my/support/faq/personal")
                    ]
                )
            ]))
        elif plan == "POSTPAID":
            page.send(sender_id, Template.Generic([
                Template.GenericElement(
                    "Postpaid FAQ",
                    subtitle="Faq about postpaid plan",
                    item_url="https://www.celcom.com.my/support/faq/personal#personal-postpaid-plans-first-gold",
                    buttons=[
                        Template.ButtonWeb("Get Answer", "https://www.celcom.com.my/support/faq/personal#personal-postpaid-plans-first-gold")
                    ]
                )
            ]))
    else:
        if plan == "PREPAID":
            page.send(sender_id, "Then, I am assuming you ask about postpaid plan!")
            page.typing_on(sender_id)
            page.send(sender_id, Template.Generic([
                Template.GenericElement(
                    "Postpaid FAQ",
                    subtitle="Faq about postpaid plan",
                    item_url="https://www.celcom.com.my/support/faq/personal#personal-postpaid-plans-first-gold",
                    buttons=[
                        Template.ButtonWeb("Get Answer", "https://www.celcom.com.my/support/faq/personal#personal-postpaid-plans-first-gold")
                    ]
                )
            ]))
        elif plan == "POSTPAID":
            page.send(sender_id, "Then, I am assuming you ask about prepaid plan!")
            page.typing_on(sender_id)
            page.send(sender_id, Template.Generic([
                Template.GenericElement(
                    "Prepaid FAQ",
                    subtitle="Faq about prepaid plan",
                    item_url="https://www.celcom.com.my/support/faq/personal",
                    buttons=[
                        Template.ButtonWeb("Get Answer", "https://www.celcom.com.my/support/faq/personal")
                    ]
                )
            ]))

@page.callback(["GAME"], types=['QUICK_REPLY'])
def game_callback(payload, event):
    sender_id = event.sender_id
    page.send(sender_id, "🤖 Let's start the QUIZ")
    page.typing_on(sender_id)
    sleep(1)
    # page.send(sender_id, "WIN 🎮👾 by getting the HIGHEST mark")
    # page.typing_on(sender_id)
    # sleep(1)
    quick_replies = [
        QuickReply(title="easy", payload="EASY"),
        QuickReply(title="medium", payload="MEDIUM"),
        QuickReply(title="hard", payload="HARD")
    ]
    page.send(sender_id,
              "Select the category that you want to challenge!",
              quick_replies=quick_replies)

@page.callback(["EASY", "MEDIUM", "HARD"], types=['QUICK_REPLY'])
def handle_difficulty(payload, event):
    sender_id = event.sender_id

    message.challenge_message(page, sender_id, payload)
    if payload.lower() == "easy":
        knowledge_check_game.challenge(0, 5, 0, sender_id)
    elif payload.lower() == "medium":
        knowledge_check_game.challenge(0, 10, 0, sender_id)
    elif payload.lower() == "hard":
        knowledge_check_game.challenge(0, 15, 0, sender_id)
    else:
        quick_replies = [
            QuickReply(title="easy", payload="EASY"),
            QuickReply(title="medium", payload="MEDIUM"),
            QuickReply(title="hard", payload="HARD")
        ]
        page.send(sender_id,
                  "Which level of difficulty you want to challenge?",
                  quick_replies=quick_replies)

@app.route('/webhook', methods=['GET'])
def get_webhook():
    """
    Handle webhook verification from Facebook
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == "subscribe" and token == "goodToGo":
        cprint("webhook verify!", "green")
        return challenge
    else:
        cprint("webhook failed to verify!", "red")
        return "Fail to verify", 403

def clean_question(text):
    text = text.lower()
    text = "".join(c for c in text if c not in string.punctuation)
    text = text.strip()
    return text

if __name__ == "__main__":
    app.run(debug=True)
