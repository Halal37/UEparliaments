import os
import django
import requests
import logging
import sys
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

parliament = Parliament.objects.get(country="Denmark", name="Folketing")


def member_info(member):
    try:
        link = member.find("a")["href"]
        name = member.get_text()
        first_name = name.split()[0]
        last_name = name.replace(first_name + " ", "").split("(")[0]
        pageTree = requests.get(
            link,
            headers=headers, verify=False)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        political_party = soup.find("p", {"class", "person__container__functionparty"})
        political_party = political_party.get_text().split(",  ")[1]
        member_info = soup.find("div", {"id": "ftMember__accordion__container__tab1"})
        member_info = member_info.find("article").get_text()
        date_of_birth = member_info.split("born ")[1].split(".")[0].split(" in")[0].split(" at")[0].replace("th",
                                                                                                            "").replace(
            "nd ", " ").replace("1st", "1").replace("21st", "21")
        month = date_of_birth.split()[0]
        datetime_object = datetime.strptime(month, "%B")
        month_number = datetime_object.month

        date_before_transform = date_of_birth.replace(f"{month} ", f"{str(month_number)}-")
        date_of_birth = datetime.strptime(date_before_transform, '%m-%d %Y').strftime(
            '%Y-%m-%d')
        return date_of_birth, first_name, last_name, political_party

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def member_by_political_party(link, political_party, name):
    try:
        terms = ParliamentaryTerm.objects.get(parliament=parliament)
        parliamentary_term = terms.term
        beginning_of_term = terms.beginning_of_term
        pageTree = requests.get(
            link,
            headers=headers, verify=False)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        last_name = name.split()[-1]
        first_name = name.split(" " + last_name)[0]

        member_info = soup.find("div", {"id": "ftMember__accordion__container__tab1"})
        member_info = member_info.find("article").get_text()
        if " born on " in member_info:
            date_of_birth = \
                member_info.split("born on ")[1].replace("13.", "13").replace("29.", "29").split(".")[0].split(" in ")[
                    0].split(" at")[0].split(" on")[
                    0].replace("th",
                               "").replace(
                    "nd ", " ").replace("1st", "1").replace("21st", "21").replace("3rd", "3").split(",")[0].replace(
                    "Juni",
                    "June").split(
                    "\xa0in ")[0].replace("Juny", "June")
        elif "Vanopslagh, born in Épernay" in member_info:
            date_of_birth = None
        else:
            date_of_birth = \
                member_info.split("born ")[1].replace("13.", "13").replace("29.", "29").split(".")[0].split(" in ")[
                    0].split(" at")[0].split(" on")[
                    0].replace("th",
                               "").replace(
                    "nd ", " ").replace("1st", "1").replace("21st", "21").replace("3rd", "3").split(",")[0].replace(
                    "Juni",
                    "June").split(
                    "\xa0in ")[0].replace("Juny", "June")
        if date_of_birth == None:
            pass
        elif date_of_birth[0].isdigit():
            month = date_of_birth.split()[1]

            datetime_object = datetime.strptime(month, "%B")
            month_number = datetime_object.month

            date_before_transform = date_of_birth.replace(f" {month} ", f"-{str(month_number)}-")
            date_of_birth = datetime.strptime(date_before_transform, '%d-%m-%Y').strftime(
                '%Y-%m-%d')
        else:

            month = date_of_birth.split()[0]
            datetime_object = datetime.strptime(month, "%B")
            month_number = datetime_object.month

            date_before_transform = date_of_birth.replace(f"{month} ", f"{str(month_number)}-")
            date_of_birth = datetime.strptime(date_before_transform, '%m-%d %Y').strftime(
                '%Y-%m-%d')

        MP.objects.get_or_create(first_name=first_name,
                                 last_name=last_name,
                                 date_of_birth=date_of_birth)
        exists = MandateOfMP.objects.filter(
            party=PoliticalParty.objects.get(country="Denmark", name=political_party),
            parliamentary_term=ParliamentaryTerm.objects.get(
                parliament=parliament,
                term=parliamentary_term),
            parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                     last_name=last_name,
                                                     date_of_birth=date_of_birth), )

        if len(exists) > 0:
            return

        MandateOfMP.objects.get_or_create(
            party=PoliticalParty.objects.get(country="Denmark", name=political_party),
            parliamentary_term=ParliamentaryTerm.objects.get(
                parliament=parliament,
                term=parliamentary_term),
            parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                     last_name=last_name,
                                                     date_of_birth=date_of_birth),
            beginning_of_term=beginning_of_term,
            end_of_term=None)


    except Exception as e:
        print("Could not save: ")
        print(e)

    print("Action complete!")


def political_parties(link, political_party):
    try:
        pageTree = requests.get(
            link,
            headers=headers, verify=False)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        members = soup.find("tbody")
        members = members.find_all("tr", {"tabindex": "0"})
        for member in members:
            name = member.find("img")["alt"]
            link = member.find("td", {"class": "filtered"})
            link = link.find("a")["href"]
            member_by_political_party(link, political_party, name)


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_mps_and_political_paries():
    try:
        pageTree = requests.get(
            "https://www.thedanishparliament.dk/en/members/members-in-party-groups",
            headers=headers, verify=False)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        parties = soup.find("table", {"class": "telbogTable members-groups"})

        parties = parties.find("tbody")
        parties = parties.find_all("tr")
        for party in parties:
            party.find("td")
            political_party = party.find("a").get_text()
            link = party.find("a")["href"]
            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Denmark"), name=political_party)
            political_parties("https://www.thedanishparliament.dk" + link + "&pageSize=100", political_party)


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def entered_during_term():
    try:
        terms = ParliamentaryTerm.objects.get(parliament=parliament)
        parliamentary_term = terms.term
        beginning_of_term = terms.beginning_of_term
        pageTree = requests.get(
            "https://www.thedanishparliament.dk/en/members/entered-parliament-during-the-electoral-period",
            headers=headers, verify=False)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        parties = soup.find("div", {"class": "ftMembersOnLeave"})

        members = parties.find_all("table", {"class": "telbogTable"})
        for member in members:
            dates = member.find("th")
            end_of_mandate = dates.find("span").get_text()
            end_of_mandate = end_of_mandate.replace(".", "").replace("februar", "february").replace("juni",
                                                                                                    "june").replace(
                "oktober", "october")

            month = end_of_mandate.split()[1]
            datetime_object = datetime.strptime(month, "%B")
            month_number = datetime_object.month

            date_before_transform = end_of_mandate.replace(f" {month} ", f"-{str(month_number)}-")
            end_of_mandate = datetime.strptime(date_before_transform, '%d-%m-%Y').strftime(
                '%Y-%m-%d')
            beginning_of_mandate = end_of_mandate
            datetime_object = datetime.strptime(end_of_mandate, '%Y-%m-%d')
            end_of_mandate = datetime_object - timedelta(1)
            end_of_mandate = end_of_mandate.strftime(
                '%Y-%m-%d')
            first_member = member.find_all("div", {"class": "cellInfo"})
            second_member = first_member[1]
            first_member = first_member[0]
            date_of_birth, first_name, last_name, political_party = member_info(first_member)

            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Denmark"), name=political_party)
            MP.objects.get_or_create(first_name=first_name,
                                     last_name=last_name,
                                     date_of_birth=date_of_birth)
            MandateOfMP.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Denmark", name=political_party),
                parliamentary_term=ParliamentaryTerm.objects.get(
                    parliament=parliament,
                    term=parliamentary_term),
                parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                         last_name=last_name,
                                                         date_of_birth=date_of_birth),
                beginning_of_term=beginning_of_term,
                end_of_term=end_of_mandate)
            date_of_birth, first_name, last_name, political_party = member_info(second_member)

            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Denmark"), name=political_party)
            MP.objects.get_or_create(first_name=first_name,
                                     last_name=last_name,
                                     date_of_birth=date_of_birth)
            MandateOfMP.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Denmark", name=political_party),
                parliamentary_term=ParliamentaryTerm.objects.get(
                    parliament=parliament,
                    term=parliamentary_term),
                parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                         last_name=last_name,
                                                         date_of_birth=date_of_birth),
                beginning_of_term=beginning_of_mandate,
                end_of_term=None)




    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    entered_during_term()
    add_mps_and_political_paries()
