from django.db import models


# Countries

class Group(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Country(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    country_name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.country_name

    class Meta:
        verbose_name_plural = "Countries"


# Political parties

class Ideology(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Ideologies"


class EuropeanPoliticalParty(models.Model):
    name = models.CharField(max_length=255)
    founded = models.DateField(null=True)
    ideology = models.ManyToManyField(Ideology, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "European political parties"


class PoliticalParty(models.Model):
    name = models.CharField(max_length=255)
    founded = models.DateField(null=True, blank=True)
    epp = models.ForeignKey(EuropeanPoliticalParty, on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    ideology = models.ManyToManyField(Ideology, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Political parties"


# Office

class KeyFunction(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class TermOfOffice(models.Model):
    beginning_of_term = models.DateField()
    end_of_term = models.DateField()
    key_function = models.ForeignKey(KeyFunction, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.key_function) + " " + str(self.beginning_of_term) + " to " + str(self.end_of_term)


# Senate

class Senate(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.name


class SenateTerm(models.Model):
    seats = models.IntegerField()
    senate = models.ForeignKey(Senate, on_delete=models.CASCADE)
    beginning_of_term = models.DateField(null=True, blank=True)
    end_of_term = models.DateField(null=True, blank=True)
    term = models.CharField(max_length=255)

    def __str__(self):
        return self.term


class Senator(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    term_of_office = models.ForeignKey(TermOfOffice, on_delete=models.CASCADE, null=True, blank=True)
    date_of_birth = models.DateField(null=True)
    biographical_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class MandateOfSenator(models.Model):
    senate = models.ForeignKey(Senate, on_delete=models.CASCADE)
    senator = models.ForeignKey(Senator, on_delete=models.CASCADE)
    senate_term = models.ForeignKey(SenateTerm, blank=True, on_delete=models.CASCADE, null=True)
    party = models.ForeignKey(PoliticalParty, on_delete=models.CASCADE, null=True, blank=True)
    beginning_of_term = models.DateField(null=True)
    end_of_term = models.DateField(null=True)


# Parliaments
class Parliament(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.name


class ParliamentaryTerm(models.Model):
    seats = models.IntegerField()
    parliament = models.ForeignKey(Parliament, on_delete=models.CASCADE)
    beginning_of_term = models.DateField(null=True, blank=True)
    end_of_term = models.DateField(null=True, blank=True)
    term = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return str(self.parliament) + self.term


class MP(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=255, null=True, blank=True)
    term_of_office = models.ForeignKey(TermOfOffice, on_delete=models.CASCADE, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    biographical_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class MandateOfMP(models.Model):
    parliament = models.ForeignKey(Parliament, on_delete=models.CASCADE)
    mp = models.ForeignKey(MP, on_delete=models.CASCADE)
    parliamentary_term = models.ForeignKey(ParliamentaryTerm, blank=True, on_delete=models.CASCADE, null=True)
    party = models.ForeignKey(PoliticalParty, on_delete=models.CASCADE, null=True, blank=True)
    beginning_of_term = models.DateField(null=True)
    end_of_term = models.DateField(null=True)
