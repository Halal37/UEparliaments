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

parliament = Parliament.objects.get(country="Greece", name="Parliament")


def add_political_parties():
    try:
        pageTree = requests.get(
            "https://www.hellenicparliament.gr/en/Vouleftes/Viografika-Stoicheia/",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        political_parties = soup.find_all("div", {"class": "labelinputpair"})[1]
        political_parties = political_parties.find_all("option")[1:]
        for political_party in political_parties:
            political_party = political_party.get_text()
            if political_party != "MeRA25":
                political_party = political_party.lower().title()
            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Greece"), name=political_party)
    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_mps():
    try:
        pageTree = requests.get(
            "https://www.hellenicparliament.gr/en/Vouleftes/Viografika-Stoicheia/",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        political_parties = soup.find_all("div", {"class": "labelinputpair"})[1]
        political_parties = political_parties.find_all("option")[1:]
        for political_party in political_parties:
            political_party_value = political_party["value"]
            political_party = political_party.get_text()
            if political_party != "MeRA25":
                political_party = political_party.lower().title()
            link = f"https://www.hellenicparliament.gr/en/Vouleftes/Viografika-Stoicheia/?search=on&PoliticalParty={political_party_value}8&pageNo=1"
            mp_by_political_party(link, political_party)

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def mp_by_political_party(link, political_party):
    try:
        term = ParliamentaryTerm.objects.get(parliament=parliament)
        parliamentary_term = term.term
        beginning_of_term = term.beginning_of_term
        political_party_pageTree = requests.get(
            link,
            headers=headers)
        political_party_soup = BeautifulSoup(political_party_pageTree.content, 'html.parser')
        next_link = political_party_soup.find("a", {
            "id": "ctl00_ContentPlaceHolder1_mpr_repSearchResults_ctl11_ctl01_repPager_ctl10_lnkNextPages"})
        odd_mps = political_party_soup.find_all("tr", {"class", "odd"})
        even_mps = political_party_soup.find_all("tr", {"class", "even"})
        for mp in odd_mps:
            add_mp(mp, political_party, parliamentary_term, beginning_of_term)
        for mp in even_mps:
            add_mp(mp, political_party, parliamentary_term, beginning_of_term)
        if next_link is not None:
            next_link = next_link["href"]
            next_link = f"https://www.hellenicparliament.gr{next_link}"
            mp_by_political_party(next_link, political_party)

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")

def add_mp(mp,political_party,parliamentary_term,beginning_of_term):
    name = mp.find_all("a")[1].get_text()
    name = name.split(" (")[0]
    last_name = name.split()[0]
    first_name = name.split()[-1]
    MP.objects.get_or_create(first_name=first_name,
                             last_name=last_name)

    MandateOfMP.objects.get_or_create(
        party=PoliticalParty.objects.get(country="Greece", name=political_party),
        parliamentary_term=ParliamentaryTerm.objects.get(
            parliament=parliament,
            term=parliamentary_term),
        parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                 last_name=last_name),
        beginning_of_term=beginning_of_term,
        end_of_term=None)


if __name__ == "__main__":
    add_political_parties()
    add_mps()
