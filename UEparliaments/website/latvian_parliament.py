import os
import django
import requests
import logging
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

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

parliament = Parliament.objects.get(country="Latvia", name="Saeima")

def get_political_party_info(link):
    url = link
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    driver.maximize_window()
    mp_info = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'wholeForm')))
    mp_info = \
    mp_info.find_element(By.TAG_NAME, "tbody").find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "td")[1].text
    political_party = mp_info.split("Elected from the following candidate list: ")[1].splitlines()[0]
    if political_party == "“THE UNITED LIST – Latvian Green Party, Latvian Regional Alliance, Liepāja Party”":
        political_party = "The United List"
    elif political_party == "National Alliance “All For Latvia!”–“For Fatherland and Freedom/LNNK”":
        political_party = "National Alliance"
    elif political_party == "Political Party “For Stability!”":
        political_party = "For Stability!"
    else:
        political_party = political_party.title()
    return political_party

def add_current_term_mps_and_political_parties(side):
    try:
        pageTree = requests.get(
            "https://titania.saeima.lv/personal/deputati/saeima14_depweb_public.nsf/deputies?OpenView&lang=EN&count=1000",
            headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        url = "https://titania.saeima.lv/personal/deputati/saeima14_depweb_public.nsf/deputies?OpenView&lang=EN&count=1000"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(url)
        mps = driver.find_elements(By.CLASS_NAME, side)

        for mp in mps:
            last_name = mp.find_element(By.CLASS_NAME, 'sortedCol').text
            first_name = mp.find_elements(By.TAG_NAME, 'td')[1].text
            link = mp.get_attribute("onclick")
            link = link.split("opnHref('")[1].split("')")[0]
            link = link.split("&url=.")[1]
            link = "https://titania.saeima.lv/personal/deputati/saeima14_depweb_public.nsf/"+link
            url = link
            political_party=get_political_party_info(url)
            MP.objects.get_or_create(first_name=first_name,
                                     last_name=last_name)

            PoliticalParty.objects.get_or_create(
                country=Country.objects.get(country_name="Latvia"),
                name=political_party)

            parliamentary_term = ParliamentaryTerm.objects.get(
                parliament=parliament,
                term="14")
            MandateOfMP.objects.get_or_create(
                party=PoliticalParty.objects.get(country="Latvia",
                                                 name=political_party),
                parliamentary_term=parliamentary_term,
                parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                         last_name=last_name),
                beginning_of_term="2022-11-01",
                end_of_term=None)


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_current_term_mps_and_political_parties("tRowD")
    add_current_term_mps_and_political_parties("tRowL")
