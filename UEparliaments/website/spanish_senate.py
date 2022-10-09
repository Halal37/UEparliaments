import os
import django
import logging
import sys
from datetime import datetime
from bs4 import BeautifulSoup
import requests

headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
           'Accept':
               'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

logger = logging.getLogger(__name__)
os.environ['DJANGO_SETTINGS_MODULE'] = 'UEparliaments.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UEparliaments.settings")

django.setup()
from website.models import SenateTerm, Senate, MandateOfSenator, Senator, PoliticalParty, Country, Parliament, \
    ParliamentaryTerm

senate = Senate.objects.get(country="Spain", name="Senate")


def add_terms():
    try:
        parliament = Parliament.objects.get(country="Spain", name="Congress of Deputies")
        spain_terms = ParliamentaryTerm.objects.filter(parliament=parliament)
        terms = []
        for i in spain_terms:
            terms.append(i.term)
            term = ParliamentaryTerm.objects.get(parliament=parliament, term=str(i.term))
            SenateTerm.objects.get_or_create(seats=266, term=str(i.term),
                                             senate=senate,
                                             beginning_of_term=term.beginning_of_term,
                                             end_of_term=term.end_of_term)
    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_senators():
    try:
        parliament = Parliament.objects.get(country="Spain", name="Congress of Deputies")
        spain_term = ParliamentaryTerm.objects.get(parliament=parliament, term=14)
        senate_term = spain_term.term
        end_of_term = spain_term.end_of_term

        pageTree = requests.get(
            "https://www.senado.es/web/composicionorganizacion/senadores/composicionsenado/senadoresdesde1977/consultaorden/index.html?legis=14",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        senators = soup.find_all("span", {"class": "col-1"})
        for senator in senators:
            name = senator.find("span").find("span")["title"].title()
            link = senator.find("a")["href"]
            first_name = name.split(", ")[1]
            last_name = name.split(",")[0]
            member_pageTree = requests.get(
                f"https://www.senado.es{link}",
                headers=headers)
            member_soup = BeautifulSoup(member_pageTree.content, 'html.parser')
            political_party = member_soup.find_all("a", {"class": "text_s_c2"})[-1].get_text()
            political_party = political_party.split("(")[1].split(")")[0]
            beginning_of_term = member_soup.find_all("span", {"class": "text_s"})[1].get_text()
            beginning_of_term = beginning_of_term.split("Fecha: ")[1]
            beginning_of_term = datetime.strptime(beginning_of_term, '%d/%m/%Y').strftime(
                '%Y-%m-%d')
            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Spain"), name=political_party)
            if "Baja " in member_soup.find_all("span", {"class": "text_s"})[2].get_text():
                end_of_term = member_soup.find_all("span", {"class": "text_s"})[2].get_text()
                end_of_term = end_of_term.split(": ")[1]
                end_of_term = datetime.strptime(end_of_term, '%d/%m/%Y').strftime(
                    '%Y-%m-%d')
            Senator.objects.get_or_create(first_name=first_name,
                                          last_name=last_name)

            MandateOfSenator.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Spain", name=political_party),
                senate_term=SenateTerm.objects.get(senate=senate, term=senate_term),
                senate=senate,
                senator=Senator.objects.get(first_name=first_name,
                                            last_name=last_name),
                beginning_of_term=beginning_of_term,
                end_of_term=end_of_term)

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_terms()
    add_senators()
