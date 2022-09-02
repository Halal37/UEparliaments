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
from website.models import SenateTerm, Senate, MandateOfSenator, Senator, PoliticalParty, Country

senate = Senate.objects.get(country="France", name="Senate")
terms = ["16", "17", "18", "19", "20", "21"]
years = ["2004", "2008", "2011", "2014", "2017", "2020"]
dates_start = ["2004-09-26", "2008-09-21", "2011-09-25", "2014-09-28", "2017-09-24", "2020-09-27", "2023-09-26"]
dates_end = ["2004-09-30", "2008-09-30", "2011-09-30", "2014-09-30", "2017-10-01", "2020-09-30", "2023-09-30"]
seats = [326, 331, 343, 348, 348, 348]


def add_senators_and_political_parties():
    try:

        response = requests.get("https://www.nossenateurs.fr/senateurs/xml")
        decoded_response = response.content.decode('utf-8')
        response_json = json.loads(json.dumps(xmltodict.parse(decoded_response)))

        for element in response_json['senateurs']['senateur']:
            if element['sexe'] is "H":
                gender = "male"
            elif element['sexe'] is "F":
                gender = "female"
            party = element['groupe_sigle']

            Senator.objects.get_or_create(first_name=element['prenom'],
                                          last_name=element['nom_de_famille'],
                                          date_of_birth=element['date_naissance'],
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
                end_of_term = None  # end of term
            for i, dates in enumerate(dates_start[:-1]):
                if end_of_term is not None:

                    if (element['mandat_debut'] >= dates) and (
                            element['mandat_debut'] <
                            dates_start[i + 1]) and (
                            element['mandat_fin'] <
                            dates_end[
                                i + 1]):

                        term = SenateTerm.objects.get(
                            senate=senate,
                            term=terms[i])

                        MandateOfSenator.objects.get_or_create(
                            party=PoliticalParty.objects.get(country="France", name=party),
                            senate_term=term,
                            senate=senate, senator=Senator.objects.get(first_name=element['prenom'],
                                                                       last_name=element['nom_de_famille']),
                            beginning_of_term=element['mandat_debut'],
                            end_of_term=element['mandat_fin'])

                    elif (element['mandat_debut'] >= dates) and (
                            element['mandat_debut'] <
                            dates_start[i + 1]) and (
                            element['mandat_fin'] >=
                            dates_end[
                                i + 1]):

                        term = SenateTerm.objects.get(
                            senate=senate,
                            term=terms[i])

                        MandateOfSenator.objects.get_or_create(
                            party=PoliticalParty.objects.get(country="France", name=party),
                            senate_term=term,
                            senate=senate, senator=Senator.objects.get(first_name=element['prenom'],
                                                                       last_name=element['nom_de_famille']),
                            beginning_of_term=element['mandat_debut'],
                            end_of_term=dates_end[i + 1])

                    elif (element['mandat_debut'] <
                          dates_start[i]) and (
                            element['mandat_fin'] >=
                            dates_end[
                                i + 1]):
                        term = SenateTerm.objects.get(
                            senate=senate,
                            term=terms[i])
                        MandateOfSenator.objects.get_or_create(
                            party=PoliticalParty.objects.get(country="France", name=party),
                            senate_term=term,
                            senate=senate, senator=Senator.objects.get(first_name=element['prenom'],
                                                                       last_name=element['nom_de_famille']),
                            beginning_of_term=dates_start[i],
                            end_of_term=dates_end[i + 1])

                    elif (element['mandat_debut'] <
                          dates_start[i]) and (
                            element['mandat_fin'] <
                            dates_end[
                                i + 1]) and (
                            element['mandat_fin'] >
                            dates_end[
                                i]):
                        term = SenateTerm.objects.get(
                            senate=senate,
                            term=terms[i])
                        MandateOfSenator.objects.get_or_create(
                            party=PoliticalParty.objects.get(country="France", name=party),
                            senate_term=term,
                            senate=senate, senator=Senator.objects.get(first_name=element['prenom'],
                                                                       last_name=element['nom_de_famille']),
                            beginning_of_term=dates_start[i],
                            end_of_term=element['mandat_fin'])
                else:
                    if ((element['mandat_debut'] >= "2020-09-27") or (element['mandat_debut'] >= dates) and (
                            element['mandat_debut'] <
                            dates_start[i + 1])):

                        term = SenateTerm.objects.get(
                            senate=senate,
                            term=terms[i])
                        MandateOfSenator.objects.get_or_create(
                            party=PoliticalParty.objects.get(country="France", name=party),
                            senate_term=term,
                            senate=senate, senator=Senator.objects.get(first_name=element['prenom'],
                                                                       last_name=element['nom_de_famille']),
                            beginning_of_term=element['mandat_debut'],
                            end_of_term=dates_end[i + 1])

                    elif (element['mandat_debut'] <
                          dates_start[i]):
                        term = SenateTerm.objects.get(
                            senate=senate,
                            term=terms[i])
                        MandateOfSenator.objects.get_or_create(
                            party=PoliticalParty.objects.get(country="France", name=party),
                            senate_term=term,
                            senate=senate, senator=Senator.objects.get(first_name=element['prenom'],
                                                                       last_name=element['nom_de_famille']),
                            beginning_of_term=dates_start[i],
                            end_of_term=dates_end[i + 1])



    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_terms():
    try:

        for j, i in enumerate(years):
            if int(i) < 2020:
                SenateTerm.objects.get_or_create(seats=seats[j], term=terms[j], senate=senate,
                                                 beginning_of_term=dates_start[j],
                                                 end_of_term=dates_end[j + 1])
            else:
                SenateTerm.objects.get_or_create(seats=seats[j], term=terms[j], senate=senate,
                                                 beginning_of_term=dates_start[j],
                                                 end_of_term=None)



    except Exception as e:

        print("Could not save: ")

        print(e)

    print("Action complete!")


if __name__ == "__main__":
    add_terms()
    add_senators_and_political_parties()
