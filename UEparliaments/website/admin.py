from django.contrib import admin
from .models import Parliament, ParliamentaryTerm, PoliticalParty, EuropeanPoliticalParty, MandateOfMP, MP, Group, \
    Ideology, TermOfOffice, KeyFunction, SenateTerm, Senate, Senator, MandateOfSenator, Country


# Countries

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ['country_name']
    list_display = ['country_name', 'group']
    list_filter = ['group']


# Political parties

@admin.register(Ideology)
class IdeologyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(EuropeanPoliticalParty)
class EuropeanPoliticalPartyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'founded', 'get_ideologies']
    filter_horizontal = ['ideology']

    def get_ideologies(self, obj):
        if obj.ideology.all():
            return list(obj.ideology.all().values_list('name', flat=True))
        else:
            return 'NA'

    get_ideologies.short_description = 'ideologies'


@admin.register(PoliticalParty)
class PoliticalPartyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'founded', 'country', 'epp', 'get_ideologies']
    filter_horizontal = ['ideology']

    def get_ideologies(self, obj):
        if obj.ideology.all():
            return list(obj.ideology.all().values_list('name', flat=True))
        else:
            return 'NA'

    get_ideologies.short_description = 'ideologies'


# Senate

@admin.register(Senate)
class SenateAdmin(admin.ModelAdmin):
    list_display = ['country', 'name']


@admin.register(SenateTerm)
class SenateTermAdmin(admin.ModelAdmin):
    list_display = ['id', 'term', 'seats', 'senate', 'beginning_of_term', 'end_of_term']


@admin.register(Senator)
class SenatorAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'gender', 'term_of_office',
                    'date_of_birth', 'biographical_notes']
    """
    filter_horizontal = ['senate_term']

    def get_terms(self, obj):
        if obj.senate_term.all():
            return list(obj.senate_term.all().values_list('name', flat=True))
        else:
            return 'NA'

    get_terms.short_description = 'terms'
"""

@admin.register(MandateOfSenator)
class MandateOfSenatorAdmin(admin.ModelAdmin):
    list_display = ['id', 'senate', 'senator', 'senate_term', 'party', 'beginning_of_term', 'end_of_term']


# Parliaments


@admin.register(Parliament)
class ParliamentAdmin(admin.ModelAdmin):
    list_display = ['country', 'name']


@admin.register(ParliamentaryTerm)
class ParliamentaryTermAdmin(admin.ModelAdmin):
    list_display = ['id', 'term', 'seats', 'parliament', 'beginning_of_term', 'end_of_term']


@admin.register(MP)
class MPAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'gender',
                    'term_of_office', 'date_of_birth', 'biographical_notes']
"""
    filter_horizontal = ['parliamentary_term']

    def get_terms(self, obj):
        if obj.parliamentary_term.all():
            return list(obj.parliamentary_term.all().values_list('name', flat=True))
        else:
            return 'NA'

    get_terms.short_description = 'terms'
"""

@admin.register(MandateOfMP)
class MandateOfMPAdmin(admin.ModelAdmin):
    list_display = ['id', 'parliament', 'mp', 'parliamentary_term', 'party', 'beginning_of_term', 'end_of_term']


# Office

@admin.register(KeyFunction)
class KeyFunctionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(TermOfOffice)
class TermOfOfficeAdmin(admin.ModelAdmin):
    list_display = ['id', 'key_function', 'beginning_of_term', 'end_of_term']
