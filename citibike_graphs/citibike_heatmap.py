import json
import datetime

from os.path import dirname, abspath
from citibike_data import read_s3_file

PROJECT_DIR = dirname(dirname(abspath(__file__)))


def create_citibike_heat_map_data(new_datasets, file_type='s3'):
    new_data = citibike_heat_map_data(new_datasets)

    if file_type == 'local':
        try:
            with open(f"{PROJECT_DIR}/datasets/heat_graph.json", 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = None
    elif file_type == 's3':
        existing_data = read_s3_file('heat_graph.json')

    if existing_data:
        new_data = update_data(new_data, existing_data)

    return new_data


def convert_month(month_num):
    date = datetime.datetime(2000, month_num, 1)
    short_month_name = date.strftime('%b')
    return short_month_name


def update_data(new_data, existing_data):
    heat_data = {}

    new_years = [
        year
        for year in list(new_data.keys())
        if year not in list(existing_data.keys())
    ]
    if new_years:
        for year in new_years:
            heat_data[year] = new_data[year]

    for year in existing_data:
        if new_data.get(str(year)):
            new_data_fields = new_data[year]
            existing_data_fields = existing_data[year]

            max_value = existing_data_fields['max_value']
            hours = existing_data_fields['hours']
            months = existing_data_fields['months'] + \
                new_data_fields['months']
            value = existing_data_fields['value'] + \
                new_data_fields['value']

            if max_value < new_data_fields['max_value']:
                max_value = new_data_fields['max_value']

            heat_data[year] = {
                "max_value": max_value,
                "months": months,
                "hours": hours,
                "value": value
            }
        else:
            heat_data[year] = existing_data[year]
    return heat_data


def sum_trip_data(new_datasets, year, month, hour):

    if hour == 1:
        return sum(
            [
                len(
                    dataset['data_df'][
                        (dataset['data_df']['starttime'].dt.month == month) &
                        (dataset['data_df']['starttime'].dt.hour <= hour)
                    ].index
                )
                for dataset in new_datasets
                if dataset['year'] == year
            ]
        )
    elif hour == 23:
        return sum(
            [
                len(
                    dataset['data_df'][
                        (dataset['data_df']['starttime'].dt.month == month) &
                        (dataset['data_df']['starttime'].dt.hour >= hour)
                    ].index
                )
                for dataset in new_datasets
                if dataset['year'] == year
            ]
        )
    else:
        return sum(
            [
                len(
                    dataset['data_df'][
                        (dataset['data_df']['starttime'].dt.month == month) &
                        (dataset['data_df']['starttime'].dt.hour == hour)
                    ].index
                )
                for dataset in new_datasets
                if dataset['year'] == year
            ]
        )


def citibike_heat_map_data(new_datasets):
    years = set([
        df['year']
        for df in new_datasets
    ])
    heat_data = {}

    for year in years:
        hours = list(range(1, 24))
        months = list(range(1, 13))

        values = [
            [
                month - 1,
                hour - 1,
                sum_trip_data(new_datasets, year, month, hour)
            ]
            for hour in hours
            for month in months
            if sum_trip_data(new_datasets, year, month, hour) != 0
        ]

        months = [
            convert_month(month)
            for month in months
            if month in [
                value[0] + 1
                for value in values
                if value[2] != 0
            ]
        ]
        max_value = max(
            [
                value[2]
                for value in values
            ]
        )
        heat_data[str(year)] = {
            "max_value": max_value,
            "months": months,
            "hours": hours,
            "value": values
        }
    return heat_data
