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
from website.models import SenateTerm, Senate, MandateOfSenator, Senator, PoliticalParty, Country

senate = Senate.objects.get(country="Ireland", name="Seanad Éireann")


def add_political_parties():
    try:
        for i in range(26, 3, -1):
            response = requests.get(
                f"https://api.oireachtas.ie/v1/parties?chamber_id=&chamber=seanad&house_no={i}&limit=50")
            data = response.text
            parse_json = json.loads(data)
            for element in parse_json['results']["house"]["parties"]:
                PoliticalParty.objects.get_or_create(
                    country=Country.objects.get(country_name="Ireland"), name=element["party"]['showAs'])
    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_political_parties_before_1934():
    years = {1934, 1931, 1928, 1925, 1922}
    try:
        for i in years:
            response = requests.get(
                f"https://api.oireachtas.ie/v1/parties?chamber_id=&chamber=seanad&house_no={i}&limit=50")
            data = response.text
            parse_json = json.loads(data)
            for element in parse_json['results']["house"]["parties"]:
                PoliticalParty.objects.get_or_create(
                    country=Country.objects.get(country_name="Ireland"), name=element["party"]['showAs'])
    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_senators():
    try:
        for i in range(26, 3, -1):
            response = requests.get(
                f"https://api.oireachtas.ie/v1/members?date_start=1900-01-01&chamber_id=&chamber=seanad&house_no={i}&date_end=2099-01-01&limit=250")
            data = response.text
            parse_json = json.loads(data)

            for element in parse_json['results']:
                Senator.objects.get_or_create(first_name=element['member']['firstName'],
                                              last_name=element['member']['lastName'],
                                              gender=element['member']['gender'])

                MandateOfSenator.objects.get_or_create(
                    party=PoliticalParty.objects.get(country="Ireland", name=
                    element['member']['memberships'][0]['membership']['parties'][-1]['party']['showAs']),
                    senate_term=SenateTerm.objects.get(senate=senate, term=f"{i}"),
                    senate=senate, senator=Senator.objects.get(first_name=element['member']['firstName'],
                                                               last_name=element['member']['lastName']),
                    beginning_of_term=element["member"]['memberships'][0]['membership']['dateRange']['start'],
                    end_of_term=element["member"]['memberships'][0]['membership']['dateRange']['end'])

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_senate_terms():
    try:
        response = requests.get(
            f"https://api.oireachtas.ie/v1/houses?chamber_id=&chamber=seanad&limit=50")
        data = response.text
        parse_json = json.loads(data)
        for element in parse_json['results']:
            term = element["house"]['showAs'].replace("rd Seanad", "").replace("th Seanad", "").replace("st Seanad",
                                                                                                        "").replace(
                "nd Seanad", "").replace("Seanad", "")

            SenateTerm.objects.get_or_create(seats=element["house"]['seats'], term=term,
                                             senate=senate,
                                             beginning_of_term=element["house"]['dateRange']['start'],
                                             end_of_term=element["house"]['dateRange']['end'])
    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_senators_before_1934():
    years = {1934, 1931, 1928, 1925, 1922}
    try:
        for i in years:
            response = requests.get(
                f"https://api.oireachtas.ie/v1/members?date_start=1900-01-01&chamber_id=&chamber=seanad&house_no={i}&date_end=2099-01-01&limit=250")
            data = response.text
            parse_json = json.loads(data)

            for element in parse_json['results']:
                Senator.objects.get_or_create(first_name=element['member']['firstName'],
                                              last_name=element['member']['lastName'],
                                              gender=element['member']['gender'])

                MandateOfSenator.objects.get_or_create(
                    party=PoliticalParty.objects.get(country="Ireland", name=
                    element['member']['memberships'][0]['membership']['parties'][-1]['party']['showAs']),
                    senate_term=SenateTerm.objects.get(senate=senate, term=f"{i} "),
                    senate=senate, senator=Senator.objects.get(first_name=element['member']['firstName'],
                                                               last_name=element['member']['lastName']),
                    beginning_of_term=element["member"]['memberships'][0]['membership']['dateRange']['start'],
                    end_of_term=element["member"]['memberships'][0]['membership']['dateRange']['end'])

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_political_parties()
    add_political_parties_before_1934()
    add_senate_terms()
    add_senators()
    add_senators_before_1934()
