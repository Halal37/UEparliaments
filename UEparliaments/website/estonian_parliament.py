import os
import django
import requests
import xmltodict
import json
import logging
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

logger = logging.getLogger(__name__)
os.environ['DJANGO_SETTINGS_MODULE'] = 'UEparliaments.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UEparliaments.settings")

django.setup()
from website.models import ParliamentaryTerm, Parliament, MandateOfMP, MP, PoliticalParty, Country

parliament = Parliament.objects.get(country="Estonia", name="Riigikogu")


def add_mps_and_political_parties():
    try:
        response = requests.get("https://api.riigikogu.ee/api/plenary-members?includeInactive=true&lang=et")
        data = response.text
        parse_json = json.loads(data)
        print(parse_json)
        for i, element in enumerate(parse_json):
            print(element)
            print(i)
            print(element["firstName"])
            print(element["lastName"])
            if element["faction"] is not None:
                party = element["faction"]["name"]
            else:
                party = "Independent"
            print(element["plenaryMembership"]["startDate"])
            print(element["plenaryMembership"]["endDate"])
            uuid = element["uuid"]
            if element["active"] is True:
                end_of_term = None
                response = requests.get(f"https://api.riigikogu.ee/api/plenary-members/{uuid}?lang=EN&querySteno=true")
                data = response.text
                parse_json_mp = json.loads(data)
                note = parse_json_mp["introduction"]
            else:
                end_of_term = element["plenaryMembership"]["endDate"]
                note = ""

            MP.objects.get_or_create(first_name=element['firstName'],
                                     last_name=element['lastName'], biographical_notes=note)

            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Estonia"), name=party)

            term = ParliamentaryTerm.objects.get(
                parliament=parliament,
                term="14")
            MandateOfMP.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Estonia", name=party),
                parliamentary_term=term,
                parliament=parliament, mp=MP.objects.get(first_name=element['firstName'],
                                                         last_name=element['lastName'], biographical_notes=note),
                beginning_of_term=element["plenaryMembership"]["startDate"],
                end_of_term=end_of_term)



    except Exception as e:

        print("Could not save: ")

        print(e)

    print("Action complete!")


def add_terms():
    try:
        response = requests.get("https://api.riigikogu.ee/api/memberships")
        data = response.text
        parse_json = json.loads(data)
        for element in parse_json:
            ParliamentaryTerm.objects.get_or_create(seats=101, term=element['number'], parliament=parliament,
                                                    beginning_of_term=element['startDate'],
                                                    end_of_term=element['endDate'])
    except Exception as e:

        print("Could not save: ")

        print(e)

    print("Action complete!")


if __name__ == "__main__":
    add_terms()
    add_mps_and_political_parties()
