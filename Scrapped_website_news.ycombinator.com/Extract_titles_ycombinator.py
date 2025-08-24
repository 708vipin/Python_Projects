#To install Beautifulsoup run the command in terminal
#To install lxml parser
#html5lib is also a popular parser, but here we are going to use lxml
#To install requests
#You don't have to be extremely familiar with HTML to scrape 

from bs4 import BeautifulSoup
import requests
import csv

source = requests.get("https://news.ycombinator.com/").text
soup = BeautifulSoup(source, "lxml")

article_title = soup.find_all(class_="titleline")

csv_file = open("ycombinator_scrapped.csv", "w")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Article_headline", "Article_link"])

for title in article_title:
    a_tag = title.find("a")
    headline = title.find("a").text
    link =a_tag["href"]
    print(headline, "-", link)
    # print(title.prettify())

    csv_writer.writerow([headline, link])

csv_file.close()    



