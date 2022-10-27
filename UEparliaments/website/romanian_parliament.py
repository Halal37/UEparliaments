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

parliament = Parliament.objects.get(country="Romania", name="Chamber of Deputies")


def add_mps(mps, gender):
    months = ["january", "february", "march", "april", "may", "june", "july",
              "august", "september", "october", "november", "december"]
    short_months = ["jan.", "feb.", "mar.", "apr.", "may", "jun.", "jul.",
                    "aug.", "sep.", "oct.", "nov.", "dec."]
    for mp in mps:
        name = mp.find("b").find("a").get_text()
        member_link = mp.find("b").find("a")['href']
        last_name = name.split()[-1]
        first_name = name.split(" " + last_name)[0]
        member_pageTree = requests.get(
            "http://www.cdep.ro" + member_link,
            headers=headers)
        member_soup = BeautifulSoup(member_pageTree.content, 'html.parser')
        political_party = member_soup.find("tr", {"valign": "center"})
        if name == "Stoica Bogdan-Alin":
            political_party = "League of Albanians of Romania"
        else:
            political_party = political_party.find("a").get_text()
        date_of_birth = member_soup.find("td", {"class": "menuoff"}).get_text()
        if "-2022" in date_of_birth:
            date_of_birth = None
        else:
            date_of_birth = date_of_birth.split(".  ")[1]
            for i, month in enumerate(short_months):
                if month in date_of_birth:
                    datetime_object = datetime.strptime(months[i], "%B")
                    month_number = datetime_object.month
                    date_before_transform = date_of_birth.replace(f" {month} ", f"/{str(month_number)}/")
                    temporary_date_before_transform = date_before_transform.split()
                    date_before_transform = "".join(temporary_date_before_transform)
                    date_of_birth = datetime.strptime(date_before_transform, '%d/%m/%Y').strftime('%Y-%m-%d')
        mandate = member_soup.find("table", {"cellpadding": "3"}).find("td", {"width": "100%"}).get_text()
        if "end of the mandate: " in mandate:
            end_of_term = mandate.split("end of the mandate: ")[1].split(" - ")[0]
            for month in months:
                if month in end_of_term:
                    datetime_object = datetime.strptime(month, "%B")
                    month_number = datetime_object.month
                    date_before_transform = end_of_term.replace(f" {month} ", f"/{str(month_number)}/")
                    temporary_date_before_transform = date_before_transform.split()
                    date_before_transform = "".join(temporary_date_before_transform)
                    end_of_term = datetime.strptime(date_before_transform, '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            end_of_term = None
        if "start of the mandate: " in mandate:
            beginning_of_term = mandate.split("start of the mandate: ")[1].split(" - ")[0].split("replaces")[0]
            for month in months:
                if month in beginning_of_term:
                    datetime_object = datetime.strptime(month, "%B")
                    month_number = datetime_object.month
                    date_before_transform = beginning_of_term.replace(f" {month} ", f"/{str(month_number)}/")
                    temporary_date_before_transform = date_before_transform.split()
                    date_before_transform = "".join(temporary_date_before_transform)
                    beginning_of_term = datetime.strptime(date_before_transform, '%d/%m/%Y').strftime('%Y-%m-%d')
        MP.objects.get_or_create(first_name=first_name,
                                 last_name=last_name, gender=gender, date_of_birth=date_of_birth)

        PoliticalParty.objects.get_or_create(
            country=Country.objects.get(country_name="Romania"),
            name=political_party)

        parliamentary_term = ParliamentaryTerm.objects.get(
            parliament=parliament,
            term="56")
        MandateOfMP.objects.get_or_create(
            party=PoliticalParty.objects.get(country="Romania",
                                             name=political_party),
            parliamentary_term=parliamentary_term,
            parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                     last_name=last_name, gender=gender,
                                                     date_of_birth=date_of_birth),
            beginning_of_term=beginning_of_term,
            end_of_term=end_of_term)


def add_current_term_mps_and_political_parties(link):
    try:

        if link[-1] == "F":
            gender = "female"
        elif link[-1] == "M":
            gender = "male"
        pageTree = requests.get(
            link,
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        mps_c = soup.find_all("tr", {"bgcolor": "#fef9c2"})
        mps_c2 = soup.find_all("tr", {"bgcolor": "#fffef2"})
        add_mps(mps_c,gender)
        add_mps(mps_c2, gender)




    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_current_term_mps_and_political_parties("http://www.cdep.ro/pls/parlam/structura.de?leg=2020&idl=2&par=M")
    add_current_term_mps_and_political_parties("http://www.cdep.ro/pls/parlam/structura.de?leg=2020&idl=2&par=F")
