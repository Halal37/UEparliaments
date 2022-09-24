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
from website.models import ParliamentaryTerm, Parliament, MandateOfMP, MP, PoliticalParty, Country

parliament = Parliament.objects.get(country="Czech Republic", name="Chamber of Deputies")

headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
           'Accept':
               'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}


def add_political_parties_and_mps():
    try:
        terms = ParliamentaryTerm.objects.get(parliament=parliament)
        parliament_term = terms.term
        pageTree = requests.get(
            "https://pspen.psp.cz/chamber-members/members/",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        members = soup.find_all("div", {"class": "col-md-4 col-sm-6 col-xs-12"})
        for member in members:
            link_and_name = member.find("a", {"class": "member_name"})
            name = link_and_name.get_text()
            first_name = name.split()[0]
            last_name = name.split(first_name + " ")[1]
            link = link_and_name['href']
            party = member.find("img", {"class": "party_img"})['alt']
            if "Lucie" is first_name or first_name[-1] is "a":
                gender = "female"
            else:
                gender = "male"

            if party == "piráti":
                party = party.title()
            else:
                party = party.upper()
            member_pageTree = requests.get(
                link,
                headers=headers)
            member_soup = BeautifulSoup(member_pageTree.content, 'html.parser')
            date_of_birth = member_soup.find("ul", {"class": "member_chars"}).get_text()
            date_of_birth = date_of_birth.split("Date of birth: ")[1]
            date_of_birth = date_of_birth.split(" ")[0][0:10]
            date_of_birth = datetime.strptime(date_of_birth, '%d.%m.%Y').strftime(
                '%Y-%m-%d')
            term = member_soup.find("div", {"id": "detail_tab0"})
            if "verifier from" in term.get_text():
                beginning_of_term = term.get_text().split("verifier from ")[1]
                beginning_of_term = beginning_of_term.split(" ")[0][0:10]
                beginning_of_term = datetime.strptime(beginning_of_term, '%d.%m.%Y').strftime(
                    '%Y-%m-%d')
            else:
                beginning_of_term = terms.beginning_of_term
            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Czech Republic"), name=party)

            MP.objects.get_or_create(first_name=first_name,
                                     last_name=last_name,
                                     gender=gender,
                                     date_of_birth=date_of_birth)

            MandateOfMP.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Czech Republic", name=party),
                parliamentary_term=ParliamentaryTerm.objects.get(
                    parliament=parliament,
                    term=parliament_term),
                parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                         last_name=last_name,
                                                         gender=gender,
                                                         date_of_birth=date_of_birth),
                beginning_of_term=beginning_of_term,
                end_of_term=None)


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_political_parties_and_mps()
