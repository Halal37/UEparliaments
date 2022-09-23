import os
import django
import requests
import logging
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

logger = logging.getLogger(__name__)
os.environ['DJANGO_SETTINGS_MODULE'] = 'UEparliaments.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UEparliaments.settings")

django.setup()
from website.models import ParliamentaryTerm, Parliament, MandateOfMP, MP, PoliticalParty, Country

parliament = Parliament.objects.get(country="Finland", name="Parliament")

headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
           'Accept':
               'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}


def add_mp_and_political_parties():
    try:
        finnish_terms = ParliamentaryTerm.objects.get(parliament=parliament)
        parliamentary_term = finnish_terms.term
        url = "https://www.eduskunta.fi/EN/kansanedustajat/nykyiset_kansanedustajat/Pages/default.aspx"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(url)
        mps = driver.find_elements(By.CLASS_NAME, "edk-list-wrapper")
        for mp in mps:
            name = mp.find_element(By.CLASS_NAME, 'edk-title-h4').text
            last_name = name.split()[-1]
            first_name = name.split(" " + last_name)[0]

            link = mp.find_element(By.TAG_NAME, 'a')
            parliamentary_group = mp.find_element(By.TAG_NAME, 'time').text
            if "Parliamentary Group of the " in parliamentary_group:
                party = parliamentary_group.split("Parliamentary Group of the ")[1]
            else:
                party = parliamentary_group.split(" Parliamentary Group")[0]
            pageTree = requests.get(
                link.get_attribute('href'),
                headers=headers)
            soup = BeautifulSoup(pageTree.content, 'html.parser')
            mandate = soup.find_all("div", {"class": "MOPContainer"})[1]
            if "Electoral district:" not in mandate.get_text():
                mandate = soup.find_all("div", {"class": "MOPContainer"})[2]

            mandate = mandate.get_text().split("–")[0][-10:]
            mandate = datetime.strptime(mandate, '%d.%m.%Y').strftime(
                '%Y-%m-%d')
            if mandate <= "2019-04-17":
                mandate = "2019-04-17"
            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Finland"), name=party)

            MP.objects.get_or_create(first_name=first_name,
                                     last_name=last_name)

            MandateOfMP.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Finland", name=party),
                parliamentary_term=ParliamentaryTerm.objects.get(
                        parliament=parliament,
                        term=parliamentary_term),
                parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                         last_name=last_name),
                beginning_of_term=mandate,
                end_of_term=None)

    except Exception as e:
        print("Could not save: ")
        print(e)


    print("Action complete!")

if __name__ == "__main__":
    add_mp_and_political_parties()
