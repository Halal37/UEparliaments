"""UEparliaments URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
from website import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('website.urls')),
    path('api_schema/', get_schema_view(
        title='API Schema',
        description='Guide for the REST API'
    ), name='api_schema'),
    path('docs/', TemplateView.as_view(
        template_name='docs.html',
        extra_context={'schema_url': 'api_schema'}
    ), name='swagger-ui'),
    path('', views.home_view_screen, name='home'),
    path('epp', views.epp_home_view_screen, name='epp'),
    path('parliaments', views.parliaments_home_view_screen, name='parliaments'),
    path('parliaments/<str:country>/', views.parliaments_country_view_screen, name='parliaments_country'),
    path('parliaments/<str:country>/<str:house>/', views.parliaments_house_view_screen, name='parliaments_house'),
    path('elections', views.elections_home_view_screen, name='elections'),
    path('about', views.about_home_view_screen, name='about'),

]
