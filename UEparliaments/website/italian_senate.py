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

from website.models import SenateTerm, Senate, MandateOfSenator, Senator, PoliticalParty, Country

headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
           'Accept':
               'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

senate = Senate.objects.get(country="Italy", name="Senate of the Republic")


def add_current_term_senators():
    try:

        pageTree = requests.get(
            "https://www.senato.it/leg/19/BGT/Schede/MappaAula/00000000.htm",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        senators = soup.find_all("li")
        for number, senator in enumerate(senators):
            name = senator.get_text().split(" - ")[0]
            last_name = name.split()[-1]
            first_name = name.split(" " + last_name)[0].title()
            last_name = last_name.title()
            political_party = senator.get_text().split(" - ")[1]
            political_party = political_party.split(" - ")[0]
            if political_party == "Azione-ItaliaViva-RenewEurope":
                political_party = "Azione-ItaliaViva"
            if political_party == "Presidente":
                political_party = "Fratelli d'Italia"
            if political_party == "FITTIZIO":
                political_party = "Independent"
            if number > 205:
                break

            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Italy"), name=political_party)
            Senator.objects.get_or_create(first_name=first_name,
                                          last_name=last_name)

            MandateOfSenator.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Italy", name=political_party),
                senate_term=SenateTerm.objects.get(senate=senate, term="19"),
                senate=senate,
                senator=Senator.objects.get(first_name=first_name,
                                            last_name=last_name),
                beginning_of_term="2022-10-13",
                end_of_term=None)


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_current_term_senators()
