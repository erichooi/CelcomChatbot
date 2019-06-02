import pickle
import requests
import os

from termcolor import cprint

link = pickle.load(open("celcom_link.pickle", "rb"))
base_url = "https://www.celcom.com.my"

if not os.path.exists("document"):
    cprint("Creating directory document", "green")
    os.mkdir("document")

for key in link.keys():
    if not os.path.exists("document/{}".format(key)):
        cprint("Creating directory {}".format(key), "green")
        os.mkdir("document/{}".format(key))
    for postfix_url in link[key]:
        url = base_url + postfix_url
        cprint("Downloading from " + url + "...", "blue")
        document = requests.get(url)
        with open("document/{}/{}".format(key, url.split("/")[-1] + ".html"), "w") as f:
            f.write(document.text)
cprint("Done downloading", "green")
