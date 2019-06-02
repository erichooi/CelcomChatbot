from time import sleep

def challenge_message(page, sender_id, level):
    page.send(sender_id, "Welcome to the " + level + " quiz.")
    page.typing_on(sender_id)
    sleep(1)
    level = level.lower()
    if level == "easy":
        page.send(sender_id, "This quiz contains 5 questions.")
    elif level == "medium":
        page.send(sender_id, "This quiz contains 10 questions.")
    elif level == "hard":
        page.send(sender_id, "This quiz contains 15 questions.")
    page.typing_on(sender_id)
    sleep(2)
    page.send(sender_id, "Let's start the quiz!!!")
    page.typing_on(sender_id)
    sleep(2)