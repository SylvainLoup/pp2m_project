from django import forms
from django.core.exceptions import ValidationError
from dal import autocomplete

from .models import City


class JourneyForm(forms.Form):
    city = forms.ModelChoiceField(queryset=City.objects.all(), widget=autocomplete.ModelSelect2(url='find_pp2m:city-autocomplete'), label='Ville', required=False)
    nb_people = forms.IntegerField(min_value=1, label='Gens', initial=1, required=False)
    conveyance_choices = [
        ("car", "En voiture"),
        ("train", "En train")
    ]
    conveyance = forms.CharField(widget=forms.Select(choices=conveyance_choices),
                               initial='car',
                               required=False,
                               label='Moyen de transport')

    def clean(self):
        cleaned_data = super(JourneyForm, self).clean()

        return cleaned_data

    def clean_nb_people(self):
        data = self.cleaned_data['nb_people']
        city_data = self.cleaned_data['city']
        if data is None and city_data is not None:
            raise ValidationError("Le nombre de personnes ne peut pas être vide si une ville est renseignée")
        
        return data

class ParamForm(forms.Form):
    method_choices = [
        ("route_duration", "Temps de trajet"),
        ("route_distance", "Distance"),
        # ("raw_distance", "Distance à vol d'oiseau"),
    ]
    method = forms.CharField(widget=forms.Select(choices=method_choices),
                               initial='route_duration',
                               required=True,
                               label='Méthode de calcul')
    criteria_choices = [
        ("mixed", "Critère mixte"),
        ("community", "Minimiser la somme globale des déplacements"),
        ("individual", "Minimiser le trajet le plus long"),
    ]
    criteria = forms.CharField(widget=forms.Select(choices=criteria_choices),
                               initial='mixed',
                               required=True,
                               label='Critère')

    def clean(self):
        cleaned_data = super(ParamForm, self).clean()

        return cleaned_data
