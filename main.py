import requests
import pandas as pd
import progressbar
from bs4 import BeautifulSoup
import re

URL = "https://satisfactory-calculator.com"


def parse_items():
    page = requests.get(URL + "/en/items")
    soup = BeautifulSoup(page.content, "html.parser")
    return map(lambda x: x.attrs["href"], soup.select(".card > .card-body > a"))


def parse_item(href):
    page = requests.get(URL + href)
    soup = BeautifulSoup(page.content, "html.parser")
    name = soup.select_one("main h4").text
    category = soup.select("i.fa-archive")[0].parent.text.strip()
    stacksize = 0
    sinkpoints = 0
    try:
        stacksize = soup.select("i.fa-layer-group")[0].parent.parent.find("strong").text.strip()
        sinkpoints = soup.select("i.fa-money-bill-wave")[0].parent.parent.find("strong").text.strip()
    except IndexError:
        pass
    id = re.findall('id/(.*?)/name', href)[0]
    buildables = 0
    try:
        producers = soup.find("strong", string="Used to craft").parent.parent.select("tbody td:nth-child(5)")
        buildables = len(list(filter(lambda x: x.text.strip() == "---", producers)))
    except AttributeError:
        pass
    intermediate = buildables == 0

    return {'id': id, 'name': name, 'intermediate': intermediate, 'category': category, 'stacksize': stacksize,
            'sinkpoints': sinkpoints, 'buildables': buildables}


items = pd.DataFrame.from_records([])
for i in progressbar.progressbar(map(parse_item, list(parse_items())[:])):
    items = pd.concat([items,pd.DataFrame.from_records([i])])
items.to_csv("items.csv", index=False)

