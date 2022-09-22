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

headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
           'Accept':
               'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

parliament = Parliament.objects.get(country="Cyprus", name="House of Representatives")


def add_political_parties_and_mps():
    try:
        cypriot_terms = ParliamentaryTerm.objects.get(parliament=parliament)
        parliamentary_term = cypriot_terms.term
        months = ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"]
        pageTree = requests.get(
            "http://www.parliament.cy/en/composition/members-of-the-house/biographical-notes",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        script = soup.find("section", {"id": "generic_section"})
        members = script.find_all("div", {"class": "greybox2"})
        for member in members:
            name = member.find("h2").get_text()
            first_name = name.split()[-1]
            last_name = name.split(" " + first_name)[0].replace("Dr ", "").lower().title()
            link = member.find("a")['href']
            member_pageTree = requests.get(
                f"http://www.parliament.cy{link}",
                headers=headers)
            member_soup = BeautifulSoup(member_pageTree.content, 'html.parser')
            political_party = member_soup.find_all("section")

            if "PRESIDENT OF THE HOUSE OF REPRESENTATIVES" in political_party[2].find("strong").get_text():
                if "(" in political_party[2].find_all("strong")[1].get_text():
                    party = political_party[2].find_all("strong")[1].get_text().split("(")[1].replace(")", "").replace(
                        "PRESIDENT OF ", "").replace("ELAM ", "ELAM")
                else:
                    party = political_party[2].find_all("strong")[1].get_text()
            elif "INDEPENDENT " in political_party[2].find("strong").get_text():
                party = "Independent"
            else:
                if "(" in political_party[2].find("strong").get_text().split("CONSTITUENCY")[1].replace('\r\n',
                                                                                                        '').replace(",",
                                                                                                                    ""):
                    party = \
                        political_party[2].find("strong").get_text().split("CONSTITUENCY")[1].replace('\r\n',
                                                                                                      '').replace(
                            ",",
                            "").split(
                            "(")[1].replace(")", "").replace("PRESIDENT OF ", "").replace("ELAM ", "ELAM")
                elif '' is political_party[2].find("strong").get_text().split("CONSTITUENCY")[1]:
                    if "(" in political_party[2].find_all("strong")[1].get_text():
                        party = political_party[2].find_all("strong")[1].get_text().split("(")[1].replace(")",
                                                                                                          "").replace(
                            "PRESIDENT OF ", "").replace("ELAM ", "ELAM")
                    else:
                        party = political_party[2].find_all("strong")[1].get_text().replace("PRESIDENT OF ",
                                                                                            "").replace("ELAM ", "ELAM")

                else:
                    party = political_party[2].find("strong").get_text().split("CONSTITUENCY")[1].replace('\r\n',
                                                                                                          '').replace(
                        ",", "").replace("PRESIDENT OF ", "").replace("ELAM ", "ELAM")
            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Cyprus"), name=party)
            term = ParliamentaryTerm.objects.filter(parliament=parliament)[0].beginning_of_term
            bio = member_soup.find_all("p", {"style": "margin-left: 40px;"})
            if len(bio) is 0:
                bio = member_soup.find_all("div", {"style": "margin-left: 40px;"})
                date = bio[1].get_text().split(", ")[-1].replace(".", "").replace('.\xa0', "").replace(".", "").replace(
                    '\xa0', " ")
                for element in bio:
                    if "Representative of " in element.get_text():
                        if "since " in element.get_text():
                            election = element.get_text().split("since ")[1].split(".")[0]  # .replace(".", "")
                            for month in months:
                                if month in election:
                                    datetime_object = datetime.strptime(month, "%B")
                                    month_number = datetime_object.month
                                    date_before_transform = election.replace(f"{month} ", f"01-{str(month_number)}-")
                                    date_mandate = datetime.strptime(date_before_transform, '%d-%m-%Y').strftime(
                                        '%Y-%m-%d')
                                    if str(term) > date_mandate:
                                        beginning_of_term = str(term)
                                    else:
                                        beginning_of_term = date_mandate
                                    break
                                if month not in date and month is "December":
                                    date_mandate = election+"-01-01"
                                    if str(term) > date_mandate:
                                        beginning_of_term = str(term)
                                    else:
                                        beginning_of_term = date_mandate
                for month in months:
                    if month in date:
                        datetime_object = datetime.strptime(month, "%B")
                        month_number = datetime_object.month
                        date_before_transform = date.replace(f" {month} ", f"/{str(month_number)}/")
                        date_of_birth = datetime.strptime(date_before_transform, '%d/%m/%Y').strftime('%Y-%m-%d')
                        break
                    if month not in date and month is "December":
                        date_of_birth = None
            else:
                date = bio[0].get_text().split(", ")[-1].replace('.\xa0', "").replace(".", "").replace('\xa0', " ")
                for month in months:
                    if month in date:
                        datetime_object = datetime.strptime(month, "%B")
                        month_number = datetime_object.month
                        date_before_transform = date.replace(f" {month} ", f"/{str(month_number)}/")
                        date_of_birth = datetime.strptime(date_before_transform, '%d/%m/%Y').strftime('%Y-%m-%d')
                        break
                    if month not in date and month is "December":
                        date_of_birth = None
                for element in bio:
                    if "Representative of " in element.get_text():
                        if "since " in element.get_text():
                            election = element.get_text().split("since ")[1].split(".")[0]
                            for month in months:
                                if month in election:
                                    datetime_object = datetime.strptime(month, "%B")
                                    month_number = datetime_object.month

                                    date_before_transform = election.replace(f"{month} ", f"01-{str(month_number)}-")
                                    date_mandate = datetime.strptime(date_before_transform, '%d-%m-%Y').strftime(
                                        '%Y-%m-%d')
                                    if str(term) > date_mandate:
                                        beginning_of_term = str(term)
                                    else:
                                        beginning_of_term = date_mandate
                                    break
                                if month is "December":
                                    date_mandate = election + "-01-01"
                                    if str(term) > date_mandate:
                                        beginning_of_term = str(term)
                                    else:
                                        beginning_of_term = date_mandate

                        else:
                            date_mandate = element.get_text().split(", ")[1].split("-")[0] + "-01-01"
                            if str(term) > date_mandate:
                                beginning_of_term = str(term)
                            else:
                                beginning_of_term = date_mandate

            MP.objects.get_or_create(first_name=first_name,
                                         last_name=last_name,
                                         date_of_birth=date_of_birth)
            MandateOfMP.objects.get_or_create(
                    party=PoliticalParty.objects.get(country="Cyprus", name=party),
                    parliamentary_term=ParliamentaryTerm.objects.get(
                        parliament=parliament,
                        term=parliamentary_term),
                    parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                             last_name=last_name,
                                                             date_of_birth=date_of_birth),
                    beginning_of_term=str(beginning_of_term),
                    end_of_term=None)

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_political_parties_and_mps()
