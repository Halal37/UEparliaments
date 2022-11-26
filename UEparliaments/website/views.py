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
    print(request.headers)
    parliament = Parliament.objects.get(country="Latvia")

    term = ParliamentaryTerm.objects.get(parliament=parliament)
    mandates = MandateOfMP.objects.filter(parliamentary_term=term)
    #value = mandates
    value = []
    for mandate in mandates:
       value.append(mandate.mp)
    return render(request, 'UEparliaments/home.html', {"value": value})


"""
def estonia(request):
    response = requests.get("https://api.riigikogu.ee/api/plenary-members?lang=EN")
    print(response)
    return render(request, 'estonia.html', {'response': response})
"""
