import os
import django
import requests
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

parliament = Parliament.objects.get(country="Ireland", name="Dáil Éireann")


def add_political_parties():
    try:
        for i in range(33, 0, -1):
            response = requests.get(
                f"https://api.oireachtas.ie/v1/parties?chamber_id=&chamber=dail&house_no={i}&limit=50")
            data = response.text
            parse_json = json.loads(data)
            for element in parse_json['results']["house"]["parties"]:
                PoliticalParty.objects.get_or_create(
                    country=Country.objects.get(country_name="Ireland"), name=element["party"]['showAs'])
    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_mps():
    try:
        for i in range(33, 0, -1):
            response = requests.get(
                f"https://api.oireachtas.ie/v1/members?date_start=1900-01-01&chamber_id=&chamber=dail&house_no={i}&date_end=2099-01-01&limit=250")
            data = response.text
            parse_json = json.loads(data)

            for element in parse_json['results']:
                MP.objects.get_or_create(first_name=element['member']['firstName'],
                                         last_name=element['member']['lastName'], gender=element['member']['gender'])

                MandateOfMP.objects.get_or_create(
                    party=PoliticalParty.objects.get(country="Ireland", name=
                    element['member']['memberships'][0]['membership']['parties'][-1]['party']['showAs']),
                    parliamentary_term=ParliamentaryTerm.objects.get(parliament=parliament, term=f"{i}"),
                    parliament=parliament, mp=MP.objects.get(first_name=element['member']['firstName'],
                                                             last_name=element['member']['lastName']),
                    beginning_of_term=element["member"]['memberships'][0]['membership']['dateRange']['start'],
                    end_of_term=element["member"]['memberships'][0]['membership']['dateRange']['end'])

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_parliamentary_terms():
    try:
        response = requests.get(
            f"https://api.oireachtas.ie/v1/houses?chamber_id=&chamber=dail&limit=50")
        data = response.text
        parse_json = json.loads(data)
        for element in parse_json['results']:
            term = element["house"]['showAs'].replace("rd Dáil", "").replace("th Dáil", "").replace("st Dáil",
                                                                                                    "").replace(
                "nd Dáil", "")

            ParliamentaryTerm.objects.get_or_create(seats=element["house"]['seats'], term=term,
                                                    parliament=parliament,
                                                    beginning_of_term=element["house"]['dateRange']['start'],
                                                    end_of_term=element["house"]['dateRange']['end'])
    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_political_parties()
    add_parliamentary_terms()
    add_mps()
