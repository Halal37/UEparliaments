import os
import django
import requests
import logging
import sys
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

logger = logging.getLogger(__name__)
os.environ['DJANGO_SETTINGS_MODULE'] = 'UEparliaments.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UEparliaments.settings")

django.setup()
from website.models import ParliamentaryTerm, Parliament, MandateOfMP, MP, PoliticalParty, Country

headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
           'Accept':
               'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

parliament = Parliament.objects.get(country="Sweden", name="Riksdag")


def add_political_parties():
    try:
        pageTree = requests.get(
            "https://www.riksdagen.se/en/members-and-parties/?typeoflist=default",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        political_parties = soup.find("ul", {"class",
                                             "module-parties-list-logo large-block-grid-6 medium-block-grid-4 small-block-grid-2"})
        political_parties = political_parties.find_all("li", {"class", "item"})
        for party in political_parties:
            political_party = party.find("a", {"class", "item-name"}).get_text()[:-1]
            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Sweden"), name=political_party)


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_mps():
    try:
        terms = ParliamentaryTerm.objects.get(parliament=parliament)
        parliamentary_term = terms.term
        beginning_of_term = terms.beginning_of_term
        pageTree = requests.get(
            "https://www.riksdagen.se/en/members-and-parties/?typeoflist=default",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        mps = soup.find_all("li", {"class", "fellow-item"})
        for mp in mps:
            name = mp.find("span", {"class": "fellow-name"}).get_text()
            name = name.split(" (")[0]
            first_name = name.split(", ")[1]
            last_name = name.split(",")[0]
            last_name = last_name[1:]
            link = mp.find("a", {"class", "fellow-item-container"})['href']

            member_pageTree = requests.get(
                "https://www.riksdagen.se" + link,
                headers=headers)
            member_soup = BeautifulSoup(member_pageTree.content, 'html.parser')
            political_party = member_soup.find("div",
                                               {"class": "large-4 medium-6 small-12 columns fellow-item-collection"})
            political_party = political_party.find("div", {
                "class": "large-12 medium-12 small-12 columns fellow-item"}).get_text()
            political_party = political_party.split("Party ")[1]
            temporary_political_party = political_party.split()
            political_party = " ".join(temporary_political_party)
            MP.objects.get_or_create(first_name=first_name,
                                     last_name=last_name)

            MandateOfMP.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Sweden", name=political_party),
                parliamentary_term=ParliamentaryTerm.objects.get(
                    parliament=parliament,
                    term=parliamentary_term),
                parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                         last_name=last_name),
                beginning_of_term=beginning_of_term,
                end_of_term=None)


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_political_parties()
    add_mps()
