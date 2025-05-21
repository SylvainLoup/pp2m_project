import math
import numpy as np
import pandas as pd
from django.db.models import Q
from find_pp2m.models import City, Journey


def calculate_distance(city_A, city_B):
    # Calculate as the crow flies distance between two cities
    latA = math.radians(city_A.latitude)
    lonA = math.radians(city_A.longitude)
    latB = math.radians(city_B.latitude)
    lonB = math.radians(city_B.longitude)

    distance = math.acos(math.sin(latA) * math.sin(latB)
                         + math.cos(latA) * math.cos(latB) * math.cos(lonB - lonA)) * 6371

    distance = round(distance, 2)

    return distance


def get_cities_weightings_old(departure_cities_dict, all_cities_list, method):
    depts_weightings_community = []
    depts_weightings_individual = []
    nb_cities = sum([int(city['nb_people']) for city in departure_cities_dict])

    # Get tuples with unique departure cities and their occurences in departure_cities_list
    departure_cities_tuples = [(x['city'], int(x['nb_people'])) for x in departure_cities_dict]

    for city in all_cities_list:
        city_weighting_individual = 0
        city_weighting_community = 0
        for dep_city_tuple in departure_cities_tuples:
            dep_city = dep_city_tuple[0]
            dep_city_occurence = dep_city_tuple[1]
            if dep_city != city:
                journey_weighting = 0
                try:
                    if method == 'raw_distance':
                        journey_weighting = calculate_distance(dep_city, city)
                    elif method == 'route_distance':
                        journey_weighting = Journey.objects.get(departure=dep_city.pref_name, arrival=city.name).distance / 1000
                    elif method == 'route_duration':
                        journey_weighting = Journey.objects.get(departure=dep_city.pref_name, arrival=city.name).duration / 3600
                except:
                    print('Problème avec le trajet {} - {}'.format(dep_city.pref_name, city.name))

                city_weighting_community += journey_weighting * dep_city_occurence
                if journey_weighting > city_weighting_individual:
                    city_weighting_individual = journey_weighting

        depts_weightings_community.append((city.num_department, city_weighting_community / nb_cities))
        depts_weightings_individual.append((city.num_department, city_weighting_individual))

    depts_weightings = {
        'com' : depts_weightings_community,
        'ind' : depts_weightings_individual
    }

    return depts_weightings


def get_cities_weightings(departure_cities_dict, method, mixed_criteria=True):
    
    # print(departure_cities_dict)
    nb_cities = sum([int(city['nb_people']) for city in departure_cities_dict])
    dep_cities_list = [(x['city'].pref_name, x['conveyance']) for x in departure_cities_dict]

    # Get raw values for major cities
    columns_list = ['departure', 'arrival', 'value']
    dep_cities_df = pd.DataFrame()
    for (dep_city, dep_conveyance) in dep_cities_list:
        db_method = dep_conveyance + '_' + method.replace('route_', '')
        dep_city_df = pd.DataFrame.from_records(
            Journey.objects.filter(departure=dep_city).values_list('departure', 'arrival', db_method), 
            columns=columns_list
        )
        dep_cities_df = dep_cities_df.append(dep_city_df)

    # Convert distance and duration in kms and hours
    if method.replace('route_', '') == 'distance':
        dep_cities_df['value'] = dep_cities_df['value'] / 1000
    elif method.replace('route_', '') == 'duration':
        dep_cities_df['value'] = dep_cities_df['value'] / 3600

    # Ponderate community city with nb of people
    dep_cities_com_df = dep_cities_df.copy()
    for dep_city in departure_cities_dict:
        city = dep_city['city'].name
        nb_people = dep_city['nb_people']
        dep_cities_com_df.loc[dep_cities_com_df['departure'] == city, 'value'] = dep_cities_com_df.loc[dep_cities_com_df['departure'] == city, 'value'] * nb_people

    # Generate dataframes on aggregating values
    com_df = pd.DataFrame(dep_cities_com_df.groupby('arrival').sum()['value'])
    com_df['value'] = com_df['value'] / nb_cities
    ind_df = pd.DataFrame(dep_cities_df.groupby('arrival').max()['value'])

    # Calculate mixed criteria
    if mixed_criteria:
        # mix_df = pd.DataFrame((com_df['value'] - com_df['value'].min()) / (com_df['value'].max() - com_df['value'].min())) 
        # mix_df = mix_df.append(pd.DataFrame((ind_df['value'] - ind_df['value'].min()) / (ind_df['value'].max() - ind_df['value'].min())))
        # mix_df = pd.DataFrame(mix_df.groupby('arrival').sum()['value'])
        # mix_df['value'] = mix_df['value'] - mix_df['value'].min() + 1

        # calculation modified after train_duration addition (big values for city wo station failed the values)
        mix_df = pd.DataFrame(com_df['value'] / com_df['value'].min())
        mix_df = mix_df.append(pd.DataFrame(ind_df['value'] / ind_df['value'].min()))
        mix_df = pd.DataFrame(mix_df.groupby('arrival').sum()['value'])
        mix_df['value'] = mix_df['value'] - mix_df['value'].min() + 1

    # Sort values
    com_df = com_df.rename(columns={"value": "value_com"})
    ind_df = ind_df.rename(columns={"value": "value_ind"})
    mix_df = mix_df.rename(columns={"value": "value_mix"})
    results_df = pd.merge(com_df, ind_df, left_on='arrival', right_on='arrival')
    results_df = pd.merge(results_df, mix_df, left_on='arrival', right_on='arrival')
    com_df = results_df.sort_values('value_com')
    ind_df = results_df.sort_values('value_ind')
    mix_df = results_df.sort_values('value_mix')


    # Get polygons and left join on dataframes
    arr_cities_df = pd.DataFrame.from_records(
        City.objects.filter(Q(is_pref=True) | Q(is_sous_pref=True)).values_list('name', 'polygon'), 
        columns=['name', 'polygon']
    )

    com_df = pd.merge(com_df, arr_cities_df, left_on='arrival', right_on='name')
    ind_df = pd.merge(ind_df, arr_cities_df, left_on='arrival', right_on='name')
    mix_df = pd.merge(mix_df, arr_cities_df, left_on='arrival', right_on='name')

    # Return dataframes as dictionnary
    df_dict = {
        'com': com_df,
        'ind': ind_df,
        'mix': mix_df
    }

    return df_dict


def calculate_mixed_criteria(entities, weightings):
    entities_weightings = {}
    std_wgs = {}

    for criteria in entities:
        entities_weightings[criteria] = zip(entities[criteria], weightings[criteria])
        entities_weightings[criteria] = sorted(entities_weightings[criteria], key=lambda weight: weight[0].name)
        std_wgs[criteria] = np.array([x[1] for x in entities_weightings[criteria]])
        std_wgs[criteria] = (std_wgs[criteria] - min(std_wgs[criteria])) / (max(std_wgs[criteria]) - min(std_wgs[criteria]))   
    
    entities_list = [x[0] for x in entities_weightings['com']]
    std_wgs['mix'] = np.array(std_wgs['com']) + np.array(std_wgs['ind'])
    std_wgs['mix'] = std_wgs['mix'] - min(std_wgs['mix']) + 1
    entities_weightings['mix'] = sorted(zip(entities_list, list(std_wgs['mix'])), key=lambda weight: weight[1])

    entities['mix'] = [x[0] for x in entities_weightings['mix']]
    weightings['mix'] = [x[1] for x in entities_weightings['mix']]

    return (entities, weightings)
