import os
import django
import requests
import logging
import sys
from bs4 import BeautifulSoup
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

logger = logging.getLogger(__name__)
os.environ['DJANGO_SETTINGS_MODULE'] = 'UEparliaments.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UEparliaments.settings")

django.setup()
from website.models import ParliamentaryTerm, Parliament, MandateOfMP, MP, PoliticalParty, Country

headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
           'Accept':
               'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

parliament = Parliament.objects.get(country="Italy", name="Chamber of Deputies")


def add_current_term_mps_and_political_parties(link, gender):
    try:
        pageTree = requests.get(
            link,
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        mps = soup.find("ul", {"class": "main_img_ul"})
        mps = mps.find_all("li")
        for mp in mps:
            mp_link = mp.find_all("a")[2]['href']
            name = mp.find_all("a")[2].get_text()
            name = name.replace("\'", "")
            political_party = mp.find_all("a")[3].get_text()
            splited_name = re.findall('[A-Z][a-z]*', name)
            list_of_lengths = (lambda x: [len(i) for i in x])(splited_name)
            for number, length in enumerate(list_of_lengths):
                if length > 1:
                    last_name = name.split(splited_name[number])[0]
                    first_name = name.split(last_name)[1]
                    last_name = last_name.title()
                    break

            if political_party == "FRATELLI D'ITALIA":
                political_party = "Fratelli d'Italia"
            elif political_party == "MOVIMENTO 5 STELLE":
                political_party = "MoVimento 5 Stelle"
            elif political_party == "LEGA - SALVINI PREMIER":
                political_party = "Lega Salvini Premier"
            elif political_party == "PARTITO DEMOCRATICO - ITALIA DEMOCRATICA E PROGRESSISTA":
                political_party = "Partito Democratico"
            elif political_party == "FORZA ITALIA - BERLUSCONI PRESIDENTE - PPE":
                political_party = "Forza Italia"
            elif political_party == "AZIONE - ITALIA VIVA - RENEW EUROPE":
                political_party = "Azione-ItaliaViva"
            elif "MISTO - non iscritto ad alcuna componente" in political_party:
                political_party = "Misto"
            elif political_party == "MISTO-MINORANZE LINGUISTICHE":
                political_party = "Misto"
            elif political_party == "MISTO-+EUROPA":
                political_party = "Misto"
            elif political_party == "NOI MODERATI (NOI CON L'ITALIA, CORAGGIO ITALIA, UDC, ITALIA AL CENTRO)-MAIE":
                political_party = "Civici d'Italia"
            elif political_party == "ALLEANZA VERDI E SINISTRA":
                political_party = "Alleanza Verdi e Sinistra"

            member_pageTree = requests.get(
                f"https://www.camera.it/leg19/{mp_link}",
                headers=headers)
            member_soup = BeautifulSoup(member_pageTree.content, 'html.parser')
            info = member_soup.find("div", {"class": "datibiografici"}).get_text()
            if "il " in info:
                date_of_birth = get_date_of_birth(info, "il ")
            elif "l'" in info:
                date_of_birth = get_date_of_birth(info, "l'")
            MP.objects.get_or_create(first_name=first_name,
                                     last_name=last_name, gender=gender, date_of_birth=date_of_birth)

            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Italy"),
                name=political_party)

            parliamentary_term = ParliamentaryTerm.objects.get(
                parliament=parliament,
                term="19")
            MandateOfMP.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Italy",
                                                 name=political_party),
                parliamentary_term=parliamentary_term,
                parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                         last_name=last_name, gender=gender,
                                                         date_of_birth=date_of_birth),
                beginning_of_term="2022-10-13",
                end_of_term=None)

        if soup.find("li", {"class": "next"}).find("a") is not None:
            next_link = soup.find("li", {"class": "next"}).find("a")['href']
            add_current_term_mps_and_political_parties(f"https://www.camera.it/leg19/{next_link}", gender)


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def replace_italian_months(text):
    text = text.replace("gennaio", "01").replace("febbraio", "02").replace("marzo", "03").replace("aprile",
                                                                                                  "04").replace(
        "maggio", "05").replace(
        "giugno", "06").replace("luglio", "07").replace("agosto", "08").replace("settembre", "09").replace("ottobre",
                                                                                                           "10").replace(
        "novembre", "11").replace("dicembre", "12")
    return text


def get_date_of_birth(info, text):
    date_of_birth = info.split(text)[1]
    date_of_birth = date_of_birth.splitlines()[0]
    date_of_birth = date_of_birth.replace("°", "")
    date_of_birth = replace_italian_months(date_of_birth)
    temporary_date_of_birth = date_of_birth.split()
    date_of_birth = " ".join(temporary_date_of_birth)
    date_of_birth = datetime.strptime(date_of_birth, '%d %m %Y').strftime('%Y-%m-%d')
    return date_of_birth


if __name__ == "__main__":
    add_current_term_mps_and_political_parties(
        "https://www.camera.it/leg19/313?current_page_2632=1&shadow_deputato_has_provincia_di_nascita=&shadow_deputato_has_cognome_notorieta=&shadow_titolidistudio=&shadow_circoscrizioni=&shadow_gruppi_parlamentari=&shadow_deputato_has_sesso=F&shadow_deputato_range_eta=&shadow_professione=",
        "female")
    add_current_term_mps_and_political_parties(
        "https://www.camera.it/leg19/313?current_page_2632=1&shadow_deputato_has_provincia_di_nascita=&shadow_deputato_has_cognome_notorieta=&shadow_titolidistudio=&shadow_circoscrizioni=&shadow_gruppi_parlamentari=&shadow_deputato_has_sesso=M&shadow_deputato_range_eta=&shadow_professione=",
        "male")
