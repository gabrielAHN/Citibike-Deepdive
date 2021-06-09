import csv
import os
import json

from io import TextIOWrapper
from zipfile import ZipFile

datasets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/')


def format_data(column):
    column = column.lower()
    column = column.replace(' ', '_')
    column = column.replace('usertype', 'user_type')
    column = column.replace('start_time', 'starttime')
    return column


def get_new_data(file, file_path):
    unzipped_file = file.replace('.zip', '')

    with ZipFile('{}{}'.format(file_path, file)) as zf:
        with zf.open(unzipped_file, 'r') as infile:
            reader = csv.reader(TextIOWrapper(infile, 'utf-8'))
            header = next(reader)
            new_data = [
                {
                    format_data(header[idx]):column 
                    for idx, column in enumerate(row)
                }
                for row in reader
            ]
    return new_data


def create_json_file(data, path, file_name):
    with open("{}/{}".format(path, file_name), 'w+') as f:
        json.dump(data, f, indent=4)


def citibike_dates(path):
    file = "{}file_dates.json".format(path)
    with open(file) as f:
      data = json.load(f)
    return data


def get_citibike_map_data():
    file = "{}citibike_data_map.json".format(datasets_path)
    try:
        with open(file) as f:
            data = json.load(f)
            return data
    except IOError:
        return None


def get_citibike_heatmap_data():
    file = "{}citibike_data_heatmap.json".format(datasets_path)
    try:
        with open(file) as f:
            data = json.load(f)
            return data
    except IOError:
        return None


def get_citibike_date():
    file = "{}file_dates.json".format(datasets_path)
    try:
        with open(file) as f:
            data = json.load(f)
            return data
    except IOError:
        return None

def get_citibike_line_graph():
    file = "{}citibike_line_graph.json".format(datasets_path)
    try:
        with open(file) as f:
            data = json.load(f)
            return data
    except IOError:
        return None
