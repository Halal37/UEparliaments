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
from website.models import SenateTerm, Senate, MandateOfSenator, Senator, PoliticalParty, Country, Parliament, \
    ParliamentaryTerm, MP, MandateOfMP

parliament = Parliament.objects.get(country="The Netherlands", name="House of Representatives")
senate = Senate.objects.get(country="The Netherlands", name="Senate")


def add_political_parties():
    try:
        response = requests.get(
            "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/fractie")
        data = response.text
        parse_json = json.loads(data)
        for element in parse_json["value"]:
            if element["DatumActief"] is not None:
                PoliticalParty.objects.get_or_create(
                    country=Country.objects.get(country_name="The Netherlands"), name=element["Afkorting"],
                    founded=element["DatumActief"].split("T")[0])


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_mps_and_senators(link, count_senators, count_mp):
    try:
        response = requests.get(
            link)
        data = response.text
        parse_json = json.loads(data)
        for element in parse_json["value"]:

            if element["Tussenvoegsel"] is not None:
                last_name = element["Tussenvoegsel"] + " " + element["Achternaam"]
            else:
                last_name = element["Achternaam"]
            if element["Voornamen"] is not None:
                first_name = element["Voornamen"]
            else:
                first_name = element["Initialen"]
            if element["Geboortedatum"] is not None:
                date_of_birth = element["Geboortedatum"].split("T")[0]
            else:
                date_of_birth = None

            if element["Geslacht"] == "vrouw":
                gender = "female"
            else:
                gender = "male"

            if element["Functie"] == "Eerste Kamerlid":
                PoliticalParty.objects.get_or_create(
                    country=Country.objects.get(country_name="The Netherlands"),
                    name=last_name.split("(")[1].split(")")[0])
                count_senators += 1
                Senator.objects.get_or_create(first_name=first_name,
                                              last_name=last_name.split("(")[0],
                                              gender=gender,
                                              date_of_birth=date_of_birth)
                MandateOfSenator.objects.get_or_create(
                    party=PoliticalParty.objects.get(country="The Netherlands",
                                                     name=last_name.split("(")[1].split(")")[0]),
                    senate_term=SenateTerm.objects.get(senate=senate, term="10"),
                    senate=senate, senator=Senator.objects.get(first_name=first_name,
                                                               last_name=last_name.split("(")[0]),
                    beginning_of_term="2019-06-11",
                    end_of_term=None)
            elif element["Functie"] == "Tweede Kamerlid":
                count_mp += 1
                MP.objects.get_or_create(first_name=first_name,
                                         last_name=last_name,
                                         gender=gender,
                                         date_of_birth=date_of_birth)

        if "@odata.nextLink" in parse_json:
            add_mps_and_senators(parse_json["@odata.nextLink"], count_senators, count_mp)


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_mps_mandates(link):
    try:
        response = requests.get(
            link)
        data = response.text
        parse_json = json.loads(data)
        for element in parse_json["value"]:
            if element["Persoon_Id"] is None:
                continue
            if element["TotEnMet"] is None:
                pass
            elif element["TotEnMet"].split("T")[0] > "2019-06-11":
                pass
            else:
                continue

            deputy_id = element["Persoon_Id"]
            response_deputy = requests.get(
                f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Persoon/{deputy_id}")
            data_deputy = response_deputy.text
            parse_json_deputy = json.loads(data_deputy)

            if parse_json_deputy["Functie"] == "Tweede Kamerlid" and element["TotEnMet"] is None or \
                    element["TotEnMet"].split("T")[0] > "2021-03-31":
                if parse_json_deputy["Voornamen"] is not None:
                    first_name = parse_json_deputy["Voornamen"]
                else:
                    first_name = parse_json_deputy["Initialen"]
            else:
                continue

            group_id = element["FractieZetel_Id"]
            response_group = requests.get(
                f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/FractieZetel/{group_id}")
            data_group = response_group.text
            parse_json_group = json.loads(data_group)
            party_id = parse_json_group["Fractie_Id"]
            response_party = requests.get(
                f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Fractie/{party_id}")
            data_party = response_party.text
            parse_json_party = json.loads(data_party)

            if parse_json_deputy["Tussenvoegsel"] is not None:
                last_name = parse_json_deputy["Tussenvoegsel"] + " " + parse_json_deputy["Achternaam"]
            else:
                last_name = parse_json_deputy["Achternaam"]

            if element["TotEnMet"] is not None:
                end_of_term = element["TotEnMet"].split("T")[0]
            else:
                end_of_term = None

            if element["Van"] > "2021-03-31":
                beginning_of_term = element["Van"].split("T")[0]
            else:
                beginning_of_term = "2021-03-31"

            if parse_json_deputy["Functie"] == "Tweede Kamerlid":
                MandateOfMP.objects.get_or_create(
                    party=PoliticalParty.objects.get(country="The Netherlands", name=parse_json_party["Afkorting"]),
                    parliamentary_term=ParliamentaryTerm.objects.get(parliament=parliament, term="16"),
                    parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                             last_name=last_name),
                    beginning_of_term=beginning_of_term,
                    end_of_term=end_of_term)

        if "@odata.nextLink" in parse_json:
            add_mps_mandates(parse_json["@odata.nextLink"])


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_senators():
    pass


if __name__ == "__main__":
    add_political_parties()
    add_mps_and_senators("https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Persoon", 0, 0)
    add_mps_mandates("https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/FractieZetelPersoon")
