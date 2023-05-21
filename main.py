import argparse
import os
import requests
import json

from datetime import date
from bs4 import BeautifulSoup
from citibike_data import read_s3_file, get_new_datasets, import_to_s3
from citibike_graphs.citibike_dock_map import create_citibike_dock_map
from citibike_graphs.citibike_heatmap import create_citibike_heat_map_data
from citibike_graphs.citibike_line_graph import create_citibike_line_graph_data
from citibike_graphs.citibike_trips_map import create_citibike_trips_map_data


PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets/')


class ClassCitibikeObject:

    def __init__(self, start_station_id, start_station_name, start_station_latitude,
                 start_station_longitude, starttime, end_station_id, end_station_name,
                 end_station_latitude, end_station_longitude, usertype
                 ):
        self.start_station_id = start_station_id
        self.start_station_name = start_station_name
        self.start_station_latitude, = float(start_station_latitude),
        self.start_station_longitude = float(start_station_longitude)
        self.starttime = starttime
        self.end_station_id = end_station_id
        self.end_station_name = end_station_name
        self.end_station_latitude = float(end_station_latitude)
        self.end_station_longitude = float(end_station_longitude)
        self.usertype = usertype


def create_date_data(new_files, file_type='s3'):
    date_data = [
        {
            "year": list(date.values())[0][:4],
            "day": list(date.values())[0][4:]
        }
        for date in new_files
    ]
    if file_type == 'local':
        try:
            with open(f"{PROJECT_DIR}/date_data.json", 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = None
    elif file_type == 's3':
        existing_data = read_s3_file('date_data.json')

    if existing_data:
        date_data = existing_data + date_data

    return date_data


def check_for_new_data(now, file_type='s3'):
    response = requests.get('https://s3.amazonaws.com/tripdata/')
    soup = BeautifulSoup(response.content, 'xml')

    if file_type == 'local':
        try:
            with open(f"{PROJECT_DIR}/date_data.json", 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = None
    elif file_type == 's3':
        data = read_s3_file('date_data.json')

    if not data:
        data = []
    
    dates_of_new_files = [
        {
            date.text: date.text.split('-')[0]
        }
        for date in soup.findAll("Key")[44:]
        if 'JC-' not in date.text
        and 'index' not in date.text
        and date.text.split('-')[0] not in [
            f"{row['year']}{row['day']}"
            for row in data
        ]
    ]

    if dates_of_new_files:
        print(dates_of_new_files)
        return dates_of_new_files

def create_locally(datasets):
    for dataset in datasets:
        with open(f"{PROJECT_DIR}/{dataset}.json", 'w+') as file:
            json.dump(datasets[dataset], file, indent=2)
            print(f"Created {dataset}.json")

def create_in_s3(datasets):
    for dataset in datasets:
        json_data = json.dumps(datasets[dataset], indent=2)
        import_to_s3(f'citibike-data/{dataset}.json', json_data)
        print(f'{dataset}.json created')


def CitibikeMain():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs='?',
                        help='s3 or local')
    args = parser.parse_args()

    datasets = {}
    now = date.today()

    if args.command == 'local':
        new_dates = check_for_new_data(now, 'local')
        if new_dates:
            new_datasets = get_new_datasets(new_dates)
            datasets['trip_map_data'] = create_citibike_trips_map_data(new_datasets, 'local')
            datasets['dock_map'] = create_citibike_dock_map(new_datasets, 'local')
            datasets['heat_graph'] = create_citibike_heat_map_data(new_datasets, 'local')
            datasets['line_graph'] = create_citibike_line_graph_data(new_datasets, 'local')
            datasets['date_data'] = create_date_data(new_dates, 'local')
            create_locally(datasets)
            print(f'Finished creating data locally')
        else:
            print(f'No new files on {now}')
    if args.command == 's3':
        new_dates = check_for_new_data(now)
        if new_dates:
            new_datasets = get_new_datasets(new_dates)
            datasets['trip_map_data'] = create_citibike_trips_map_data(new_datasets)
            datasets['dock_map'] = create_citibike_dock_map(new_datasets)
            datasets['heat_graph'] = create_citibike_heat_map_data(new_datasets)
            datasets['line_graph'] = create_citibike_line_graph_data(new_datasets)
            datasets['date_data'] = create_date_data(new_dates)
            create_in_s3(datasets)
            print(f'Finished creating data for s3')
        else:
            print(f'No new files on {now}')
    else:
        print(f'Please enter s3 or local as an argument')

if __name__ == "__main__":
    CitibikeMain()
