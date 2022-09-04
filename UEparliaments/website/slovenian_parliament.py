import os
import django
import requests
import xmltodict
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
from website.models import ParliamentaryTerm, Parliament, MandateOfMP, MP, PoliticalParty, Country

parliament = Parliament.objects.get(country="Slovenia", name="National Assembly")

term = ParliamentaryTerm.objects.get_or_create(seats=90, term="9",
                                              parliament=parliament,
                                              beginning_of_term="2022-05-13",
                                              end_of_term=None)

response = requests.get("https://fotogalerija.dz-rs.si/datoteke/opendata/SIF.XML")

decoded_response = response.content.decode('utf-8')
response_json = json.loads(json.dumps(xmltodict.parse(decoded_response)))

def add_mps_and_political_parties_and_term():
    try:
        term = ParliamentaryTerm.objects.get(seats=90, term="9",
                                                       parliament=parliament,
                                                       beginning_of_term="2022-05-13",
                                                       end_of_term=None)
        codes = {}
        for element in response_json['SIF']['SUBJEKTI_FUNKCIJE']['SUBJEKT_FUNKCIJA']:
            if (element['SUBJEKT_FUNKCIJA_SIFRA'] >= "PS012" and element['SUBJEKT_FUNKCIJA_SIFRA'] <= "PS036"):
                if "AN" in element["SUBJEKT_FUNKCIJA_NAZIV"]:
                    name = element["SUBJEKT_FUNKCIJA_NAZIV"]["AN"]
                else:
                    name = "Parliamentary Group of the Italian and Hungarian National Communities"
                codes[element['SUBJEKT_FUNKCIJA_SIFRA']] = name.split(" Deputy Group")[0]

        party = {}
        for element in response_json['SIF']['POVEZAVE']['POVEZAVA']:
            if element['SUBJEKTI_FUNKCIJA_SIFRA'] in codes.keys():
                party[element['OSEBA_SIFRA']] = element['SUBJEKTI_FUNKCIJA_SIFRA']
        for element in response_json['SIF']['OSEBE']['OSEBA']:
            if element['OSEBA_SPOL'] is "Z":
                gender = "female"
            elif element['OSEBA_SPOL'] is "M":
                gender = "male"
            if element['OSEBA_OSEBNA_IZKAZNICA'] is not None:
                if "#text" in element['OSEBA_OSEBNA_IZKAZNICA']:
                    date_time_str = \
                        element['OSEBA_OSEBNA_IZKAZNICA']['#text'].split(" v ")[0].split(" na ")[0].split("Rojen ")[
                            -1].split(
                            "Rojena ")[-1].replace("avgusta", "08.").replace("julija", "07.").replace("februarja",
                                                                                                      "02.").replace(
                            "maja", "05.").replace("oktobra", "10.").replace("novembra", "11.").replace("marca",
                                                                                                        "03.").replace(
                            "januarja", "01.").replace("septembra", "09.").replace("aprila", "04.").replace("junija",
                                                                                                            "06.").replace(
                            "decembra", "12.").replace(" ", "").replace(".", "/")

                    if date_time_str[-1] is "/":
                        date_time_str = date_time_str[:-1]
                    date_time_obj = datetime.strptime(date_time_str, '%d/%m/%Y').strftime('%Y-%m-%d')
                else:
                    date_time_obj = None
            else:
                date_time_obj = None

            if element['OSEBA_DOSEDANJE_DELO'] is not None:
                if "AN" in element['OSEBA_DOSEDANJE_DELO']:
                    bio = element['OSEBA_DOSEDANJE_DELO']['AN']
                else:
                    bio = None
            else:
                bio = None

            MP.objects.get_or_create(first_name=element['OSEBA_IME'],
                                     last_name=element['OSEBA_PRIIMEK'], gender=gender,
                                     date_of_birth=date_time_obj, biographical_notes=bio)

            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Slovenia"), name=codes[party[element['OSEBA_SIFRA']]])

            MandateOfMP.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Slovenia", name=codes[party[element['OSEBA_SIFRA']]]),
                parliamentary_term=term,
                parliament=parliament, mp=MP.objects.get(first_name=element['OSEBA_IME'],
                                                         last_name=element['OSEBA_PRIIMEK'], gender=gender,
                                                         date_of_birth=date_time_obj, biographical_notes=bio),
                beginning_of_term=term.beginning_of_term,
                end_of_term=term.end_of_term)

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_mps_and_political_parties_and_term()
