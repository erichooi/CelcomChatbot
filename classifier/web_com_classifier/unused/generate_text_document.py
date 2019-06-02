import os

from bs4 import BeautifulSoup


def convert_html_to_text(filename):
    with open(filename, "r") as f:
        content = f.read()
    # take from https://stackoverflow.com/questions/22799990/beatifulsoup4-get-text-still-has-javascript
    soup = BeautifulSoup(content, "html.parser")
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split(" "))
    text = "\n".join(chunk for chunk in chunks if chunk)
    return text

if not os.path.exists("data"):
    os.mkdir("data")

for root, dirs, files in os.walk("."):
    for name in files:
        filename = os.path.join(root, name)
        if filename.endswith(".html"):
            while True:
                convert = input("Convert this file '" + filename + "' (y)es or (n)o? ")
                if convert.startswith("y"):
                    filename_split = filename.split("/")
                    if not os.path.exists("data/{}".format(filename_split[2])):
                        os.mkdir("data/{}".format(filename_split[2]))
                    with open(
                            "data/{}/{}".format(
                                filename_split[2],
                                filename_split[3].split(".")[0] + ".txt"
                            )
                            , "w"
                        ) as f:
                        f.write(convert_html_to_text(filename))
                    break
                elif convert.startswith("n"):
                    break
                else:
                    pass

