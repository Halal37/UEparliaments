import os
import django
import requests
import json
import logging
import sys
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

logger = logging.getLogger(__name__)
os.environ['DJANGO_SETTINGS_MODULE'] = 'UEparliaments.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UEparliaments.settings")

django.setup()
from website.models import ParliamentaryTerm, Parliament, MandateOfMP, MP, PoliticalParty, Country

parliament = Parliament.objects.get(country="Belgium", name="Chamber of Representatives")


def add_parliamentary_terms():
    try:
        response = requests.get(
            "https://parlement.thundr.be/index.json")
        data = response.text
        parse_json = json.loads(data)
        for i in parse_json:
            term = i
            response = requests.get(
                parse_json[f'{term}'])
            data = response.text
            parse_json_term = json.loads(data)
            for element in parse_json_term:
                ParliamentaryTerm.objects.get_or_create(seats=150, term=term,
                                                        parliament=parliament,
                                                        beginning_of_term=parse_json_term["start"],
                                                        end_of_term=parse_json_term["end"])
    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_mps_and_political_parties():
    try:
        terms = ParliamentaryTerm.objects.filter(parliament=parliament)
        for term in terms:
            response = requests.get(
                f"https://parlement.thundr.be/sessions/{term.term}/session.json")
            data = response.text
            parse_json = json.loads(data)

            for member in parse_json["members"]:
                response = requests.get(
                    member)
                data = response.text
                parse_json_member = json.loads(data)
                replace = parse_json_member["replaces"]

                MP.objects.get_or_create(first_name=parse_json_member["first_name"],
                                         last_name=parse_json_member["last_name"], gender=parse_json_member["gender"],
                                         date_of_birth=parse_json_member["date_of_birth"].split("T")[0])

                PoliticalParty.objects.get_or_create(
                    country=Country.objects.get(country_name="Belgium"), name=parse_json_member["party"])

                if not replace:
                    MandateOfMP.objects.get_or_create(
                        party=PoliticalParty.objects.get(country="Belgium", name=parse_json_member["party"]),
                        parliamentary_term=term,
                        parliament=parliament, mp=MP.objects.get(first_name=parse_json_member["first_name"],
                                                                 last_name=parse_json_member["last_name"],
                                                                 gender=parse_json_member["gender"],
                                                                 date_of_birth=
                                                                 parse_json_member["date_of_birth"].split("T")[0]),
                        beginning_of_term=term.beginning_of_term,
                        end_of_term=term.end_of_term)

                else:
                    MandateOfMP.objects.get_or_create(
                        party=PoliticalParty.objects.get(country="Belgium", name=parse_json_member["party"]),
                        parliamentary_term=term,
                        parliament=parliament, mp=MP.objects.get(first_name=parse_json_member["first_name"],
                                                                 last_name=parse_json_member["last_name"],
                                                                 gender=parse_json_member["gender"],
                                                                 date_of_birth=
                                                                 parse_json_member["date_of_birth"].split("T")[0]),
                        beginning_of_term=replace[0]["dates"][0]['from'],
                        end_of_term=term.end_of_term)
                    response = requests.get(
                        replace[0]['member'])
                    data = response.text
                    parse_json_replaced = json.loads(data)
                    MP.objects.get_or_create(first_name=parse_json_replaced["first_name"],
                                             last_name=parse_json_replaced["last_name"],
                                             gender=parse_json_replaced["gender"],
                                             date_of_birth=parse_json_replaced["date_of_birth"].split("T")[0])

                    PoliticalParty.objects.get_or_create(
                        country=Country.objects.get(country_name="Belgium"), name=parse_json_replaced["party"])

                    mp, i = MandateOfMP.objects.get_or_create(
                        party=PoliticalParty.objects.get(country="Belgium", name=parse_json_replaced["party"]),
                        parliamentary_term=term,
                        parliament=parliament,
                        mp=MP.objects.get(first_name=parse_json_replaced["first_name"],
                                          last_name=parse_json_replaced["last_name"],
                                          gender=parse_json_replaced["gender"],
                                          date_of_birth=parse_json_replaced["date_of_birth"].split("T")[0]),
                        beginning_of_term=term.beginning_of_term, end_of_term=term.end_of_term)
                    mp.mp.end_of_term = replace[0]["dates"][0]['from']
                    mp.save()

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_parliamentary_terms()
    add_mps_and_political_parties()
