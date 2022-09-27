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

parliament = Parliament.objects.get(country="Slovakia", name="National Council")

headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
           'Accept':
               'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}


def add_political_parties_and_mps():
    try:
        terms = ParliamentaryTerm.objects.filter(parliament=parliament)
        parliamentary_term = terms[0].term
        beginning_of_term = terms[0].beginning_of_term
        for i in range(8, 2, -1):
            pageTree = requests.get(
                f"https://www.nrsr.sk/web/Default.aspx?sid=poslanci/zoznam_abc&ListType=0&CisObdobia={i}",
                headers=headers)
            soup = BeautifulSoup(pageTree.content, 'html.parser')
            members = soup.find("div", {"class": "mps_list"})
            members = members.find_all("a")
            for member in members:
                if len(member.get_text().split()) > 0:
                    if "Default.aspx?sid=poslanci/poslanec" in member['href']:
                        name = member.get_text()
                        if "Dr. " is name:
                            name = name.replace("Dr. ", "")

                        last_name = name.split(",")[0]
                        first_name = name.split(", ")[1]

                        if "Lucie" is first_name or first_name[-1] is "a":
                            gender = "female"
                        else:
                            gender = "male"
                        link = member["href"]
                        member_pageTree = requests.get(
                            "https://www.nrsr.sk/web/" + link,
                            headers=headers)
                        member_soup = BeautifulSoup(member_pageTree.content, 'html.parser')
                        date_of_birth = member_soup.find_all("div", {"class": "grid_4 alpha"})[1]

                        date_of_birth = date_of_birth.find("span").get_text().replace(" ", "").replace("\xa0", "")
                        if len(date_of_birth.split())>0:
                            date_of_birth = datetime.strptime(date_of_birth.split()[0], '%d.%m.%Y').strftime(
                                '%Y-%m-%d')
                        else:
                            date_of_birth = None

                        political_party = member_soup.find_all("div", {"class": "grid_8 alpha omega"})[1]
                        political_party = political_party.find("span").get_text()

                        PoliticalParty.objects.get_or_create(
                            country=Country.objects.get(country_name="Slovakia"), name=political_party)

                        MP.objects.get_or_create(first_name=first_name,
                                                 last_name=last_name,
                                                 gender=gender,
                                                 date_of_birth=date_of_birth)
                        if i == 8:
                            MandateOfMP.objects.get_or_create(
                                party=PoliticalParty.objects.get(country="Slovakia", name=political_party),
                                parliamentary_term=ParliamentaryTerm.objects.get(
                                    parliament=parliament,
                                    term=parliamentary_term),
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
