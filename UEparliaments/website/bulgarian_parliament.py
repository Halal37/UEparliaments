import os
import django
import requests
import logging
import sys
import json

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

parliament = Parliament.objects.get(country="Bulgaria", name="National Assembly")


def add_current_term_mps():
    try:
        response = requests.get("https://www.parliament.bg/api/v1/coll-list-ns/en")
        data = response.text
        parse_json = json.loads(data)
        for element in parse_json["colListMP"]:
            beginning_of_term = element["A_ns_MSP_date_F"]
            political_party = element["A_ns_CL_value"]
            if "Parliamentary Group of political party " in political_party:
                political_party = political_party.split("Parliamentary Group of political party ")[1]
            elif "Parliamentary Group of " in political_party:
                political_party = political_party.split("Parliamentary Group of ")[1]
            else:
                political_party = political_party.split("Parliamentary Group ")[1]
            political_party = political_party.replace("\" ", "")
            political_party = political_party.replace("\"", "")
            first_name = element["A_ns_MPL_Name1"].title()
            temporary_first_name=first_name.split()
            first_name = "".join(temporary_first_name)
            last_name = element["A_ns_MPL_Name3"].title()
            if first_name == "Nebie" or first_name == "Mukaddes" or first_name == "Imren" or first_name == "Erten" or first_name == "Alizan" or first_name == "Adlen":
                gender = "female"
            elif first_name == "Nikola" or first_name == "Mustafa" or first_name == "Toma":
                gender = "male"
            elif first_name[-1] == "a":
                gender = "female"
            else:
                gender = "male"
            if beginning_of_term == "2022-10-21":
                beginning_of_term = "2022-10-19"

            MP.objects.get_or_create(first_name=first_name,
                                     last_name=last_name, gender=gender)

            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Bulgaria"), name=political_party)

            term = ParliamentaryTerm.objects.get(
                parliament=parliament,
                term="48")
            MandateOfMP.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Bulgaria", name=political_party),
                parliamentary_term=term,
                parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                         last_name=last_name, gender=gender),
                beginning_of_term=beginning_of_term,
                end_of_term=None)





    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_current_term_mps()
