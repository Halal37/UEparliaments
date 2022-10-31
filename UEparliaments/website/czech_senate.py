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

senate = Senate.objects.get(country="Czech Republic", name="Senate")


def add_current_term_senators():
    try:

        pageTree = requests.get(
            "https://www.senat.cz/senatori/index.php?lng=en&ke_dni=31.10.2022&O=13&par_2=2",
            headers=headers, verify=False)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        senators = soup.find_all("tr")
        for senator in senators[1:]:
            name = senator.find_all("td")[1].get_text()
            temporary_name = name.split()
            name = " ".join(temporary_name)
            first_name = name.split()[0]
            last_name = name.split(first_name + " ")[1]
            if first_name[-1] == "a":
                gender = "female"
            else:
                gender = "male"
            link = senator.find_all("td")[1].find("a")['href']
            senator_pageTree = requests.get(
                "https://www.senat.cz/senatori/" + link,
                headers=headers, verify=False)
            senator_soup = BeautifulSoup(senator_pageTree.content, 'html.parser')
            senator_info = senator_soup.find_all("td", {"class", "even"})
            if "Nr." not in senator_info[0].get_text():
                political_party = senator_info[0].get_text()
                if political_party == "no party affiliation":
                    political_party = "Independent"
                elif political_party == "KDU-CSL":
                    political_party = "KDU-ČSL"
                elif political_party == "TOP 09":
                    political_party = "TOP09"
                elif political_party == "Pirate":
                    political_party = "Piráti"
            else:
                political_party = "Independent"
            for info in senator_info:
                if "- " in info.get_text():
                    beginning_of_term = info.get_text()[0:10]
                    beginning_of_term = datetime.strptime(beginning_of_term, '%d.%m.%Y').strftime('%Y-%m-%d')
                    if beginning_of_term < "2022-10-01":
                        beginning_of_term = "2022-10-01"
            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Czech Republic"), name=political_party)
            Senator.objects.get_or_create(first_name=first_name,
                                          last_name=last_name,
                                          gender=gender)

            MandateOfSenator.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Czech Republic", name=political_party),
                senate_term=SenateTerm.objects.get(senate=senate, term="14"),
                senate=senate,
                senator=Senator.objects.get(first_name=first_name,
                                            last_name=last_name,
                                            gender=gender),
                beginning_of_term=beginning_of_term,
                end_of_term=None)

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_current_term_senators()
