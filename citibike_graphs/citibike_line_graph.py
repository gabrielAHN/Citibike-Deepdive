import re
import json

from os.path import dirname, abspath
from datetime import datetime
from citibike_data import read_s3_file


PROJECT_DIR = dirname(dirname(abspath(__file__)))

user_types_dict = {
    'Subscriber': 'member',
    'Customer': 'casual'
}

user_types = [
    'Subscriber',
    'Customer'
]


def create_citibike_line_graph_data(new_datasets, file_type='s3'):
    new_data = citibike_line_data(new_datasets)

    if file_type == 'local':
        try:
            with open(f"{PROJECT_DIR}/datasets/line_graph.json", 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = None
    elif file_type == 's3':
        existing_data = read_s3_file('line_graph.json')
    existing_data = read_s3_file('line_graph.json')

    if existing_data:
        new_data = {
            field: existing_data[field] + new_data[field]
            for field in existing_data
        }
    return new_data    


def get_date_object(date):
    date = date['starttime']
    date = re.sub(r'\..+', '', date)
    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    return date


def combine_datasets(data, new_data):
    for x in new_data:
        if x['year'] == data["year"] and \
                x['user_type'] == data["user_type"]:
            data["amount"] = int(x["amount"]) + int(data["amount"])
            return data
    return data


def user_type_count(dates, user_type, data):
    if data[0]['user_type'] in ['member', 'casual']:
        user_type = user_types_dict.get(user_type)
    count = [
        row
        for row in data
        if user_type == row['user_type']
        and int(dates['year']) == get_date_object(row).year
        and int(dates['month']) == get_date_object(row).month
    ]
    return len(count)


def citibike_line_data(new_datasets):
    formated_data = {
        'month_year': [],
        'sub_amt': [],
        'user_amt': []
    }

    for date_file in new_datasets:
        formated_data['month_year'].append(
            f"{date_file['month']}/{date_file['year']}"
        )
        formated_data['sub_amt'].append(
            len(
                
                date_file['data_df'][
                    (
                        date_file['data_df']['usertype'].str.contains('Subscriber') |
                        date_file['data_df']['usertype'].str.contains(
                            'member')
                    )
                ].index
            )
        )
        formated_data['user_amt'].append(
            len(
                date_file['data_df'][
                    (
                        date_file['data_df']['usertype'].str.contains('Customer') |
                        date_file['data_df']['usertype'].str.contains(
                            'casual')
                    )
                ].index
            )
        )
    return formated_data
