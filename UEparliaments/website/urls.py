from rest_framework import routers
from django.urls import path, include
from .views import GroupViewSet, CountryViewSet, IdeologyViewSet, EuropeanPoliticalPartyViewSet, PoliticalPartyViewSet, \
    KeyFunctionViewSet, TermOfOfficeViewSet, SenateViewSet, SenateTermViewSet, MandateOfSenatorViewSet, SenatorViewSet, \
    ParliamentViewSet, ParliamentaryTermViewSet, MandateOfMPViewSet, MPViewSet

router = routers.DefaultRouter()
router.register(r'groups', GroupViewSet)
router.register(r"countries", CountryViewSet)
router.register(r"ideologies", IdeologyViewSet)
router.register(r"epps", EuropeanPoliticalPartyViewSet)
router.register(r"politicalpartries", PoliticalPartyViewSet)
router.register(r"keyfunctions", KeyFunctionViewSet)
router.register(r"termofoffices", TermOfOfficeViewSet)
router.register(r"senates", SenateViewSet)
router.register(r"senateterms", SenateTermViewSet)
router.register(r"mandatesofsenators", MandateOfSenatorViewSet)
router.register(r"parliaments", ParliamentViewSet)
router.register(r"parliamentaryterms", ParliamentaryTermViewSet)
router.register(r"mandatesofmps", MandateOfMPViewSet)
router.register(r"mps", MPViewSet)

urlpatterns = [
    path('', include(router.urls))
]
