import os
import django
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

parliament = Parliament.objects.get(country="Germany", name="Bundestag")

term_seats = [420, 519, 519, 521, 518, 518, 518, 518, 519, 520, 663, 662, 672, 665, 601, 611, 620, 630, 709, 736]


def add_terms():
    try:
        with open("MDB_STAMMDATEN.xml", encoding="utf8") as xml_file:
            data_dict = xmltodict.parse(xml_file.read())
            temporary_json = json.dumps(data_dict)
        file_json = json.loads(temporary_json)
        beginnings_of_term = ["3900-10-15", "3900-10-15", "3900-10-15", "3900-10-15", "3900-10-15", "3900-10-15",
                              "3900-10-15", "3900-10-15", "3900-10-15", "3900-10-15", "3900-10-15", "3900-10-15",
                              "3900-10-15", "3900-10-15", "3900-10-15", "3900-10-15", "3900-10-15", "3900-10-15",
                              "3900-10-15", "3900-10-15", "3900-10-15", "3900-10-15"]
        ends_of_term = ["1900-10-15", "1900-10-15", "1900-10-15", "1900-10-15", "1900-10-15", "1900-10-15",
                        "1900-10-15",
                        "1900-10-15", "1900-10-15", "1900-10-15", "1900-10-15", "1900-10-15", "1900-10-15",
                        "1900-10-15",
                        "1900-10-15", "1900-10-15", "1900-10-15", "1900-10-15", "1900-10-15", "1900-10-15"]
        terms = {1}
        for element in file_json['DOCUMENT']['MDB']:
            if type(element['WAHLPERIODEN']['WAHLPERIODE']) is dict:
                beginning_of_term = datetime.strptime(element['WAHLPERIODEN']['WAHLPERIODE']['MDBWP_VON'],
                                                      '%d.%m.%Y').strftime('%Y-%m-%d')
                if element['WAHLPERIODEN']['WAHLPERIODE']['MDBWP_BIS'] is not None:
                    end_of_term = datetime.strptime(element['WAHLPERIODEN']['WAHLPERIODE']['MDBWP_BIS'],
                                                    '%d.%m.%Y').strftime('%Y-%m-%d')
                else:
                    end_of_term = None
                terms.add(int(element['WAHLPERIODEN']['WAHLPERIODE']['WP']))

                if end_of_term is None:
                    ends_of_term[int(element['WAHLPERIODEN']['WAHLPERIODE']['WP']) - 1] = None
                elif end_of_term > ends_of_term[
                    int(element['WAHLPERIODEN']['WAHLPERIODE']['WP']) - 1]:
                    ends_of_term[int(element['WAHLPERIODEN']['WAHLPERIODE']['WP']) - 1] = end_of_term

                if beginning_of_term < beginnings_of_term[int(element['WAHLPERIODEN']['WAHLPERIODE']['WP']) - 1]:
                    beginnings_of_term[int(element['WAHLPERIODEN']['WAHLPERIODE']['WP']) - 1] = beginning_of_term

        terms = sorted(terms)
        for term in terms:
            ParliamentaryTerm.objects.get_or_create(seats=term_seats[term - 1], term=term,
                                                    parliament=parliament,
                                                    beginning_of_term=beginnings_of_term[term - 1],
                                                    end_of_term=ends_of_term[term - 1])
    except Exception as e:

        print("Could not save: ")

        print(e)

    print("Action complete!")


def add_political_parties_and_mps():
    try:
        with open("MDB_STAMMDATEN.xml", encoding="utf8") as xml_file:
            data_dict = xmltodict.parse(xml_file.read())
            temporary_json = json.dumps(data_dict)
        file_json = json.loads(temporary_json)

        for element in file_json['DOCUMENT']['MDB']:

            if element['BIOGRAFISCHE_ANGABEN']['GESCHLECHT'] == "weiblich":
                gender = "female"
            elif element['BIOGRAFISCHE_ANGABEN']['GESCHLECHT'] == "männlich":
                gender = "male"
            if type(element['NAMEN']['NAME']) is dict:

                fullname = element['NAMEN']['NAME']

            else:

                fullname = element['NAMEN']['NAME'][-1]

            MP.objects.get_or_create(first_name=fullname['VORNAME'],
                                     last_name=fullname['NACHNAME'],
                                     date_of_birth=datetime.strptime(element['BIOGRAFISCHE_ANGABEN']['GEBURTSDATUM'],
                                                                     '%d.%m.%Y').strftime('%Y-%m-%d'),
                                     gender=gender)

            if type(element['WAHLPERIODEN']['WAHLPERIODE']) is dict:

                if type(element['WAHLPERIODEN']['WAHLPERIODE']['INSTITUTIONEN']['INSTITUTION']) is dict:
                    party = element['WAHLPERIODEN']['WAHLPERIODE']['INSTITUTIONEN']['INSTITUTION']['INS_LANG'].replace(
                        "Fraktion der ", "").replace("Fraktion ", "")
                    PoliticalParty.objects.get_or_create(
                        country=Country.objects.get(country_name="Germany"),
                        name=element['WAHLPERIODEN']['WAHLPERIODE']['INSTITUTIONEN']['INSTITUTION']['INS_LANG'].replace(
                            "Fraktion der ", "").replace("Fraktion ", ""))

                    beginning_of_term = datetime.strptime(element['WAHLPERIODEN']['WAHLPERIODE']['MDBWP_VON'],
                                                          '%d.%m.%Y').strftime('%Y-%m-%d').replace("('", "").replace(
                        "',)", "")
                    if element['WAHLPERIODEN']['WAHLPERIODE']['MDBWP_BIS'] is not None:
                        end_of_term = datetime.strptime(element['WAHLPERIODEN']['WAHLPERIODE']['MDBWP_BIS'],
                                                        '%d.%m.%Y').strftime('%Y-%m-%d').replace("('", "").replace(
                            "',)",
                            ""),
                    else:
                        end_of_term = None
                    if type(end_of_term) is not str and end_of_term is not None:
                        end_of_term = end_of_term[0]
                    MandateOfMP.objects.get_or_create(
                        party=PoliticalParty.objects.get(country="Germany", name=party),
                        parliamentary_term=ParliamentaryTerm.objects.get(
                            parliament=parliament,
                            term=element['WAHLPERIODEN']['WAHLPERIODE']['WP']),
                        parliament=parliament, mp=MP.objects.get(first_name=fullname['VORNAME'],
                                                                 last_name=fullname['NACHNAME'],
                                                                 date_of_birth=datetime.strptime(
                                                                     element['BIOGRAFISCHE_ANGABEN']['GEBURTSDATUM'],
                                                                     '%d.%m.%Y').strftime('%Y-%m-%d'),
                                                                 gender=gender),
                        beginning_of_term=beginning_of_term,
                        end_of_term=end_of_term)

                else:
                    for fraction in element['WAHLPERIODEN']['WAHLPERIODE']['INSTITUTIONEN']['INSTITUTION']:

                        if fraction['INSART_LANG'] == "Fraktion/Gruppe":

                            if fraction['MDBINS_VON'] is not None:
                                beginning_of_term = datetime.strptime(
                                    fraction['MDBINS_VON'],
                                    '%d.%m.%Y').strftime('%Y-%m-%d').replace("('", "").replace("',)", "")
                            if fraction['MDBINS_BIS'] is not None:
                                end_of_term = datetime.strptime(fraction['MDBINS_BIS'],
                                                                '%d.%m.%Y').strftime('%Y-%m-%d').replace("('",
                                                                                                         "").replace(
                                    "',)", ""),

                            party = fraction['INS_LANG'].replace("Fraktion der ", "").replace("Fraktion ", "")
                            PoliticalParty.objects.get_or_create(
                                country=Country.objects.get(country_name="Germany"),
                                name=fraction['INS_LANG'].replace("Fraktion der ", "").replace("Fraktion ", ""))
                            if type(end_of_term) is not str and end_of_term is not None:
                                end_of_term = end_of_term[0]
                            MandateOfMP.objects.get_or_create(
                                party=PoliticalParty.objects.get(country="Germany", name=party),
                                parliamentary_term=ParliamentaryTerm.objects.get(
                                    parliament=parliament,
                                    term=element['WAHLPERIODEN']['WAHLPERIODE']['WP']),
                                parliament=parliament, mp=MP.objects.get(first_name=fullname['VORNAME'],
                                                                         last_name=fullname['NACHNAME'],
                                                                         date_of_birth=datetime.strptime(
                                                                             element['BIOGRAFISCHE_ANGABEN'][
                                                                                 'GEBURTSDATUM'],
                                                                             '%d.%m.%Y').strftime('%Y-%m-%d'),
                                                                         gender=gender),
                                beginning_of_term=beginning_of_term,
                                end_of_term=end_of_term)
            else:

                for institution in element['WAHLPERIODEN']['WAHLPERIODE']:

                    beginning_of_term = datetime.strptime(institution['MDBWP_VON'],
                                                          '%d.%m.%Y').strftime('%Y-%m-%d').replace("('", "")
                    if institution['MDBWP_BIS'] is not None:
                        end_of_term = datetime.strptime(institution['MDBWP_BIS'], '%d.%m.%Y').strftime('%Y-%m-%d')
                    else:
                        end_of_term = None

                    if type(end_of_term) is not str and end_of_term is not None:
                        end_of_term = end_of_term[0]
                    if type(institution['INSTITUTIONEN']['INSTITUTION']) is dict:

                        PoliticalParty.objects.get_or_create(
                            country=Country.objects.get(country_name="Germany"),
                            name=institution['INSTITUTIONEN']['INSTITUTION']['INS_LANG'].replace("Fraktion der ",
                                                                                                 "").replace(
                                "Fraktion ", ""))
                        party = institution['INSTITUTIONEN']['INSTITUTION']['INS_LANG'].replace("Fraktion der ",
                                                                                                "").replace(
                            "Fraktion ", "")

                        MandateOfMP.objects.get_or_create(
                            party=PoliticalParty.objects.get(country="Germany", name=party),
                            parliamentary_term=ParliamentaryTerm.objects.get(
                                parliament=parliament,
                                term=institution['WP']),
                            parliament=parliament, mp=MP.objects.get(first_name=fullname['VORNAME'],
                                                                     last_name=fullname['NACHNAME'],
                                                                     date_of_birth=datetime.strptime(
                                                                         element['BIOGRAFISCHE_ANGABEN'][
                                                                             'GEBURTSDATUM'],
                                                                         '%d.%m.%Y').strftime('%Y-%m-%d'),
                                                                     gender=gender),
                            beginning_of_term=beginning_of_term,
                            end_of_term=end_of_term)
                    else:
                        for fraction in institution['INSTITUTIONEN']['INSTITUTION']:

                            if fraction['INSART_LANG'] == "Fraktion/Gruppe":
                                if fraction['MDBINS_VON'] is not None:
                                    beginning_of_term = datetime.strptime(
                                        fraction['MDBINS_VON'],
                                        '%d.%m.%Y').strftime('%Y-%m-%d').replace("('", "").replace("',)", "")
                                if fraction['MDBINS_BIS'] is not None:
                                    end_of_term = datetime.strptime(fraction['MDBINS_BIS'],
                                                                    '%d.%m.%Y').strftime('%Y-%m-%d').replace("'",
                                                                                                             "").replace(
                                        "'", ""),
                                PoliticalParty.objects.get_or_create(
                                    country=Country.objects.get(country_name="Germany"),
                                    name=fraction['INS_LANG'].replace("Fraktion der ", "").replace("Fraktion ", ""))
                                party = fraction['INS_LANG'].replace("Fraktion der ", "").replace("Fraktion ", "")
                                if type(end_of_term) is not str and end_of_term is not None:
                                    end_of_term = end_of_term[0]
                                MandateOfMP.objects.get_or_create(
                                    party=PoliticalParty.objects.get(country="Germany", name=party),
                                    parliamentary_term=ParliamentaryTerm.objects.get(
                                        parliament=parliament,
                                        term=institution['WP']),
                                    parliament=parliament, mp=MP.objects.get(first_name=fullname['VORNAME'],
                                                                             last_name=fullname['NACHNAME'],
                                                                             date_of_birth=
                                                                             datetime.strptime(
                                                                                 element['BIOGRAFISCHE_ANGABEN'][
                                                                                     'GEBURTSDATUM'],
                                                                                 '%d.%m.%Y').strftime('%Y-%m-%d'),
                                                                             gender=gender),
                                    beginning_of_term=beginning_of_term,
                                    end_of_term=end_of_term)

    except Exception as e:

        print("Could not save: ")

        print(e)

    print("Action complete!")


if __name__ == "__main__":
    add_terms()
    add_political_parties_and_mps()
