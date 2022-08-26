from .models import Group, Country, Ideology, EuropeanPoliticalParty, PoliticalParty, KeyFunction, TermOfOffice, Senate, \
    SenateTerm, MandateOfSenator, Senator, Parliament, ParliamentaryTerm, MandateOfMP, MP
from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['group', 'country_name']


class IdeologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ideology
        fields = ['id', 'name']


class EuropeanPoliticalPartySerializer(serializers.ModelSerializer):
    class Meta:
        model = EuropeanPoliticalParty
        fields = ['id', 'name', 'founded', 'ideology']


class PoliticalPartySerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliticalParty
        fields = ['id', 'name', 'founded', 'epp', 'country', 'ideology']


class KeyFunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyFunction
        fields = ['id', 'name']


class TermOfOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermOfOffice
        fields = ['id', 'beginning_of_term', 'end_of_term', 'key_function']


class SenateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Senate
        fields = ['country', 'name']


class SenateTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = SenateTerm
        fields = ['id', 'seats', 'senate', 'beginning_of_term', 'end_of_term', 'term']


class MandateOfSenatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MandateOfSenator
        fields = ['id', 'senate', 'senator', 'senate_term', 'party', 'beginning_of_term', 'end_of_term']


class SenatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Senator
        fields = ['id', 'first_name', 'last_name', 'gender', 'term_of_office', 'date_of_birth',
                  'biographical_notes']


class ParliamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parliament
        fields = ['country', 'name']


class ParliamentaryTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParliamentaryTerm
        fields = ['id', 'seats', 'parliament', 'beginning_of_term', 'end_of_term', 'term']


class MandateOfMPSerializer(serializers.ModelSerializer):
    class Meta:
        model = MandateOfMP
        fields = ['id', 'parliament', 'mp', 'parliamentary_term', 'party', 'beginning_of_term', 'end_of_term']


class MPSerializer(serializers.ModelSerializer):
    class Meta:
        model = MP
        fields = ['id', 'first_name', 'last_name', 'gender', 'term_of_office',
                  'date_of_birth', 'biographical_notes']
