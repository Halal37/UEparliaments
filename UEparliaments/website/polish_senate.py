import os
import django
import logging
import sys
from datetime import datetime
from bs4 import BeautifulSoup
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

logger = logging.getLogger(__name__)
os.environ['DJANGO_SETTINGS_MODULE'] = 'UEparliaments.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UEparliaments.settings")

django.setup()
from website.models import SenateTerm, Senate, MandateOfSenator, Senator, PoliticalParty, Country, Parliament, \
    ParliamentaryTerm

headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
           'Accept':
               'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

senate = Senate.objects.get(country="Poland", name="Senate")
parliament = Parliament.objects.get(country="Poland", name="Sejm")


def add_senators(link, term):
    try:
        senate_term = SenateTerm.objects.get(senate=senate, term=term)
        pageTree = requests.get(
            link,
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        members = soup.find_all("div", {"class": "senator-kontener"})
        for member in members:
            link = member.find("a")['href']
            name = member.find("a").get_text()
            last_name = name.split()[-1]
            first_name = name.split(" " + last_name)[0]
            if first_name[-1] is "a":
                if first_name == "Jan Maria":
                    gender = "male"
                else:
                    gender = "female"
            else:
                gender = "male"
            member_pageTree = requests.get(
                "https://www.senat.gov.pl" + link,
                headers=headers)
            member_soup = BeautifulSoup(member_pageTree.content, 'html.parser')

            description = member_soup.find("div", {"class": "description"}).get_text()
            if "urodził się " in description:
                date_of_birth = \
                    description.split("urodził się ")[1].split(" r.")[0].split("\xa0r.")[0].split(" roku")[0].split(
                        " w ")[
                        0].replace("\xa0", " ")
            if "Urodził się " in description:
                date_of_birth = \
                    description.split("Urodził się ")[1].split(" r.")[0].split("\xa0r.")[0].split(" roku")[0].split(
                        " w ")[
                        0].replace("\xa0", " ")
            elif "Urodziła się " in description:
                date_of_birth = \
                    description.split("Urodziła się ")[1].split(" r.")[0].split("\xa0r.")[0].split(" roku")[0].split(
                        " w ")[
                        0].replace("\xa0", " ")
            elif "urodziła się " in description:
                date_of_birth = \
                    description.split("urodziła się ")[1].split(" r.")[0].split("\xa0r.")[0].split(" roku")[0].split(
                        " w ")[
                        0].replace("\xa0", " ")
            date_of_birth = replace_polish_months(date_of_birth)
            month = date_of_birth.split()[1]

            datetime_object = datetime.strptime(month, "%B")
            month_number = datetime_object.month

            date_before_transform = date_of_birth.replace(f" {month} ", f"-{str(month_number)}-")
            date_of_birth = datetime.strptime(date_before_transform, '%d-%m-%Y').strftime(
                '%Y-%m-%d')
            Senator.objects.get_or_create(first_name=first_name,
                                          last_name=last_name,
                                          date_of_birth=date_of_birth,
                                          gender=gender)
            political_parties = member_soup.find("div", {"class": "kluby"}).find_all("li")

            for party in political_parties:
                political_party = party.find("a")['title'].replace("Klub Parlamentarny ", "").replace(
                    "Koło Parlamentarne ", "").replace("Koło Senatorów ", "")
                political_party = political_party.split(" – ")[0].split(" - ")[0]

                if "Niezależnych" == political_party or "Senatorowie niezrzeszeni" == political_party:
                    political_party = "Independent"
                elif "Koalicyjny Lewicy" == political_party:
                    political_party = "Lewica"
                elif "Polska 2050" == political_party:
                    political_party = "Polska2050"
                elif "Porozumienie Jarosława Gowina" == political_party:
                    political_party = "Porozumienie"
                else:
                    temporary_political_party = [s[0] for s in political_party.split()]
                    political_party = "".join(temporary_political_party)
                term_time = party.find("p").get_text()
                beginning_of_term = term_time.split("Od: ")[1]
                temporary_beginning_of_term = beginning_of_term.split()
                beginning_of_term = " ".join(temporary_beginning_of_term)
                beginning_of_term = beginning_of_term.split(" r")[0]
                beginning_of_term = datetime.strptime(beginning_of_term, '%d.%m.%Y').strftime(
                '%Y-%m-%d')
                if "Do: " in term_time:
                    end_of_term = term_time.split("Do: ")[1]
                    temporary_end_of_term = end_of_term.split()
                    end_of_term = " ".join(temporary_end_of_term)
                    end_of_term = end_of_term.split(" r")[0]
                    end_of_term = datetime.strptime(end_of_term, '%d.%m.%Y').strftime(
                '%Y-%m-%d')
                else:
                    end_of_term = None

                PoliticalParty.objects.get_or_create(
                    country=Country.objects.get(country_name="Poland"), name=political_party)
                if end_of_term == None:
                    MandateOfSenator.objects.get_or_create(
                        party=PoliticalParty.objects.get(country="Poland", name=political_party),
                        senate_term=SenateTerm.objects.get(senate=senate, term=senate_term),
                        senate=senate,
                        senator=Senator.objects.get(first_name=first_name,
                                                    last_name=last_name,
                                                    date_of_birth=date_of_birth, ),
                        beginning_of_term=beginning_of_term,
                        end_of_term=senate_term.end_of_term)
                else:
                    MandateOfSenator.objects.get_or_create(
                        party=PoliticalParty.objects.get(country="Poland", name=political_party),
                        senate_term=SenateTerm.objects.get(senate=senate, term=senate_term),
                        senate=senate,
                        senator=Senator.objects.get(first_name=first_name,
                                                    last_name=last_name,
                                                    date_of_birth=date_of_birth, ),
                        beginning_of_term=beginning_of_term,
                        end_of_term=end_of_term)



    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_senate_terms():
    try:
        terms = ParliamentaryTerm.objects.filter(parliament=parliament)
        for term in terms:
            parliamentary_term = int(term.term) + 1
            SenateTerm.objects.get_or_create(seats=100, term=str(parliamentary_term),
                                             senate=senate,
                                             beginning_of_term=term.beginning_of_term,
                                             end_of_term=term.end_of_term)
    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def replace_polish_months(text):
    text = text.replace("stycznia", "january").replace("lutego", "february").replace("marca", "march").replace(
        "kwietnia", "april").replace("maja",
                                     "may").replace(
        "czerwca", "june").replace("lipca", "july").replace("sierpnia", "august").replace("września",
                                                                                          "september").replace(
        "października", "october").replace("listopada", "november").replace("grudnia", "december")
    return text


if __name__ == "__main__":
    add_senate_terms()
    add_senators("https://www.senat.gov.pl/sklad/senatorowie/", 10)
    add_senators("https://www.senat.gov.pl/sklad/senatorowie/?kadencja=9", 9)
