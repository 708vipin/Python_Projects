import requests
from bs4 import BeautifulSoup

base_url = "https://www.yellowpages.com.au/search/listings?clue=Interior+Designers&locationClue=&lat=&lon="

data = []

for page in range(1,51):
    url = base_url.format(page)
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
