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

parliament = Parliament.objects.get(country="Croatia", name="Parliament")


def add_terms():
    try:
        pageTree = requests.get(
            "https://www.sabor.hr/en/mps",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        terms = soup.find("select", {"class": "filter-main-select form-select"})
        croatian_terms = terms.find_all("option")
        for element in croatian_terms:
            if " term " in element.get_text():
                term_value = element["value"]
                term_number = element.get_text().split("th ")[0]
                if " - " in element.get_text():
                    dates = element.get_text().split("(")[1].split(")")[0].split(" - ")
                    beginning_of_term = dates[0]
                    end_of_term = dates[1]
                    month = beginning_of_term.split()[1]
                    datetime_object = datetime.strptime(month, "%B")
                    month_number = datetime_object.month

                    date_before_transform = beginning_of_term.replace(f" {month} ", f"-{str(month_number)}-")
                    beginning_of_term = datetime.strptime(date_before_transform, '%d-%m-%Y').strftime(
                        '%Y-%m-%d')

                    month = end_of_term.split()[1]
                    datetime_object = datetime.strptime(month, "%B")
                    month_number = datetime_object.month

                    date_before_transform = end_of_term.replace(f" {month} ", f"-{str(month_number)}-")
                    end_of_term = datetime.strptime(date_before_transform, '%d-%m-%Y').strftime(
                        '%Y-%m-%d')

                else:
                    beginning_of_term = element.get_text().split("(")[1].split(")")[0]
                    month = beginning_of_term.split()[1]
                    datetime_object = datetime.strptime(month, "%B")
                    month_number = datetime_object.month

                    date_before_transform = beginning_of_term.replace(f" {month} ", f"-{str(month_number)}-")
                    beginning_of_term = datetime.strptime(date_before_transform, '%d-%m-%Y').strftime(
                        '%Y-%m-%d')

                    end_of_term = None
                if term_number is "5":
                    seats = 152
                elif term_number is "6":
                    seats = 153
                else:
                    seats = 151
                ParliamentaryTerm.objects.get_or_create(seats=seats, term=term_number,
                                                        parliament=parliament,
                                                        beginning_of_term=
                                                        beginning_of_term,
                                                        end_of_term=end_of_term)
    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_mps_and_political_parties(link, gender):
    try:
        pageTree = requests.get(
            link,
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        members = soup.find("tbody")
        members = members.find_all("tr")
        for member in members:
            political_party = member.find("td", {"class": "views-field views-field-entity-path-1"}).get_text().split()
            name = member.find("td", {"headers": "view-field-prezime-table-column"}).get_text()
            name = name.replace("\n", "")
            last_name = name.split(",")[0]
            if len(last_name.split()) > 1:
                last_name = last_name.split()
                temporary_last_name = ' '.join(last_name)
                last_name = temporary_last_name
            else:
                last_name = last_name.replace(" ", "")
            first_name = name.split(",")[1]
            first_name = first_name.replace(" ", "")
            term = member.find("td", {"headers": "view-field-saziv-table-column"}).get_text().split("th")[0]
            if len(political_party) == 0:
                political_party = "Indepentend"
            else:
                political_party = " ".join(political_party)

            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Croatia"), name=political_party)

            link = member.find("td", {"headers": "view-field-prezime-table-column"}).find("a")
            if member.find("td", {"headers": "view-field-prezime-table-column"}).find("a", {
                "class": "no-link-list"}) is not None:
                continue
            else:
                link = link['href']
                link = link.split()[0]

            member_pageTree = requests.get(
                f"https://www.sabor.hr{link}",
                headers=headers)
            member_soup = BeautifulSoup(member_pageTree.content, 'html.parser')
            beginning_of_term = member_soup.find("div",
                                                 {
                                                     "class": "views-field views-field-field-pocetak-mandata-1"}).get_text().replace(
                "\n", "").replace("\t", "")
            month = beginning_of_term.split()[1]
            datetime_object = datetime.strptime(month, "%B")
            month_number = datetime_object.month

            date_before_transform = beginning_of_term.replace(f" {month} ", f"-{str(month_number)}-")
            beginning_of_term = datetime.strptime(date_before_transform, '%d-%m-%Y').strftime(
                '%Y-%m-%d')

            if member_soup.find("div",
                                {"class": "views-field views-field-field-zavrsetak-mandata-1"}) is not None:
                end_of_term = member_soup.find("div",
                                               {
                                                   "class": "views-field views-field-field-zavrsetak-mandata-1"}).get_text().replace(
                    "\n", "").replace("\t", "")
                month = end_of_term.split()[1]
                datetime_object = datetime.strptime(month, "%B")
                month_number = datetime_object.month

                date_before_transform = end_of_term.replace(f" {month} ", f"-{str(month_number)}-")
                end_of_term = datetime.strptime(date_before_transform, '%d-%m-%Y').strftime(
                    '%Y-%m-%d')

            else:
                end_of_term = None
            date_of_birth = member_soup.find("div", {"class": "zivotopis"}).get_text()
            if "Born on " in date_of_birth:
                date_of_birth = date_of_birth.split(" in ")[0]
                date_of_birth = date_of_birth.split(" at ")[0]
                date_of_birth = date_of_birth.replace("8.", "8").replace("21.", "21").replace("19.", "19").replace(
                    "May 1,",
                    "1 May").replace(
                    "Yanuary", "January").replace("November 3,", "3 November").replace("1 November.",
                                                                                       "1 November 1950.")
                date_of_birth = date_of_birth.split(".")[0]
                date_of_birth = date_of_birth.replace("Born on ", "")
                date_of_birth = date_of_birth.split(" on ")[0]
                date_of_birth = date_of_birth.replace("\n", "")
                date_of_birth = date_of_birth.replace(".\xa0", "").replace("th", "").replace("\xa0", " ").replace(".",
                                                                                                                  "").replace(
                    "rd", "").replace("nd", "").replace(", St", "").replace("Februrary", "February").replace(
                    "January1945",
                    "January 1945").replace(
                    "27January", "27 January").replace(",", "").replace("1st", "1")
                date_of_birth = date_of_birth.split(" in ")[0]
                date_of_birth = date_of_birth.split()
                temporary_date_of_birth = ' '.join(date_of_birth)
                date_of_birth = temporary_date_of_birth
                month = date_of_birth.split()[1]
                datetime_object = datetime.strptime(month, "%B")
                month_number = datetime_object.month

                date_before_transform = date_of_birth.replace(f" {month} ", f"-{str(month_number)}-")
                date_of_birth = datetime.strptime(date_before_transform, '%d-%m-%Y').strftime(
                    '%Y-%m-%d')
            else:
                date_of_birth = None

            MP.objects.get_or_create(first_name=first_name,
                                     last_name=last_name,
                                     gender=gender,
                                     date_of_birth=date_of_birth)
            MandateOfMP.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Croatia", name=political_party),
                parliamentary_term=ParliamentaryTerm.objects.get(
                    parliament=parliament,
                    term=term),
                parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                         last_name=last_name,
                                                         gender=gender,
                                                         date_of_birth=date_of_birth),
                beginning_of_term=beginning_of_term,
                end_of_term=end_of_term)

        if soup.find("li", {"class": "pager__item pager__item--next"}) is not None:
            next_link = soup.find("li", {"class": "pager__item pager__item--next"}).find("a")['href']
            add_mps_and_political_parties(f"https://www.sabor.hr/en/mps{next_link}", gender)

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_terms()
    add_mps_and_political_parties(
        "https://www.sabor.hr/en/mps?field_saziv_target_id_all=all&field_prezime_value=&stranka_id_all=&field_izborna_jedinica_target_id_all=&field_izborna_lista_target_id_all=&field_spol_target_id=102&field_status_mandata_target_id=all&page=0%2C0",
        "female")

    add_mps_and_political_parties(
        "https://www.sabor.hr/en/mps?field_saziv_target_id_all=all&field_prezime_value=&stranka_id_all=&field_izborna_jedinica_target_id_all=&field_izborna_lista_target_id_all=&field_spol_target_id=100&field_status_mandata_target_id=all&page=0%2C0",
        "male")
