import json
from django.shortcuts import HttpResponse, render, get_object_or_404
from django.http import HttpResponse, Http404
from django.core import serializers
from django.db.models import Q

from django.views.generic import TemplateView
from django.forms import formset_factory

from .models import City, Department
from .forms import ParamForm, JourneyForm
from tools.calculations import *
from itertools import chain
from dal import autocomplete

import re


def index(request):
    response = 'Hello, world'
    return HttpResponse(response)


def pp2m_search(request, dep_cities_dict, method, criteria):

    # Get weightings
    df_dict = get_cities_weightings(dep_cities_dict, method)

    # Convert in JSON
    dep_cities_list = [x['city'] for x in dep_cities_dict]
    dep_cities_nbpeople = [x['nb_people'] for x in dep_cities_dict]
    cities_json = serializers.serialize('json', dep_cities_list, fields=('name', 'latitude', 'longitude', 'pref_name'))
    nbpeople_json = json.dumps(dep_cities_nbpeople)
    method_json = json.dumps(method)
    criteria_json = json.dumps(criteria)

    results_json = {}
    for crit in df_dict:
        result = df_dict[crit].to_json(orient="records")
        parsed = json.loads(result)
        results_json[crit] = json.dumps(parsed)

    # Render
    return render(request, 'find_pp2m/pp2m_distance.html', {
        'initial_cities': cities_json,
        'nb_people': nbpeople_json,
        'method': method_json,
        'criteria': criteria_json,
        'results_com': results_json['com'],
        'results_ind': results_json['ind'],
        'results_mix': results_json['mix']
    })


def pp2m_form(request):
    JourneyFormSet = formset_factory(JourneyForm, extra=1, min_num=2, validate_min=True)
    if request.method == 'POST':
        formset = JourneyFormSet(request.POST, request.FILES)
        paramForm = ParamForm(request.POST)

        if formset.is_valid() and paramForm.is_valid():
            cities_dict = [form.cleaned_data for form in formset if len(form.cleaned_data) > 0]
            cities_dict = [item for item in cities_dict if item['city'] is not None]
 
            method = paramForm.cleaned_data['method']
            criteria = paramForm.cleaned_data['criteria']

            return pp2m_search(request, cities_dict, method, criteria)


    else:
        formset = JourneyFormSet()
        paramForm = ParamForm()
    return render(request, 'find_pp2m/pp2m_formset.html', {'journey_formset': formset, 'param_form': paramForm})


class CityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated:
        #     return City.objects.none()

        qs = City.objects.all()

        if self.q:
            self.q = re.sub('[aàâäAÀÁÂÃÄÅÆ]', 'a', self.q)
            self.q = re.sub('[cçC]', 'c', self.q)
            self.q = re.sub('[eéèêëEÉÈÊË]', 'e', self.q)
            self.q = re.sub('[iïîIÌÍÎÏ]', 'i', self.q)
            self.q = re.sub('[oôöÒÓÔÕÖ]', 'o', self.q)
            self.q = re.sub('[uüûùUÜÛÙÚ]', 'u', self.q)
            self.q = re.sub('[yYÿÝ]', 'y', self.q)
            self.q = self.q.replace(' ', '-')
            self.q = self.q.lower()
            qs = qs.filter(slug__istartswith=self.q)

        return qs