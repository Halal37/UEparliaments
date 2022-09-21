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

parliament = Parliament.objects.get(country="Portugal", name="Assembly of the Republic")

information_base = [
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d5a76636d3168773666446f32386c4d6a424359584e6c4c3168574a5449775447566e61584e7359585231636d45765357356d62334a7459574e6862304a6863325659566c3971633239754c6e523464413d3d&fich=InformacaoBaseXV_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d5a76636d3168773666446f32386c4d6a424359584e6c4c31684a566955794d45786c5a326c7a6247463064584a684c306c755a6d39796257466a5957394359584e6c57456c575832707a6232347564486830&fich=InformacaoBaseXIV_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d5a76636d3168773666446f32386c4d6a424359584e6c4c31684a53556b6c4d6a424d5a57647063327868644856795953394a626d5a76636d316859324676516d467a5a56684a53556c66616e4e76626935306548513d&fich=InformacaoBaseXIII_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d5a76636d3168773666446f32386c4d6a424359584e6c4c31684a535355794d45786c5a326c7a6247463064584a684c306c755a6d39796257466a5957394359584e6c57456c4a5832707a6232347564486830&fich=InformacaoBaseXII_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d5a76636d3168773666446f32386c4d6a424359584e6c4c31684a4a5449775447566e61584e7359585231636d45765357356d62334a7459574e6862304a686332565953563971633239754c6e523464413d3d&fich=InformacaoBaseXI_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d5a76636d3168773666446f32386c4d6a424359584e6c4c31676c4d6a424d5a57647063327868644856795953394a626d5a76636d316859324676516d467a5a566866616e4e76626935306548513d&fich=InformacaoBaseX_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d5a76636d3168773666446f32386c4d6a424359584e6c4c306c594a5449775447566e61584e7359585231636d45765357356d62334a7459574e6862304a686332564a57463971633239754c6e523464413d3d&fich=InformacaoBaseIX_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d5a76636d3168773666446f32386c4d6a424359584e6c4c315a4a53556b6c4d6a424d5a57647063327868644856795953394a626d5a76636d316859324676516d467a5a565a4a53556c66616e4e76626935306548513d&fich=InformacaoBaseVIII_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d5a76636d3168773666446f32386c4d6a424359584e6c4c315a4a535355794d45786c5a326c7a6247463064584a684c306c755a6d39796257466a5957394359584e6c566b6c4a5832707a6232347564486830&fich=InformacaoBaseVII_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d5a76636d3168773666446f32386c4d6a424359584e6c4c315a4a4a5449775447566e61584e7359585231636d45765357356d62334a7459574e6862304a686332565753563971633239754c6e523464413d3d&fich=InformacaoBaseVI_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d5a76636d3168773666446f32386c4d6a424359584e6c4c31596c4d6a424d5a57647063327868644856795953394a626d5a76636d316859324676516d467a5a565a66616e4e76626935306548513d&fich=InformacaoBaseV_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d5a76636d3168773666446f32386c4d6a424359584e6c4c306c574a5449775447566e61584e7359585231636d45765357356d62334a7459574e6862304a686332564a566c3971633239754c6e523464413d3d&fich=InformacaoBaseIV_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d5a76636d3168773666446f32386c4d6a424359584e6c4c306c4a535355794d45786c5a326c7a6247463064584a684c306c755a6d39796257466a5957394359584e6c53556c4a5832707a6232347564486830&fich=InformacaoBaseIII_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d5a76636d3168773666446f32386c4d6a424359584e6c4c306c4a4a5449775447566e61584e7359585231636d45765357356d62334a7459574e6862304a686332564a53563971633239754c6e523464413d3d&fich=InformacaoBaseII_json.txt&Inline=true",
]

biography = [
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e5276637939535a576470633352764a544977516d6c765a334c446f575a70593238765746596c4d6a424d5a5764706332786864485679595339535a57647063335276516d6c765a334a685a6d6c6a623168575832707a6232347564486830&fich=RegistoBiograficoXV_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e5276637939535a576470633352764a544977516d6c765a334c446f575a705932387657456c574a5449775447566e61584e7359585231636d4576556d566e61584e3062304a706232647959575a705932395953565a66616e4e76626935306548513d&fich=RegistoBiograficoXIV_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e5276637939535a576470633352764a544977516d6c765a334c446f575a705932387657456c4a535355794d45786c5a326c7a6247463064584a684c314a6c5a326c7a644739436157396e636d466d61574e7657456c4a53563971633239754c6e523464413d3d&fich=RegistoBiograficoXIII_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e5276637939535a576470633352764a544977516d6c765a334c446f575a705932387657456c4a4a5449775447566e61584e7359585231636d4576556d566e61584e3062304a706232647959575a705932395953556c66616e4e76626935306548513d&fich=RegistoBiograficoXII_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e5276637939535a576470633352764a544977516d6c765a334c446f575a705932387657456b6c4d6a424d5a5764706332786864485679595339535a57647063335276516d6c765a334a685a6d6c6a6231684a5832707a6232347564486830&fich=RegistoBiograficoXI_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e5276637939535a576470633352764a544977516d6c765a334c446f575a7059323876574355794d45786c5a326c7a6247463064584a684c314a6c5a326c7a644739436157396e636d466d61574e7657463971633239754c6e523464413d3d&fich=RegistoBiograficoX_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e5276637939535a576470633352764a544977516d6c765a334c446f575a70593238765356676c4d6a424d5a5764706332786864485679595339535a57647063335276516d6c765a334a685a6d6c6a62306c595832707a6232347564486830&fich=RegistoBiograficoIX_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e5276637939535a576470633352764a544977516d6c765a334c446f575a7059323876566b6c4a535355794d45786c5a326c7a6247463064584a684c314a6c5a326c7a644739436157396e636d466d61574e76566b6c4a53563971633239754c6e523464413d3d&fich=RegistoBiograficoVIII_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e5276637939535a576470633352764a544977516d6c765a334c446f575a7059323876566b6c4a4a5449775447566e61584e7359585231636d4576556d566e61584e3062304a706232647959575a705932395753556c66616e4e76626935306548513d&fich=RegistoBiograficoVII_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e5276637939535a576470633352764a544977516d6c765a334c446f575a7059323876566b6b6c4d6a424d5a5764706332786864485679595339535a57647063335276516d6c765a334a685a6d6c6a62315a4a5832707a6232347564486830&fich=RegistoBiograficoVI_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e5276637939535a576470633352764a544977516d6c765a334c446f575a7059323876566955794d45786c5a326c7a6247463064584a684c314a6c5a326c7a644739436157396e636d466d61574e76566c3971633239754c6e523464413d3d&fich=RegistoBiograficoV_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e5276637939535a576470633352764a544977516d6c765a334c446f575a70593238765356596c4d6a424d5a5764706332786864485679595339535a57647063335276516d6c765a334a685a6d6c6a62306c575832707a6232347564486830&fich=RegistoBiograficoIV_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e5276637939535a576470633352764a544977516d6c765a334c446f575a705932387653556c4a4a5449775447566e61584e7359585231636d4576556d566e61584e3062304a706232647959575a705932394a53556c66616e4e76626935306548513d&fich=RegistoBiograficoIII_json.txt&Inline=true",
    "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e5276637939535a576470633352764a544977516d6c765a334c446f575a705932387653556b6c4d6a424d5a5764706332786864485679595339535a57647063335276516d6c765a334a685a6d6c6a62306c4a5832707a6232347564486830&fich=RegistoBiograficoII_json.txt&Inline=true",

]


def add_term():
    try:
        for term in information_base:
            response = requests.get(
                term)
            data = response.text
            parse_json = json.loads(data)
            if parse_json['Legislatura']['DetalheLegislatura']['dtini'] <= '1987-08-13':
                ParliamentaryTerm.objects.get_or_create(seats=250, term=roman.fromRoman(
                    parse_json['Legislatura']['DetalheLegislatura']['sigla']),
                                                        parliament=parliament,
                                                        beginning_of_term=
                                                        parse_json['Legislatura']['DetalheLegislatura']['dtini'],
                                                        end_of_term=parse_json['Legislatura']['DetalheLegislatura'][
                                                            'dtfim'])
            elif parse_json['Legislatura']['DetalheLegislatura']['sigla'] == "XIV":
                ParliamentaryTerm.objects.get_or_create(seats=230, term=roman.fromRoman(
                    parse_json['Legislatura']['DetalheLegislatura']['sigla']),
                                                        parliament=parliament,
                                                        beginning_of_term=
                                                        parse_json['Legislatura']['DetalheLegislatura']['dtini'],
                                                        end_of_term="2021-12-04")
            elif parse_json['Legislatura']['DetalheLegislatura']['sigla'] == "XV":
                ParliamentaryTerm.objects.get_or_create(seats=230, term=roman.fromRoman(
                    parse_json['Legislatura']['DetalheLegislatura']['sigla']),
                                                        parliament=parliament,
                                                        beginning_of_term=
                                                        parse_json['Legislatura']['DetalheLegislatura']['dtini'],
                                                        end_of_term=None)
            else:
                ParliamentaryTerm.objects.get_or_create(seats=230, term=roman.fromRoman(
                    parse_json['Legislatura']['DetalheLegislatura']['sigla']),
                                                        parliament=parliament,
                                                        beginning_of_term=
                                                        parse_json['Legislatura']['DetalheLegislatura']['dtini'],
                                                        end_of_term=parse_json['Legislatura']['DetalheLegislatura'][
                                                            'dtfim'])
            for party in parse_json['Legislatura']['GruposParlamentares']['pt_gov_ar_objectos_GPOut']:
                PoliticalParty.objects.get_or_create(
                    country=Country.objects.get(country_name="Portugal"), name=party['sigla'])


    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


def add_mps():
    try:
        for term in biography:
            response = requests.get(
                term)
            data = response.text
            parse_json = json.loads(data)
            for element in parse_json['RegistoBiografico']['RegistoBiograficoList'][
                'pt_ar_wsgode_objectos_DadosRegistoBiograficoWeb']:
                if element["cadSexo"] is "F":
                    gender = "female"
                else:
                    gender = "male"
                if "cadDtNascimento" in element:
                    date_of_birth = element["cadDtNascimento"]
                else:
                    date_of_birth = None
                if type(element["cadDeputadoLegis"]["pt_ar_wsgode_objectos_DadosDeputadoLegis"]) is not list:
                    if element["cadDeputadoLegis"]["pt_ar_wsgode_objectos_DadosDeputadoLegis"]["legDes"] == "Cons" or \
                            element["cadDeputadoLegis"]["pt_ar_wsgode_objectos_DadosDeputadoLegis"]["legDes"] == "IB" or \
                            element["cadDeputadoLegis"]["pt_ar_wsgode_objectos_DadosDeputadoLegis"]["legDes"] == "IA":
                        continue
                    parliamentary_term = roman.fromRoman(
                        element["cadDeputadoLegis"]["pt_ar_wsgode_objectos_DadosDeputadoLegis"]["legDes"])
                    party = element["cadDeputadoLegis"]["pt_ar_wsgode_objectos_DadosDeputadoLegis"]["parSigla"]
                    PoliticalParty.objects.get_or_create(
                        country=Country.objects.get(country_name="Portugal"), name=party)
                    if " DE " in element["cadDeputadoLegis"]["pt_ar_wsgode_objectos_DadosDeputadoLegis"][
                        "depNomeParlamentar"]:
                        first_name = element["cadDeputadoLegis"]["pt_ar_wsgode_objectos_DadosDeputadoLegis"][
                            "depNomeParlamentar"].split(" DE")[0].lower().title()
                        last_name = "de" + element["cadDeputadoLegis"]["pt_ar_wsgode_objectos_DadosDeputadoLegis"][
                            "depNomeParlamentar"].split(" DE")[1].lower().title()
                    else:
                        last_name = element["cadDeputadoLegis"]["pt_ar_wsgode_objectos_DadosDeputadoLegis"][
                            "depNomeParlamentar"].split()[-1].lower().title()
                        first_name = element["cadDeputadoLegis"]["pt_ar_wsgode_objectos_DadosDeputadoLegis"][
                            "depNomeParlamentar"].lower().title().split(" " + last_name)[0]
                    MP.objects.get_or_create(first_name=first_name,
                                             last_name=last_name,
                                             gender=gender,
                                             date_of_birth=date_of_birth)
                    if parliamentary_term >= 2:
                        link = information_base[15 - parliamentary_term]
                    else:
                        break

                    link_response = requests.get(
                        link)
                    link_data = link_response.text
                    link_parse_json = json.loads(link_data)
                    for deputy in link_parse_json['Legislatura']["Deputados"][
                        "pt_ar_wsgode_objectos_DadosDeputadoSearch"]:
                        if deputy["depNomeParlamentar"] == \
                                element["cadDeputadoLegis"]["pt_ar_wsgode_objectos_DadosDeputadoLegis"][
                                    "depNomeParlamentar"]:
                            if type(deputy["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"]) is list:
                                for terms in deputy["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"]:
                                    beginning_of_term = terms["gpDtInicio"]
                                    if "gpDtFim" in terms:
                                        if terms["gpDtFim"] == "2022-08-22":
                                           end_of_term = None
                                        else:
                                            end_of_term = terms["gpDtFim"]
                                    else:
                                        end_of_term = None
                            else:
                                beginning_of_term = deputy["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"][
                                    "gpDtInicio"]
                                if "gpDtFim" in deputy["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"]:
                                    if deputy["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"][
                                        "gpDtFim"] == "2022-08-22":
                                        end_of_term = None
                                    else:
                                        end_of_term = deputy["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"][
                                            "gpDtFim"]
                                else:
                                    end_of_term = None
                            MandateOfMP.objects.get_or_create(
                                party=PoliticalParty.objects.get(country="Portugal", name=party),
                                parliamentary_term=ParliamentaryTerm.objects.get(
                                    parliament=parliament,
                                    term=parliamentary_term),
                                parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                                         last_name=last_name,
                                                                         gender=gender,
                                                                         date_of_birth=date_of_birth),
                                beginning_of_term=beginning_of_term,
                                end_of_term=end_of_term)

                            break
                else:
                    for i in element["cadDeputadoLegis"]["pt_ar_wsgode_objectos_DadosDeputadoLegis"]:
                        if i["legDes"] == "Cons" or i["legDes"] == "IB" or i["legDes"] == "IA":
                            continue
                        parliamentary_term = roman.fromRoman(
                            i["legDes"])
                        party = i["parSigla"]
                        PoliticalParty.objects.get_or_create(
                            country=Country.objects.get(country_name="Portugal"), name=party)
                        if " DE " in i["depNomeParlamentar"]:
                            first_name = i["depNomeParlamentar"].split(" DE")[0].lower().title()
                            last_name = "de" + i["depNomeParlamentar"].split(" DE")[1].lower().title()
                        else:
                            last_name = i["depNomeParlamentar"].split()[-1].lower().title()
                            first_name = i["depNomeParlamentar"].lower().title().split(" " + last_name)[0]
                        MP.objects.get_or_create(first_name=first_name,
                                                 last_name=last_name,
                                                 gender=gender,
                                                 date_of_birth=date_of_birth)
                        if parliamentary_term >= 2:
                            link = information_base[15 - parliamentary_term]
                        else:
                            break
                        exists = MandateOfMP.objects.filter(parliamentary_term=ParliamentaryTerm.objects.get(
                            parliament=parliament,
                            term=parliamentary_term),
                            parliament=parliament,
                            party=PoliticalParty.objects.get(country="Portugal", name=party),
                            mp=MP.objects.get(first_name=first_name,
                                              last_name=last_name,
                                              gender=gender,
                                              date_of_birth=date_of_birth))
                        if len(exists) > 0:
                            continue

                        link_response = requests.get(
                            link)
                        link_data = link_response.text
                        link_parse_json = json.loads(link_data)
                        for deputy in link_parse_json['Legislatura']["Deputados"][
                            "pt_ar_wsgode_objectos_DadosDeputadoSearch"]:
                            if deputy["depNomeParlamentar"] == i["depNomeParlamentar"]:
                                if type(deputy["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"]) is list:
                                    for terms in deputy["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"]:
                                        beginning_of_term = terms["gpDtInicio"]
                                        if "gpDtFim" in terms:
                                            if terms["gpDtFim"] == "2022-08-22":
                                                end_of_term = None
                                            else:
                                                end_of_term = terms["gpDtFim"]
                                        else:
                                            end_of_term = None
                                else:
                                    beginning_of_term = deputy["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"][
                                        "gpDtInicio"]
                                    if "gpDtFim" in deputy["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"]:
                                        if deputy["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"][
                                            "gpDtFim"] == "2022-08-22":
                                            end_of_term = None
                                        else:
                                            end_of_term = deputy["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"][
                                                "gpDtFim"]

                                    else:
                                        end_of_term = None
                                MandateOfMP.objects.get_or_create(
                                    party=PoliticalParty.objects.get(country="Portugal", name=party),
                                    parliamentary_term=ParliamentaryTerm.objects.get(
                                        parliament=parliament,
                                        term=parliamentary_term),
                                    parliament=parliament, mp=MP.objects.get(first_name=first_name,
                                                                             last_name=last_name,
                                                                             gender=gender,
                                                                             date_of_birth=date_of_birth),
                                    beginning_of_term=beginning_of_term,
                                    end_of_term=end_of_term)

                                break

            # TODO: MPS




    except Exception as e:
        print("Could not save: ")
        print(e)
    print("Action complete!")


if __name__ == "__main__":
    add_mps()
    add_term()
