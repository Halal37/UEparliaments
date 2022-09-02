import os
import django
import requests
import xmltodict
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

parliament = Parliament.objects.get(country="France", name="National Assembly")

sites = {"www.nosdeputes.fr", "2017-2022.nosdeputes.fr", "2012-2017.nosdeputes.fr", "2007-2012.nosdeputes.fr"}
terms = ["16", "15", "14", "13"]


def add_mps_and_political_parties():
    try:
        for j, i in enumerate(sites):

            response = requests.get(f"https://{i}/deputes/xml")

            decoded_response = response.content.decode('utf-8')
            response_json = json.loads(json.dumps(xmltodict.parse(decoded_response)))

            for element in response_json['deputes']['depute']:
                if element['sexe'] is "H":
                    gender = "male"
                elif element['sexe'] is "F":
                    gender = "female"

                party = element['groupe_sigle']

                MP.objects.get_or_create(first_name=element['prenom'],
                                         last_name=element['nom_de_famille'], date_of_birth=element['date_naissance'],
                                         gender=gender)
                if element['groupe_sigle'] is None:
                    party = "Independent"
                    PoliticalParty.objects.get_or_create(
                        country=Country.objects.get(country_name="France"), name="Independent")
                else:
                    PoliticalParty.objects.get_or_create(
                        country=Country.objects.get(country_name="France"), name=element['groupe_sigle'])

                if 'mandat_fin' in element:
                    end_of_term = element['mandat_fin']
                else:
                    end_of_term = None
                print(terms[j])
                term = ParliamentaryTerm.objects.get(
                    parliament=parliament,
                    term=terms[j])
                print("opa")
                MandateOfMP.objects.get_or_create(
                    party=PoliticalParty.objects.get(country="France", name=party),
                    parliamentary_term=term,
                    parliament=parliament, mp=MP.objects.get(first_name=element['prenom'],
                                                             last_name=element['nom_de_famille']),
                    beginning_of_term=element['mandat_debut'],
                    end_of_term=end_of_term)

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


# response_json = json.loads(json.dumps(xmltodict.parse(decoded)))
def add_terms():
    try:
        response = requests.get(f"https://www.nosdeputes.fr/deputes/xml")
        decoded_response = response.content.decode('utf-8')
        response_json = json.loads(json.dumps(xmltodict.parse(decoded_response)))
        for element in response_json['deputes']['depute']:
            if len(element['anciens_mandats']['mandat']) is 4:
                for j, i in enumerate(element['anciens_mandats']['mandat']):

                    start = i[:10]
                    end = i[13:23]

                    if j > 0:
                        ParliamentaryTerm.objects.get_or_create(seats=577, term=terms[j], parliament=parliament,
                                                                beginning_of_term=datetime.datetime.strptime(start,
                                                                                                             '%d/%m/%Y').strftime(
                                                                    '%Y-%m-%d'),
                                                                end_of_term=datetime.datetime.strptime(end,
                                                                                                       '%d/%m/%Y').strftime(
                                                                    '%Y-%m-%d'))
                    else:
                        ParliamentaryTerm.objects.get_or_create(seats=577, term=terms[j], parliament=parliament,
                                                                beginning_of_term=datetime.datetime.strptime(start,
                                                                                                             '%d/%m/%Y').strftime(
                                                                    '%Y-%m-%d'),
                                                                end_of_term=None)

                break


    except Exception as e:

        print("Could not save: ")

        print(e)


print("Action complete!")

if __name__ == "__main__":
    add_terms()
    add_mps_and_political_parties()
