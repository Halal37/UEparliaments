import os
import django
import requests
import logging
import sys
from datetime import datetime
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

logger = logging.getLogger(__name__)
os.environ['DJANGO_SETTINGS_MODULE'] = 'UEparliaments.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UEparliaments.settings")

django.setup()

from website.models import SenateTerm, Senate, MandateOfSenator, Senator, PoliticalParty, Country

headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
           'Accept':
               'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

senate = Senate.objects.get(country="Romania", name="Senate")


def add_current_term_senators():
    try:

        pageTree = requests.get(
            "https://www.senat.ro/FisaSenatori.aspx",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        senators = soup.find("table", {"class", "display"})
        senators = senators.find("tbody").find_all("tr")
        for senator in senators:
            link = senator.find("a")['href']
            name = senator.find("a").get_text()
            last_name = name.split()[0]
            first_name = name.split(last_name + " ")[1]
            first_name = first_name.replace("-", " ")
            last_name = last_name.title()
            date_of_birth = senator.find_all("td")[2].get_text()
            date_of_birth = datetime.strptime(date_of_birth, '%d.%m.%Y').strftime('%Y-%m-%d')
            senator_pageTree = requests.get(
                "https://www.senat.ro/" + link,
                headers=headers)
            senator_soup = BeautifulSoup(senator_pageTree.content, 'html.parser')
            political_party = senator_soup.find("span", {"class", "inline-block"}).next_sibling.get_text()
            temporary_political_party = political_party.split()
            political_party = " ".join(temporary_political_party)
            if "\"" in political_party:
                political_party = political_party.split("\"")[1]
                political_party=political_party.replace("\"", "")
            political_party_short_name = []
            if political_party == "-":
                political_party = "Independent"
            else:
                for word in political_party:
                    if word[0].isupper():
                        political_party_short_name.append(word[0])
                political_party = "".join(political_party_short_name)
            tables= senator_soup.find_all("table")
            for table in tables:
                if table["id"]=="td7":
                    term = table

            term = term.find("tbody").find_all("tr")
            for i in term:
                if "Senat" in i.get_text():
                    beginning_of_term = i.find_all("td")[1].get_text()
                    beginning_of_term = datetime.strptime(beginning_of_term, '%d.%m.%Y').strftime('%Y-%m-%d')
            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Romania"), name=political_party)
            Senator.objects.get_or_create(first_name=first_name,
                                          last_name=last_name,
                                          date_of_birth=date_of_birth)

            MandateOfSenator.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Romania", name=political_party),
                senate_term=SenateTerm.objects.get(senate=senate, term="56"),
                senate=senate,
                senator=Senator.objects.get(first_name=first_name,
                                            last_name=last_name,
                                            date_of_birth=date_of_birth),
                beginning_of_term=beginning_of_term,
                end_of_term=None)


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_current_term_senators()
