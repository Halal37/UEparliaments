import os
import django
import requests
import logging
import sys
from bs4 import BeautifulSoup
from datetime import datetime

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

parliament = Parliament.objects.get(country="Malta", name="Parliament")


def add_current_term_mps_and_political_parties():
    try:
        pageTree = requests.get(
            "https://parlament.mt/en/14th-leg/political-groups/",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        terms = soup.find("div", {"class": "sidebar-module hidden-print"})
        terms = terms.find("div")
        terms = terms.find_all("a")
        term = terms[0]
        link = term['href']
        term = link
        term = term.split("th")[0].split("rd")[0].split("nd")[0].split("st")[0]
        term = term.split("/en/")[1]
        members_pageTree = requests.get(
            "https://parlament.mt" + link,
            headers=headers)
        members_soup = BeautifulSoup(members_pageTree.content, 'html.parser')
        members = members_soup.find_all("div", {"class": "col-xs-12"})
        for member in members:
            member = member.find_all("div", {"class", "col-xs-12"})
            if len(member) > 0:
                for mp in member:
                    link = mp.find("a")['href']
                    political_party = link.split("/en/14th-leg/political-groups/")[1].split("/")[0]
                    if political_party == "partit-nazzjonalista":
                        political_party = "Nationalist Party"
                    elif political_party == "labour-party":
                        political_party = "Labour Party"
                    name = mp.find("a").get_text()
                    name = name.split(" - ")[0]
                    last_name = name.split(", ")[0]
                    first_name = name.split(", ")[1]
                    mp_pageTree = requests.get(
                        "https://parlament.mt" + link,
                        headers=headers)
                    mp_soup = BeautifulSoup(mp_pageTree.content, 'html.parser')
                    mp_info = mp_soup.find_all("div", {"class", "panel-default"})

                    for info in mp_info:
                        if info.find("h4") is not None:
                            if info.find("h4").get_text() == "Electoral History":
                                mp_terms = info.find_all("div", {"class", "panel-default"})
                                for mp_term in mp_terms:
                                    if mp_term.find("p") is not None:
                                        mp_link = mp_term.find("p").find("a")['href']
                                        mp_link = mp_link.split("th")[0].split("rd")[0].split("nd")[0].split("st")[0]
                                        mp_term_number = mp_link.split("/en/")[1]
                                        if mp_term_number == term:
                                            beginning_of_term = mp_term.find("tbody").find_all("td")[1].get_text()
                                            beginning_of_term = datetime.strptime(beginning_of_term,
                                                                                  '%d.%m.%Y').strftime(
                                                '%Y-%m-%d')
                                            MP.objects.get_or_create(first_name=first_name,
                                                                     last_name=last_name)

                                            PoliticalParty.objects.get_or_create(
                                                country=Country.objects.get(country_name="Malta"),
                                                name=political_party)

                                            parliamentary_term = ParliamentaryTerm.objects.get(
                                                parliament=parliament,
                                                term="14")
                                            MandateOfMP.objects.get_or_create(
                                                party=PoliticalParty.objects.get(country="Malta",
                                                                                 name=political_party),
                                                parliamentary_term=parliamentary_term,
                                                parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                                                         last_name=last_name),
                                                beginning_of_term=beginning_of_term,
                                                end_of_term=None)

                            else:
                                continue



    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_current_term_mps_and_political_parties()
