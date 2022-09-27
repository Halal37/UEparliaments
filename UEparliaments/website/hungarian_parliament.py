import os
import django
import requests
import logging
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from time import sleep

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

logger = logging.getLogger(__name__)
os.environ['DJANGO_SETTINGS_MODULE'] = 'UEparliaments.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UEparliaments.settings")

django.setup()
from website.models import ParliamentaryTerm, Parliament, MandateOfMP, MP, PoliticalParty, Country

parliament = Parliament.objects.get(country="Hungary", name="National Assembly")

headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
           'Accept':
               'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}


def add_terms():
    try:
        pageTree = requests.get(
            "https://www.parlament.hu/web/house-of-the-national-assembly/list-of-mps?p_p_id=hu_parlament_cms_pair_portlet_PairProxy_INSTANCE_9xd2Wc9jP4z8&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_auth=iWM7Wz1z&_hu_parlament_cms_pair_portlet_PairProxy_INSTANCE_9xd2Wc9jP4z8_pairAction=%2Finternet%2Fcplsql%2Fogy_kpv.kepv_adat%3Fp_azon%3Do320%26p_nyelv%3DEN%26p_stilus%3D%26p_head%3D",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        terms = soup.find("div", {"class": "kepvcsop-tagsag"})
        terms = terms.find_all("tr")
        term_number = len(terms) - 2
        for term in terms:
            if term.find("td") is not None:
                if term.find_all("td")[3].get_text() == "\xa0":
                    end_of_term = None
                else:

                    end_of_term = datetime.strptime(term.find_all("td")[3].get_text(), '%d-%m-%Y').strftime(
                        '%Y-%m-%d')
                beginning_of_term = datetime.strptime(term.find_all("td")[2].get_text(), '%d-%m-%Y').strftime(
                    '%Y-%m-%d')
                if beginning_of_term < "2014":
                    seats = (386)
                else:
                    seats = 199
                ParliamentaryTerm.objects.get_or_create(seats=seats, term=term_number,
                                                        parliament=parliament,
                                                        beginning_of_term=beginning_of_term,
                                                        end_of_term=end_of_term)
                term_number -= 1
    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_political_parties_and_mps():
    try:

        terms = ParliamentaryTerm.objects.filter(parliament=parliament)
        parliamentary_term = terms[0].term
        pageTree = requests.get(
            "https://www.parlament.hu/web/house-of-the-national-assembly/list-of-mps",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        members = soup.find_all("a", {"class": ""})
        for member in members:

            name = member.get_text()
            if ", " not in name:
                continue
            if "Dr. " in name:
                name = name.replace("Dr. ", "")
            if "Gy. " in name:
                name = name.replace("Gy. ", "")
            if "F. " in name:
                name = name.replace("F. ", "")
            if "V. " in name:
                name = name.replace("V. ", "")
            if "Z. " in name:
                name = name.replace("Z. ", "")

            last_name = name.split(",")[0]
            first_name = name.split(", ")[1]
            exists = MP.objects.filter(first_name=first_name,
                                       last_name=last_name, )

            if len(exists) > 0:
                continue
            else:
                sleep(60)

            if "https://www.parlament.hu:443/web/house-of-the-national-assembly/" in member['href']:
                link = member['href']
                member_pageTree = requests.get(
                    link,
                    headers=headers)
                member_soup = BeautifulSoup(member_pageTree.content, 'html.parser')

                mandate = member_soup.find("div", {"class": "kepvcsop-tagsag"})
                mandate = mandate.find_all("tr")[2]
                political_party = mandate.find_all("td")[1].get_text()
                beginning_of_term = datetime.strptime(mandate.find_all("td")[2].get_text(), '%d-%m-%Y').strftime(
                    '%Y-%m-%d')
                if mandate.find_all("td")[3].get_text() == "\xa0":
                    end_of_term = None
                else:

                    end_of_term = datetime.strptime(mandate.find_all("td")[3].get_text(), '%d-%m-%Y').strftime(
                        '%Y-%m-%d')
                PoliticalParty.objects.get_or_create(
                    country=Country.objects.get(country_name="Hungary"), name=political_party)

                MP.objects.get_or_create(first_name=first_name,
                                         last_name=last_name)

                MandateOfMP.objects.get_or_create(
                    party=PoliticalParty.objects.get(country="Hungary", name=political_party),
                    parliamentary_term=ParliamentaryTerm.objects.get(
                        parliament=parliament,
                        term=parliamentary_term),
                    parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                             last_name=last_name),
                    beginning_of_term=beginning_of_term,
                    end_of_term=end_of_term)





    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_terms()
    add_political_parties_and_mps()
