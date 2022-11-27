from django.shortcuts import render
import requests
from rest_framework import viewsets, filters
import django_filters.rest_framework
from .models import Group, Country, Ideology, EuropeanPoliticalParty, PoliticalParty, KeyFunction, TermOfOffice, Senate, \
    SenateTerm, MandateOfSenator, Senator, Parliament, ParliamentaryTerm, MandateOfMP, MP
from .serializer import GroupSerializer, CountrySerializer, IdeologySerializer, EuropeanPoliticalPartySerializer, \
    PoliticalPartySerializer, KeyFunctionSerializer, TermOfOfficeSerializer, SenateSerializer, SenateTermSerializer, \
    MandateOfSenatorSerializer, SenatorSerializer, ParliamentSerializer, ParliamentaryTermSerializer, \
    MandateOfMPSerializer, MPSerializer


# Create your views here.
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class IdeologyViewSet(viewsets.ModelViewSet):
    queryset = Ideology.objects.all()
    serializer_class = IdeologySerializer


class EuropeanPoliticalPartyViewSet(viewsets.ModelViewSet):
    queryset = EuropeanPoliticalParty.objects.all()
    serializer_class = EuropeanPoliticalPartySerializer


class PoliticalPartyViewSet(viewsets.ModelViewSet):
    queryset = PoliticalParty.objects.all()
    serializer_class = PoliticalPartySerializer


class KeyFunctionViewSet(viewsets.ModelViewSet):
    queryset = KeyFunction.objects.all()
    serializer_class = KeyFunctionSerializer


class TermOfOfficeViewSet(viewsets.ModelViewSet):
    queryset = TermOfOffice.objects.all()
    serializer_class = TermOfOfficeSerializer


class SenateViewSet(viewsets.ModelViewSet):
    queryset = Senate.objects.all()
    serializer_class = SenateSerializer


class SenateTermViewSet(viewsets.ModelViewSet):
    queryset = SenateTerm.objects.all()
    serializer_class = SenateTermSerializer


class MandateOfSenatorViewSet(viewsets.ModelViewSet):
    queryset = MandateOfSenator.objects.all()
    serializer_class = MandateOfSenatorSerializer


class SenatorViewSet(viewsets.ModelViewSet):
    queryset = Senator.objects.all()
    serializer_class = SenatorSerializer


class ParliamentViewSet(viewsets.ModelViewSet):
    queryset = Parliament.objects.all()
    serializer_class = ParliamentSerializer


class ParliamentaryTermViewSet(viewsets.ModelViewSet):
    queryset = ParliamentaryTerm.objects.all()
    serializer_class = ParliamentaryTermSerializer


class MandateOfMPViewSet(viewsets.ModelViewSet):
    queryset = MandateOfMP.objects.all()
    serializer_class = MandateOfMPSerializer


class MPViewSet(viewsets.ModelViewSet):
    queryset = MP.objects.all()
    serializer_class = MPSerializer
    search_fields = ['first_name', 'last_name']
    filter_backends = (filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend)
    filterset_fields = ['first_name']


def home_view_screen(request):
    parliament = Parliament.objects.get(country="Latvia")
    term = ParliamentaryTerm.objects.get(parliament=parliament)
    mandates = MandateOfMP.objects.filter(parliamentary_term=term)
    value = []
    for mandate in mandates:
        value.append(mandate.mp)
    return render(request, 'UEparliaments/home.html', {"value": value})


def parliaments_home_view_screen(request):
    countries = Country.objects.all()
    return render(request, 'UEparliaments/parliaments.html', {"countries": countries}, )


def parliaments_country_view_screen(request, country):
    countries = Country.objects.all()
    parliament = Parliament.objects.get(country=country)
    senates = Senate.objects.filter(country=country)
    return render(request, 'UEparliaments/parliaments_country.html',
                  {"countries": countries, "parliament": parliament, "senates": senates}, )


def parliaments_house_view_screen(request, country, house):
    countries = Country.objects.all()
    parliament = Parliament.objects.get(country=country)
    senates = Senate.objects.filter(country=country)
    if house == parliament.name:
        terms = ParliamentaryTerm.objects.filter(parliament=parliament)
    else:
        terms = SenateTerm.objects.filter(senate=senates[0])

    return render(request, 'UEparliaments/parliaments_house.html',
                  {"countries": countries, "parliament": parliament, "senates": senates, "terms": terms,
                   "house": house}, )


def list_of_members_view_screen(request, country, house):
    term = request.GET.get('selected_term', '')
    parliament = Parliament.objects.get(country=country)
    terms = ParliamentaryTerm.objects.filter(parliament=parliament)

    if house in parliament.name:
        for temp_term in terms:
            if temp_term.term == term:
                mandates = MandateOfMP.objects.filter(parliament=parliament, parliamentary_term=temp_term)
    else:
        senate = Senate.objects.get(country=country)
        senate_terms = SenateTerm.objects.filter(senate=senate)
        for temp_term in senate_terms:
            if temp_term.term == term:
                mandates = MandateOfSenator.objects.filter(senate=senate, senate_term=temp_term)
    political_parties = set()
    for mandate in mandates:
        political_parties.add(mandate.party)

    return render(request, 'UEparliaments/list_of_members.html',
                  {"mandates": mandates, "political_parties": political_parties, })


def parliament_view_screen(request, country, house):
    countries = Country.objects.all()
    parliament = Parliament.objects.get(country=country)
    senates = Senate.objects.filter(country=country)
    if house == parliament.name:
        terms = ParliamentaryTerm.objects.filter(parliament=parliament)
    else:
        terms = SenateTerm.objects.filter(senate=senates[0])

    return render(request, 'UEparliaments/home.html',
                  {"countries": countries, "parliament": parliament, "senates": senates, "terms": terms,
                   "house": house}, )


def party_list_of_members_view_screen(request, country, house, term, party):
    parliament = Parliament.objects.get(country=country)
    terms = ParliamentaryTerm.objects.filter(parliament=parliament)
    if party == "Political party":
        pass
    else:
        political_party = PoliticalParty.objects.get(country=country, name=party)
    if house in parliament.name:
        for temp_term in terms:
            if temp_term.term == term:
                mandates = MandateOfMP.objects.filter(parliament=parliament, parliamentary_term=temp_term)
                if party == "Political party":
                    party_mandates = mandates

                else:
                    party_mandates = MandateOfMP.objects.filter(parliament=parliament, parliamentary_term=temp_term,
                                                                party=political_party)


    else:
        senate = Senate.objects.get(country=country)
        senate_terms = SenateTerm.objects.filter(senate=senate)
        for temp_term in senate_terms:
            if temp_term.term == term:
                mandates = MandateOfSenator.objects.filter(senate=senate, senate_term=temp_term)
                if party is not "Political party":
                    party_mandates = mandates
                else:
                    party_mandates = MandateOfSenator.objects.filter(senate=senate, senate_term=temp_term,
                                                                     party=political_party)

    political_parties = set()
    for mandate in mandates:
        political_parties.add(mandate.party)

    return render(request, 'UEparliaments/party_list_of_members.html',
                  {"mandates": party_mandates, "political_parties": political_parties, "current_party": party})


def elections_home_view_screen(request):
    return render(request, 'UEparliaments/elections.html')


def epp_home_view_screen(request):
    return render(request, 'UEparliaments/epp.html')


def about_home_view_screen(request):
    return render(request, 'UEparliaments/about.html')
