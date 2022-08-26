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

parliament = Parliament.objects.get(country="Poland", name="Sejm")


def add_mps_and_political_parties():
    try:
        for i in range(9, 2, -1):

            response = requests.get(f"http://api.sejm.gov.pl/sejm/term{i}/MP")
            data = response.text
            parse_json = json.loads(data)
            for element in parse_json:
                if "club" in element:
                    new_entry_mp = MP.objects.get_or_create(first_name=element['firstName'],
                                                            last_name=element['lastName'])

                    new_entry_party, created = PoliticalParty.objects.get_or_create(
                        country=Country.objects.get(country_name="Poland"), name=element['club'])
                    if "inactiveCause" not in element:
                        new_entry_mandate = MandateOfMP.objects.get_or_create(
                            party=PoliticalParty.objects.get(country="Poland", name=element['club']),
                            parliamentary_term=ParliamentaryTerm.objects.get(
                                parliament=Parliament.objects.get(country="Poland", name="Sejm"),
                                term=f"{i}"),
                            parliament=parliament, mp=MP.objects.get(first_name=element['firstName'],
                                                                     last_name=element['lastName']),
                            beginning_of_term=ParliamentaryTerm.objects.get(
                                parliament=Parliament.objects.get(country="Poland", name="Sejm"),
                                term=f"{i}").beginning_of_term,
                            end_of_term=ParliamentaryTerm.objects.get(
                                parliament=Parliament.objects.get(country="Poland", name="Sejm"),
                                term=f"{i}").end_of_term)
                    else:
                        new_entry_mandate = MandateOfMP.objects.get_or_create(
                            party=PoliticalParty.objects.get(country="Poland", name=element['club']),
                            parliamentary_term=ParliamentaryTerm.objects.get(
                                parliament=Parliament.objects.get(country="Poland", name="Sejm"),
                                term=f"{i}"),
                            parliament=parliament, mp=MP.objects.get(first_name=element['firstName'],
                                                                     last_name=element['lastName']),
                            beginning_of_term=ParliamentaryTerm.objects.get(
                                parliament=Parliament.objects.get(country="Poland", name="Sejm"),
                                term=f"{i}").beginning_of_term,
                            end_of_term=ParliamentaryTerm.objects.get(
                                parliament=Parliament.objects.get(country="Poland", name="Sejm"),
                                term=f"{i}").beginning_of_term)

    except Exception as e:
        print("Could not save: ")
        print(e)

    print("Action complete!")


def add_gender():
    for data in MP.objects.all():
        try:
            if data.first_name[-1] is "a":
                data.gender = "female"
            else:
                data.gender = "male"
            data.save()
        except Exception as e:
            print(e)
    print("Action complete!")


def add_terms():
    try:
        for element in parse_json:
            new_entry = ParliamentaryTerm(seats=460, term=element['num'], parliament=parliament,
                                          beginning_of_term=element['from'],
                                          end_of_term=element['to'])
            new_entry.save()

    except KeyError:
        print("Could not save:")
        new_entry = ParliamentaryTerm(seats=460, term=element['num'], parliament=parliament,
                                      beginning_of_term=element['from'],
                                      end_of_term=None)
        new_entry.save()
    print("Action complete!")
