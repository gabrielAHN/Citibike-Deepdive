import json
import os

from citibike_data import read_s3_file

PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets/')


def create_citibike_dock_map(new_datasets, file_type='s3'):
    new_data = new_map_data(new_datasets)

    if file_type == 'local':
        try:
            with open(f"{PROJECT_DIR}/dock_map.json", 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = None
    elif file_type == 's3':
        existing_data = read_s3_file('dock_map.json')

    if existing_data:
        new_data = combine_datasets(new_data, existing_data)

    return new_data


def combine_datasets(new_data, existing_data):
    combined_dataset = []

    new_docks = [
        new_dock
        for new_dock in new_data
        if new_dock['station_name'] not in [
            current_dock['station_name']
            for current_dock in existing_data
        ]
    ]
    existing_docks = {
        new_dock['station_name']: new_dock
        for new_dock in new_data
        if new_dock['station_name'] in [
            current_dock['station_name']
            for current_dock in existing_data
        ]
    }

    if new_docks:
        combined_dataset.extend(new_docks)

    if existing_docks:
        for dock in existing_data:
            if dock['station_name'] in existing_docks.keys():
                dock['date_data'].update(
                    existing_docks[dock['station_name']]['date_data'])
            combined_dataset.append(dock)

    return combined_dataset


def adding_by_year(year, dock, existing_data, new_data):
    existing_year = existing_data[dock]['year']
    if not new_data.get(dock):
        return existing_year
    existing_year.update(new_data[dock]['year'])
    return existing_year


def making_total_count(year, existing_data, new_data):
    new_data_year = new_data.get(year)
    if not new_data_year:
        return existing_data[year]['total_count']
    exist_total = existing_data[year]['total_count']
    new_total = new_data[year]['total_count']
    return exist_total + new_total


def adding_by_month(year, dock, existing_data, new_data):
    existing_months = existing_data[dock]['year'][year]['months']
    if not new_data.get(dock):
        return existing_months
    if not new_data[dock]['year'].get(year):
        return existing_months
    existing_months.update(new_data[dock]['year'][year]['months'])
    return existing_months


def new_map_data(new_datasets):
    new_dock_data = []

    dock_ids = {
        dock.start_station_name: {
            'station_name': dock.start_station_name,
            'lat': dock.start_station_latitude,
            'lon': dock.start_station_longitude,
        }
        for datasets in new_datasets
        for dock in datasets['data']
    }

    for dock in dock_ids:

        dock_data = {}

        dock_data['station_name'] = dock
        dock_data['latitude'] = dock_ids[dock]['lat']
        dock_data['longitude'] = dock_ids[dock]['lon']
        dock_data['station_name'] = dock_ids[dock]['station_name']

        dock_data['date_data'] = {
            f"{datasets['month']}/{datasets['year']}":
                {
                    'start': len(
                        [
                            row
                            for row in datasets['data']
                            if row.start_station_name == dock
                        ]),
                    'end': len(
                        [
                            row
                            for row in datasets['data']
                            if row.end_station_name == dock
                        ])
                }
            for datasets in new_datasets
        }
        new_dock_data.append(dock_data)
    return new_dock_data
