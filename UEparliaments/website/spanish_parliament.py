import os
import django
import requests
import json
import logging
import sys
import roman
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

logger = logging.getLogger(__name__)
os.environ['DJANGO_SETTINGS_MODULE'] = 'UEparliaments.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UEparliaments.settings")

django.setup()
from website.models import ParliamentaryTerm, Parliament, MandateOfMP, MP, PoliticalParty, Country

parliament = Parliament.objects.get(country="Spain", name="Congress of Deputies")

information_base = [
    "https://www.congreso.es/webpublica/opendata/diputados/odsDiputados13__20220917063013.json",
    "https://www.congreso.es/webpublica/opendata/diputados/odsDiputados12__20220917063015.json",
    "https://www.congreso.es/webpublica/opendata/diputados/odsDiputados11__20220917063221.json",
    "https://www.congreso.es/webpublica/opendata/diputados/odsDiputados10__20220917063222.json",
    "https://www.congreso.es/webpublica/opendata/diputados/odsDiputados09__20220917063224.json",
    "https://www.congreso.es/webpublica/opendata/diputados/odsDiputados08__20220917063225.json",
    "https://www.congreso.es/webpublica/opendata/diputados/odsDiputados07__20220917063226.json",
    "https://www.congreso.es/webpublica/opendata/diputados/odsDiputados06__20220917063228.json",
    "https://www.congreso.es/webpublica/opendata/diputados/odsDiputados05__20220917063230.json",
    "https://www.congreso.es/webpublica/opendata/diputados/odsDiputados04__20220917063232.json",
    "https://www.congreso.es/webpublica/opendata/diputados/odsDiputados03__20220917063233.json",
]


def add_term_and_political_parties():
    try:
        current_term = 13
        for term in information_base:
            response = requests.get(
                term)
            data = response.text
            parse_json = json.loads(data)
            beginning_of_term = "3000-12-20"
            end_of_term = "1900-12-20"

            for element in parse_json:
                if datetime.strptime(element['FECHACONDICIONPLENA'], '%d/%m/%Y').strftime(
                        '%Y-%m-%d') <= beginning_of_term:
                    beginning_of_term = datetime.strptime(element['FECHACONDICIONPLENA'], '%d/%m/%Y').strftime(
                        '%Y-%m-%d')
                if datetime.strptime(element['FECHABAJA'], '%d/%m/%Y').strftime('%Y-%m-%d') > end_of_term:
                    end_of_term = datetime.strptime(element['FECHABAJA'], '%d/%m/%Y').strftime('%Y-%m-%d')
                if "FORMACIONELECTORAL" in element:
                    PoliticalParty.objects.get_or_create(
                        country=Country.objects.get(country_name="Spain"), name=element["FORMACIONELECTORAL"])
                else:

                    PoliticalParty.objects.get_or_create(
                        country=Country.objects.get(country_name="Spain"), name="Independent")

            ParliamentaryTerm.objects.get_or_create(seats=350, term=current_term,
                                                    parliament=parliament,
                                                    beginning_of_term=beginning_of_term,
                                                    end_of_term=end_of_term)
            current_term -= 1



    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_mps():
    try:
        response = requests.get(
            "https://www.congreso.es/webpublica/opendata/diputados/Diput__20220917063244.json")
        data = response.text
        parse_json = json.loads(data)
        for element in parse_json:
            MP.objects.get_or_create(first_name=element["NOMBRE"],
                                     last_name=element["APELLIDOS"], )

    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_current_term():
    try:
        response = requests.get(
            "https://www.congreso.es/webpublica/opendata/diputados/DiputadosDeBaja__20220917063010.json")
        data = response.text
        parse_json = json.loads(data)
        beginning_of_term = "3000-12-20"

        for element in parse_json:
            if datetime.strptime(element['FECHACONDICIONPLENA'], '%d/%m/%Y').strftime(
                    '%Y-%m-%d') <= beginning_of_term:
                beginning_of_term = datetime.strptime(element['FECHACONDICIONPLENA'], '%d/%m/%Y').strftime(
                    '%Y-%m-%d')
            if "FORMACIONELECTORAL" in element:
                PoliticalParty.objects.get_or_create(
                    country=Country.objects.get(country_name="Spain"), name=element["FORMACIONELECTORAL"])
            else:
                PoliticalParty.objects.get_or_create(
                    country=Country.objects.get(country_name="Spain"), name="Independent")

        ParliamentaryTerm.objects.get_or_create(seats=350, term=14,
                                                parliament=parliament,
                                                beginning_of_term=beginning_of_term,
                                                end_of_term=None)
    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_mandates():
    try:
        response = requests.get(
            "https://www.congreso.es/webpublica/opendata/diputados/Diput__20220917063244.json")
        data = response.text
        parse_json = json.loads(data)
        for element in parse_json:
            mp_name = element["APELLIDOS"] + ", " + element["NOMBRE"]
            if element['LEGISLATURA'].split("Leg. ")[1] != "Const." and roman.fromRoman(
                    element['LEGISLATURA'].split("Leg. ")[1]) >= 3:
                term = roman.fromRoman(element['LEGISLATURA'].split("Leg. ")[1])
                if term is 14:
                    response_mp = requests.get(
                        "https://www.congreso.es/webpublica/opendata/diputados/DiputadosDeBaja__20220917063010.json")
                    data_mp = response_mp.text
                    parse_json_mp = json.loads(data_mp)
                    for mps in parse_json_mp:
                        if mp_name == mps["NOMBRE"]:
                            if "FECHAFINLEGISLATURA" in element:
                                end_of_term = datetime.strptime(element["FECHAFINLEGISLATURA"], '%d/%m/%Y').strftime(
                                    '%Y-%m-%d')
                            else:
                                end_of_term = None
                            if "FORMACIONELECTORAL" in mps:
                                party = mps["FORMACIONELECTORAL"]
                            else:
                                party = "Independent"

                            MandateOfMP.objects.get_or_create(
                                party=PoliticalParty.objects.get(country="Spain", name=party),
                                parliamentary_term=ParliamentaryTerm.objects.get(
                                    parliament=parliament,
                                    term=14),
                                parliament=parliament, mp=MP.objects.get(first_name=element["NOMBRE"],
                                                                         last_name=element["APELLIDOS"]),
                                beginning_of_term=datetime.strptime(element["FECHAINICIOLEGISLATURA"],
                                                                    '%d/%m/%Y').strftime(
                                    '%Y-%m-%d'),
                                end_of_term=end_of_term)
                            break

                else:
                    response_mp = requests.get(
                        information_base[13 - term])
                    data_mp = response_mp.text
                    parse_json_mp = json.loads(data_mp)
                    for mps in parse_json_mp:
                        if mp_name == mps["NOMBRE"]:
                            if "FORMACIONELECTORAL" in mps:
                                party = mps["FORMACIONELECTORAL"]
                            else:
                                party = "Independent"

                            MandateOfMP.objects.get_or_create(
                                party=PoliticalParty.objects.get(country="Spain", name=party),
                                parliamentary_term=ParliamentaryTerm.objects.get(
                                    parliament=parliament,
                                    term=term),
                                parliament=parliament, mp=MP.objects.get(first_name=element["NOMBRE"],
                                                                         last_name=element["APELLIDOS"]),
                                beginning_of_term=datetime.strptime(element["FECHAINICIOLEGISLATURA"],
                                                                    '%d/%m/%Y').strftime(
                                    '%Y-%m-%d'),
                                end_of_term=datetime.strptime(
                                    element["FECHAFINLEGISLATURA"], '%d/%m/%Y').strftime(
                                    '%Y-%m-%d'))
                            break


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_current_mandates():
    try:
        response = requests.get(
            "https://www.congreso.es/webpublica/opendata/diputados/Diput__20220917063244.json")
        data = response.text
        parse_json = json.loads(data)
        for element in parse_json:
            if element["LEGISLATURAACTUAL"] == "S":
                if "FECHAFINLEGISLATURA" in element:
                    end_of_term = datetime.strptime(element["FECHAFINLEGISLATURA"], '%d/%m/%Y').strftime(
                        '%Y-%m-%d')
                else:
                    end_of_term = None
                party = MandateOfMP.objects.filter(parliamentary_term=ParliamentaryTerm.objects.get(
                    parliament=parliament,
                    term=13),
                    parliament=parliament,
                    mp=MP.objects.get(first_name=element["NOMBRE"],
                                      last_name=element["APELLIDOS"]), )
                if len(party) > 0:
                    party = party[0].party

                else:
                    party = "Independent"

                MandateOfMP.objects.get_or_create(
                    party=PoliticalParty.objects.get(country="Spain", name=party),
                    parliamentary_term=ParliamentaryTerm.objects.get(
                        parliament=parliament,
                        term=14),
                    parliament=parliament, mp=MP.objects.get(first_name=element["NOMBRE"],
                                                             last_name=element["APELLIDOS"]),
                    beginning_of_term=datetime.strptime(element["FECHAINICIOLEGISLATURA"],
                                                        '%d/%m/%Y').strftime(
                        '%Y-%m-%d'),
                    end_of_term=end_of_term)


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_term_and_political_parties()
    add_mps()
    add_current_term()
    add_mandates()
    add_current_mandates()
