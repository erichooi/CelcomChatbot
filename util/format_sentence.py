import re

def format_quick_reply_title(text):
    verb_pattern = re.compile(r"(^[a-z]*)")
    object_pattern = re.compile(r"([A-Z]([A-Z]+|[a-z]+))")
    number = re.compile(r"(\d+)")
    noun = re.compile(r"(\w+)$")

    verb = re.search(verb_pattern, text)
    verb = verb.group(1)
    # change the code to their meaning
    if verb == "c":
        verb = "check"
    elif verb == "s":
        verb = "stop"
    # different uppercase method for verbs
    if verb == "nric":
        verb = verb.upper()
    else:
        verb = verb.title()
    # retrieve digit if there is any in the title
    digit = ""
    if re.search(number, text):
        digit = re.search(number, text).group()
    # retrieve the last word after any number
    word = ""
    if re.search(noun, text):
        word = re.search(noun, text).group()
    objects = re.findall(object_pattern, text)
    objects = [text[0] for text in objects]
    if verb and objects and digit:
        return verb + " " + " ".join(objects) + " " + digit
    elif verb and objects:
        return verb + " " + " ".join(objects)
    elif verb:
        return verb
    elif digit and word:
        return digit + " " + word

def format_answer(text):
    if "number_sign" in text:
        number_sign_pattern = re.compile(r"(\(\w+_\w+\))")
        text = re.sub(number_sign_pattern, r'#', text)
    else:
        text = format_quick_reply_title(text)
    return text

# print(format_answer("cRemainingBonus"))
# import pickle
# datatypes = pickle.load(open("datatype.pickle", "rb"))
# objects = pickle.load(open("object.pickle", "rb"))
# subjects = pickle.load(open("subject.pickle", "rb"))
#
# for data in subjects:
#     print(format_quick_reply_title(data))
