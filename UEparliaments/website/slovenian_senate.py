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

senate = Senate.objects.get(country="Slovenia", name="National Council")


def add_terms():
    try:
        SenateTerm.objects.get_or_create(seats=40, term=str(6),
                                         senate=senate,
                                         beginning_of_term="2017-12-12",
                                         end_of_term="2023-12-12")

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_senators():
    try:
        headers = {'User-Agent':
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
                   'Accept':
                       'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}
        months = ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"]
        pageTree = requests.get(
            "https://ds-rs.si/en/current-mandate/members-national-council",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        script = soup.find("div", {"class": "view-content"})
        members = script.find_all("div", {"class": "team-item flip_effect"})
        count = 0
        for member in members:
            name = member.find("div", {"class": "person_name"}).get_text().replace("M.Sc. ", "").replace("Dr. ", "")
            last_name = name.split()[-1]
            first_name = name.split(" " + last_name)[0]
            link = member.find("a", {"class": "arrow_btn"})['href']
            member_pageTree = requests.get(
                f"https://ds-rs.si{link}",
                headers=headers)
            member_soup = BeautifulSoup(member_pageTree.content, 'html.parser')
            bio = member_soup.find("div", {"class": "person_desc"}).get_text()
            count += 1
            if "She " in bio or " She " in bio or " she " in bio:
                gender = "female"
            if "He " in bio or " He " in bio or " he " in bio:
                gender = "male"
            if "born in " in bio:
                date_of_birth = None
            elif "Born in " in bio:
                date = bio.split("Born in ")[1].split(" on ")[1].split(".")[0].replace(".", "")
                for month in months:
                    if month in date:
                        datetime_object = datetime.strptime(month, "%B")
                        month_number = datetime_object.month
                        date_before_transform = date.replace(f" {month} ", f"/{str(month_number)}/")
                        date_of_birth = datetime.strptime(date_before_transform, '%d/%m/%Y').strftime('%Y-%m-%d')


            elif "born " in bio or "Born " in bio:
                date = bio.split("born on ")[1].split(" in")[0]
                for month in months:
                    if month in date:
                        datetime_object = datetime.strptime(month, "%B")
                        month_number = datetime_object.month
                        if "th" in date:
                            date_before_transform = date.replace(f"{month} ", f"{str(month_number)}/").replace("th ",
                                                                                                               "/")
                            date_of_birth = datetime.strptime(date_before_transform, '%m/%d/%Y').strftime('%Y-%m-%d')
                        elif "nd" in date:
                            date_before_transform = date.replace(f"{month} ", f"{str(month_number)}/").replace("nd ",
                                                                                                               "/")
                            date_of_birth = datetime.strptime(date_before_transform, '%m/%d/%Y').strftime('%Y-%m-%d')
                        else:
                            date_before_transform = date.replace(f" {month} ", f"/{str(month_number)}/")
                            date_of_birth = datetime.strptime(date_before_transform, '%d/%m/%Y').strftime('%Y-%m-%d')
            if "BIOGRAPHY:" in bio:
                bio = bio.split("BIOGRAPHY:")[1]
            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Slovenia"), name="Independent")
            Senator.objects.get_or_create(first_name=first_name,
                                          last_name=last_name,
                                          gender=gender,
                                          date_of_birth=date_of_birth,
                                          biographical_notes=bio)

            MandateOfSenator.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Slovenia", name="Independent"),
                senate_term=SenateTerm.objects.get(senate=senate, term="6"),
                senate=senate,
                senator=Senator.objects.get(first_name=first_name,
                                            last_name=last_name,
                                            gender=gender,
                                            date_of_birth=date_of_birth,
                                            biographical_notes=bio),
                beginning_of_term="2017-12-12",
                end_of_term=None)

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_terms()
    add_senators()
