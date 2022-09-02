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

parliament = Parliament.objects.get(country="Lithuania", name="Seimas")


def add_mps_and_political_parties():
    try:
        for i in range(9, 0, -1):
            response = requests.get(f"https://apps.lrs.lt/sip/p2b.ad_seimo_nariai?kadencijos_id={i}")

            decoded_response = response.content.decode('utf-8')
            response_json = json.loads(json.dumps(xmltodict.parse(decoded_response)))
            for element in response_json['SeimoInformacija']['SeimoKadencija']['SeimoNarys']:
                if element['@lytis'] is "V":
                    gender = "male"
                elif element['@lytis'] is "M":
                    gender = "female"

                MP.objects.get_or_create(first_name=element['@vardas'],
                                         last_name=element['@pavardė'], gender=gender)

                PoliticalParty.objects.get_or_create(
                        country=Country.objects.get(country_name="Lithuania"), name=element['@iškėlusi_partija'])

                if element['@data_iki'] is "":
                    end_of_term = None
                else:
                    end_of_term = element['@data_iki']
                term = ParliamentaryTerm.objects.get(
                    parliament=parliament,
                    term=i)
                MandateOfMP.objects.get_or_create(
                    party=PoliticalParty.objects.get(country="Lithuania", name=element['@iškėlusi_partija']),
                    parliamentary_term=term,
                    parliament=parliament, mp=MP.objects.get(first_name=element['@vardas'],
                                         last_name=element['@pavardė'], gender=gender),
                    beginning_of_term=element['@data_nuo'],
                    end_of_term=end_of_term)
    except Exception as e:

        print("Could not save: ")

        print(e)

    print("Action complete!")


def add_terms():
    try:
        response = requests.get("https://apps.lrs.lt/sip/p2b.ad_seimo_kadencijos")
        decoded_response = response.content.decode('utf-8')
        response_json = json.loads(json.dumps(xmltodict.parse(decoded_response)))
        for element in response_json['SeimoInformacija']['SeimoKadencija']:
            if element['@data_iki'] is "":
                end_of_term = None
            else:
                end_of_term = element['@data_iki']
            ParliamentaryTerm.objects.get_or_create(seats=141, term=element['@kadencijos_id'], parliament=parliament,
                                                    beginning_of_term=element['@data_nuo'],
                                                    end_of_term=end_of_term)
    except Exception as e:

        print("Could not save: ")

        print(e)

    print("Action complete!")


if __name__ == "__main__":
    add_terms()
    add_mps_and_political_parties()
