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

headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
           'Accept':
               'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

from website.models import SenateTerm, Senate, MandateOfSenator, Senator, PoliticalParty, Country, ParliamentaryTerm, \
    Parliament

senate = Senate.objects.get(country="Belgium", name="Senate")
parliament = Parliament.objects.get(country="Belgium", name="Chamber of Representatives")


def add_senators():
    try:
        terms = ParliamentaryTerm.objects.filter(parliament=parliament)
        senate_term = terms[0].term
        beginning_of_term = terms[0].beginning_of_term
        SenateTerm.objects.get_or_create(seats=60, term=senate_term,
                                         senate=senate,
                                         beginning_of_term=terms[0].beginning_of_term,
                                         end_of_term=terms[0].end_of_term)
        pageTree = requests.get(
            "https://www.senate.be/www/?MIval=/WieIsWie/Samenstelling&LANG=nl",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        political_parties = soup.find("map")
        political_parties = political_parties.find_all("area")
        for party in political_parties:
            political_party = party['title']
            link = party['href']
            members_pageTree = requests.get(
                link,
                headers=headers)
            members_soup = BeautifulSoup(members_pageTree.content, 'html.parser')
            members = members_soup.find_all("li")[1:]
            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Belgium"), name=political_party)

            for member in members:
                name = member.get_text()
                name = name.split(" (")[0]
                first_name = name.split()[-1]
                last_name = name.split(" " + first_name)[0]
                senator_link = member.find("a")['href']
                member_pageTree = requests.get(
                    "https://www.senate.be" + senator_link,
                    headers=headers)
                member_soup = BeautifulSoup(member_pageTree.content, 'html.parser')
                member_info = member_soup.find_all("tr", {"bgcolor": "#E3E3E3"})
                for member in member_info:

                    member = member.find("td", {"colspan": "3"})
                    if member is not None:
                        if "Geboren te " in member.get_text():
                            date_of_birth = member.get_text().split("op ")[1]
                            temporary_date_of_birth = date_of_birth.split()[0:3]
                            temporary_date_of_birth[2] = str(
                                ''.join(i for i in temporary_date_of_birth[2] if i.isdigit()))
                            temporary_date_of_birth[1] = replace_belgium_months(temporary_date_of_birth[1])
                            month = temporary_date_of_birth[1]
                            datetime_object = datetime.strptime(month, "%B")
                            month_number = datetime_object.month
                            date_of_birth = " ".join(temporary_date_of_birth)

                            date_before_transform = date_of_birth.replace(f" {month} ", f"-{str(month_number)}-")
                            date_of_birth = datetime.strptime(date_before_transform, '%d-%m-%Y').strftime(
                                '%Y-%m-%d')

                            Senator.objects.get_or_create(first_name=first_name,
                                                          last_name=last_name,
                                                          date_of_birth=date_of_birth)

                            MandateOfSenator.objects.get_or_create(
                                party=PoliticalParty.objects.get(country="Belgium", name=political_party),
                                senate_term=SenateTerm.objects.get(senate=senate, term=senate_term),
                                senate=senate,
                                senator=Senator.objects.get(first_name=first_name,
                                                            last_name=last_name,
                                                            date_of_birth=date_of_birth, ),
                                beginning_of_term=beginning_of_term,
                                end_of_term=None)

                        elif "Geboren in " in member.get_text():

                            date_of_birth = member.get_text().split("op ")[1]
                            temporary_date_of_birth = date_of_birth.split()[0:3]
                            temporary_date_of_birth[2] = str(
                                ''.join(i for i in temporary_date_of_birth[2] if i.isdigit()))
                            temporary_date_of_birth[1] = replace_belgium_months(temporary_date_of_birth[1])
                            month = temporary_date_of_birth[1]
                            datetime_object = datetime.strptime(month, "%B")
                            month_number = datetime_object.month
                            date_of_birth = " ".join(temporary_date_of_birth)

                            date_before_transform = date_of_birth.replace(f" {month} ", f"-{str(month_number)}-")
                            date_of_birth = datetime.strptime(date_before_transform, '%d-%m-%Y').strftime(
                                '%Y-%m-%d')

                            Senator.objects.get_or_create(first_name=first_name,
                                                          last_name=last_name,
                                                          date_of_birth=date_of_birth)

                            MandateOfSenator.objects.get_or_create(
                                party=PoliticalParty.objects.get(country="Belgium", name=political_party),
                                senate_term=SenateTerm.objects.get(senate=senate, term=senate_term),
                                senate=senate,
                                senator=Senator.objects.get(first_name=first_name,
                                                            last_name=last_name,
                                                            date_of_birth=date_of_birth, ),
                                beginning_of_term=beginning_of_term,
                                end_of_term=None)


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def replace_belgium_months(text):
    text = text.replace("januari", "january").replace("februari", "february").replace("maart", "march").replace("mei",
                                                                                                                "may").replace(
        "juni", "june").replace("juli", "july").replace("augustus", "august").replace("oktober", "october")
    return text


if __name__ == "__main__":
    add_senators()
