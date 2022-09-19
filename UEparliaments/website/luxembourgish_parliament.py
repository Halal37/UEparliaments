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

parliament = Parliament.objects.get(country="Luxembourg", name="Chamber of Deputies")

headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
           'Accept':
               'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}


def add_political_parties_and_mps():
    try:
        terms = ParliamentaryTerm.objects.get(parliament=parliament)
        parliament_term = terms.term
        pageTree = requests.get(
            "https://www.chd.lu/wps/portal/public/Accueil/OrganisationEtFonctionnement/Organisation/Deputes/DeputesEnFonction",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        script = soup.find_all("div", {"class": "listeInstitutions"})
        for element in script:
            links = element.find_all("a")
            for i in links:
                if i.find("img")['src'].split(".png")[0][-1] is "M":
                    gender = "male"
                else:
                    gender = "female"
                mp_link = i["href"]
                mpTree = requests.get(
                    f"https://www.chd.lu/{mp_link}",
                    headers=headers)
                mp_soup = BeautifulSoup(mpTree.content, 'html.parser')
                mp_name = mp_soup.find("h2", {"class": "TitleOnly"})
                name = mp_name.get_text().split(" ")
                first_name = name[0]
                last_name = name[1]
                mp_day_of_birth = mp_soup.find("div", {"class": "deputeDet"})
                day = mp_day_of_birth.find("td", {"class": "bgRed"})
                if len(day.get_text().split(("Date de naissance: "))) > 1:
                    day = day.get_text().split(("Date de naissance: "))[1].split(" Lieu de naissance:")[0].split(" ")[0]
                    if len(day) is 10:
                        date_of_birth = str(datetime.strptime(day, '%d/%m/%Y').strftime('%Y-%m-%d'))
                    else:
                        date_of_birth = None
                else:
                    date_of_birth = None
                mp_party = mp_soup.find("a", {"class": "arrow"})
                party_name = mp_party.get_text().replace(mp_party.get_text().split("politique ")[0], "").replace(
                    "politique ", "").replace("\"", "")
                party = party_name.title()

                mp_terms = mp_soup.find("div", {"class": "freeText padLeft10"})
                for i in mp_terms.find_all("ul"):
                    if i.find("strong").get_text() == "Député ":
                        term = i.get_text()
                        if "depuis le" in term:
                            parliament_beginning_of_term = str(
                                datetime.strptime(term.replace("Député depuis le ", ""), '%d/%m/%Y').strftime(
                                    '%Y-%m-%d'))
                PoliticalParty.objects.get_or_create(
                    country=Country.objects.get(country_name="Luxembourg"), name=party)
                MP.objects.get_or_create(first_name=first_name,
                                         last_name=last_name,
                                         gender=gender,
                                         date_of_birth=date_of_birth)
                MandateOfMP.objects.get_or_create(
                    party=PoliticalParty.objects.get(country="Luxembourg", name=party),
                    parliamentary_term=ParliamentaryTerm.objects.get(
                        parliament=parliament,
                        term=parliament_term),
                    parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                             last_name=last_name,
                                                             gender=gender,
                                                             date_of_birth=date_of_birth),
                    beginning_of_term=parliament_beginning_of_term,
                    end_of_term=None)

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_political_parties_and_mps()
