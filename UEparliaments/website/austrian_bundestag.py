import roman
import os
import django
import requests
import json
import logging
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

logger = logging.getLogger(__name__)
os.environ['DJANGO_SETTINGS_MODULE'] = 'UEparliaments.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UEparliaments.settings")

django.setup()
from website.models import SenateTerm, Senate, ParliamentaryTerm, Parliament, MandateOfMP, MP, PoliticalParty, Country

parliament = Parliament.objects.get(country="Austria", name="National Council")
austrian_terms = ParliamentaryTerm.objects.filter(parliament=parliament)
terms = []
for i in austrian_terms:
    terms.append(i.term)


def add_terms():
    try:
        senate = Senate.objects.get(country="Austria", name="Federal Council")
        austrian_terms = SenateTerm.objects.filter(senate=senate)
        terms = []
        for i in austrian_terms:
            terms.append(i.term)
            term = SenateTerm.objects.get(senate=senate, term=str(i.term))
            ParliamentaryTerm.objects.get_or_create(seats=183, term=str(i.term),
                                                    parliament=parliament,
                                                    beginning_of_term=term.beginning_of_term,
                                                    end_of_term=term.end_of_term)
    except Exception as e:

        print("Could not save: ")

        print(e)

    print("Action complete!")


def add_mps_and_political_parties():
    try:
        response = requests.get(
            "https://raw.githubusercontent.com/ginseng666/Abgeordnete-MPs-Austria-1920-2021/master/nr_complete.json")

        data = response.text
        parse_json = json.loads(data)

        for element in parse_json:

            for club in element['nr']:
                if club['end'] == "ongoing" or datetime.strptime(club['end'], '%d.%m.%Y').strftime('%Y-%m-%d') >= str(
                        ParliamentaryTerm.objects.get(parliament=parliament, term=terms[0]).beginning_of_term):
                    PoliticalParty.objects.get_or_create(
                        country=Country.objects.get(country_name="Austria"), name=club['club'])

                    for session in element['sessions']:
                        if str(roman.fromRoman(session)) in terms:
                            term = ParliamentaryTerm.objects.get(parliament=parliament,
                                                                 term=str(roman.fromRoman(session)))
                            if (datetime.strptime(element['nr'][0]['start'], '%d.%m.%Y').strftime('%Y-%m-%d') > str(
                                    term.beginning_of_term)):
                                beginning_of_term = datetime.strptime(element['nr'][0]['start'], '%d.%m.%Y').strftime(
                                    '%Y-%m-%d')
                            else:
                                beginning_of_term = term.beginning_of_term
                            if (element['nr'][0]['end'] == "ongoing"):
                                end_of_term = term.end_of_term
                            elif (datetime.strptime(element['nr'][0]['end'], '%d.%m.%Y').strftime('%Y-%m-%d') >= str(
                                    term.end_of_term)):
                                end_of_term = term.end_of_term
                            else:
                                end_of_term = datetime.strptime(element['nr'][0]['end'], '%d.%m.%Y').strftime(
                                    '%Y-%m-%d')
                            if element['birth'] == '':
                                birth = None
                            else:
                                birth = datetime.strptime(element['birth'],
                                                          '%d.%m.%Y').strftime(
                                    '%Y-%m-%d')
                            if element['sex'] is "m":
                                gender = "male"

                            elif element['sex'] is "w":
                                gender = "female"

                            MP.objects.get_or_create(first_name=element['given_name'],
                                                     last_name=element['surname'],
                                                     date_of_birth=birth,
                                                     gender=gender)

                            MandateOfMP.objects.get_or_create(
                                party=PoliticalParty.objects.get(country="Austria", name=club['club']),
                                parliamentary_term=term,
                                parliament=parliament,
                                mp=MP.objects.get(first_name=element['given_name'],
                                                  last_name=element['surname'],
                                                  date_of_birth=birth,
                                                  gender=gender),
                                beginning_of_term=beginning_of_term,
                                end_of_term=end_of_term)


    except Exception as e:

        print("Could not save: ")

        print(e)

    print("Action complete!")


if __name__ == "__main__":
    add_terms()
    add_mps_and_political_parties()
