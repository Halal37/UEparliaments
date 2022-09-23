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

senate = Senate.objects.get(country="Germany", name="Bundesrat")


def add_political_parties_and_senators():
    try:
        months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
                  "November", "Dezember"]

        for i in range(2, 18):
            pageTree = requests.get(
                f"https://www.bundesrat.de/DE/bundesrat/mitglieder/mitglieder-node.html?cms_param1=state-{i}",
                headers=headers)
            soup = BeautifulSoup(pageTree.content, 'html.parser')
            script = soup.find("div", {"class": "module type-1 members"})
            senators = script.find("ul", {"class": "members-list"})
            for senator in senators:
                gender = None
                political_party = senator.find("span", {"class": "organization-name"}).get_text()
                name = senator.find_all("a")[1].get_text().split("\xa0")[0].replace("Dr. ", "").replace("Prof. ", "")
                last_name = name.split()[-1]
                first_name = name.split(" " + last_name)[0]
                description = senator.find_all("h3")
                for line in description:
                    text = line.get_text()

                    if "Minister" in text or "minister" in text:
                        gender = "male"
                    if "Ministerin" in text or "ministerin" in text:
                        gender = "female"

                    if "Senator" in text or "senator" in text or "senator, " in text or "Senator, " in text:
                        gender = "male"
                    if "Senatorin" in text or "senatorin" in text or "senatorin, " in text or "Senatorin, " in text:
                        gender = "female"

                    if "Bürgermeister" in text or "bürgermeister" in text:
                        gender = "male"
                    if "Bürgermeisterin" in text or "bürgermeisterin" in text:
                        gender = "female"

                    if "Staatssekretär" in text:
                        gender = "male"
                    if "Staatssekretärin" in text:
                        gender = "female"

                    if "Präsident" in text or "präsident" in text:
                        gender = "male"
                    if "Präsidentin" in text or "präsidentin" in text:
                        gender = "female"

                    if "Bevollmächtigter" in text or "bevollmächtigter" in text:
                        gender = "male"
                    if "Bevollmächtigterin" in text or "bevollmächtigterin" in text:
                        gender = "female"

                link = senator.find_all("a")[1]["href"]
                senator_pageTree = requests.get(
                    f"https://www.bundesrat.de/{link}",
                    headers=headers)
                senator_soup = BeautifulSoup(senator_pageTree.content, 'html.parser')
                details = senator_soup.find("div", {"class": "module type-2 member member-furtherdetails"})
                date_of_birth = details.find("p").get_text().split("Geboren ")[1]
                if "am " in date_of_birth:
                    date_of_birth = date_of_birth.split("am ")[1]
                if " in " in date_of_birth:
                    date_of_birth = date_of_birth.split(" in ")[0]
                if ". " in date_of_birth:
                    date_of_birth = date_of_birth.replace(". ", ".")
                if "Verheiratet" in date_of_birth:
                    date_of_birth = date_of_birth.split("Verheiratet")[0]
                    date_of_birth = date_of_birth.split()[0]
                if " " in date_of_birth:
                    date_of_birth = date_of_birth.replace(" ", ".")
                if date_of_birth[-1] is "." or date_of_birth[-1] is ",":
                    date_of_birth = date_of_birth[:-1]

                for month in months:
                    if month in date_of_birth:
                        month_number = str(int(months.index(month)) + 1)
                        date_of_birth = date_of_birth.replace(f"{month}", f"{month_number}")
                date_of_birth = datetime.strptime(date_of_birth, '%d.%m.%Y').strftime(
                    '%Y-%m-%d')
                mandate = details.find_all("p")[-1].get_text()

                if "Stellvertretendes Mitglied des Bundesrates vom" in mandate:
                    if ", seit diesem " in mandate:
                        mandate = mandate.split(", seit diesem ")[0][-10:]
                    if "seit " in mandate:
                        mandate = mandate.split("seit ")[1][0:10]
                    if "Seit " in mandate:
                        mandate = mandate.split("Seit ")[1][0:10]
                    if mandate[-1] is "." or mandate[-1] is ",":
                        mandate = mandate[:-1]
                    mandate = datetime.strptime(mandate, '%d.%m.%Y').strftime(
                        '%Y-%m-%d')

                elif "Mitglied des Bundesrates seit " in mandate:
                    mandate = mandate.split("Mitglied des Bundesrates seit ")[1].replace("\n", "")
                    if " " in mandate:
                        mandate = mandate.split(" ")[0]
                    if mandate[-1] is "." or mandate[-1] is ",":
                        mandate = mandate[:-1]
                    mandate = datetime.strptime(mandate, '%d.%m.%Y').strftime(
                        '%Y-%m-%d')

                else:
                    if "Präsident des " in mandate:
                        mandate = details.find_all("p")[-2].get_text()
                    if "sei " in mandate:
                        mandate = mandate.split("sei ")[1][0:10]
                    if " Stellvertretendes Mitglied des Bundesrates, seit diesem " in mandate:
                        mandate = mandate.split(" Stellvertretendes Mitglied des Bundesrates, seit diesem ")[0][-10:]
                    if " Seit " in mandate:
                        mandate = mandate.split(" Seit ")[1][0:10]
                    if " erneut seit " in mandate:
                        mandate = mandate.split(" erneut seit ")[1][0:10]
                    if ", seit diesem " in mandate:
                        mandate = mandate.split(", seit diesem ")[0][-10:]
                    if ", seit " in mandate:
                        mandate = mandate.split(", seit ")[0][-10:]
                    mandate = datetime.strptime(mandate, '%d.%m.%Y').strftime(
                        '%Y-%m-%d')

                PoliticalParty.objects.get_or_create(
                    country=Country.objects.get(country_name="Germany"), name=political_party)
                Senator.objects.get_or_create(first_name=first_name,
                                              last_name=last_name,
                                              gender=gender,
                                              date_of_birth=date_of_birth,)

                MandateOfSenator.objects.get_or_create(
                    party=PoliticalParty.objects.get(country="Germany", name=political_party),
                    senate_term=SenateTerm.objects.get(senate=senate, term="1"),
                    senate=senate,
                    senator=Senator.objects.get(first_name=first_name,
                                                last_name=last_name,
                                                gender=gender,
                                                date_of_birth=date_of_birth),
                    beginning_of_term=mandate,
                    end_of_term=None)


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_political_parties_and_senators()
