import os
import django
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
from website.models import SenateTerm, Senate, MandateOfSenator, Senator, PoliticalParty, Country, Parliament, \
    ParliamentaryTerm

senate = Senate.objects.get(country="Spain", name="Senate")

def add_terms():
    try:
        parliament = Parliament.objects.get(country="Spain", name="Congress of Deputies")
        spain_terms = ParliamentaryTerm.objects.filter(parliament=parliament)
        terms = []
        for i in spain_terms:
            terms.append(i.term)
            term = ParliamentaryTerm.objects.get(parliament=parliament, term=str(i.term))
            SenateTerm.objects.get_or_create(seats=266, term=str(i.term),
                                             senate=senate,
                                             beginning_of_term=term.beginning_of_term,
                                             end_of_term=term.end_of_term)
    except Exception as e:

        print("Could not save: ")

        print(e)

    print("Action complete!")


if __name__ == "__main__":
    add_terms()
