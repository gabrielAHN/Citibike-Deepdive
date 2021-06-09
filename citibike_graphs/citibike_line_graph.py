import re
import json

from datetime import datetime
from citibike_data import get_citibike_line_graph

user_types = [
    'Subscriber',
    'Customer'
]


def get_date_object(date):
    date = date['starttime']
    date = re.sub('\..+', '', date)
    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    return date


def create_citibike_line_graph_data(data, path, dates):
    new_data = citibike_line_data(data, dates)
    existing_data = get_citibike_line_graph()
    if existing_data:
        new_data = existing_data + new_data

    new_file = "{}citibike_line_graph.json".format(path)
    with open(new_file, 'w+') as f:
        json.dump(new_data, f, indent=4)
    print('line_graph created')


def combine_datasets(data, new_data):
    for x in new_data:
        if x['year'] == data["year"] and \
        x['user_type'] == data["user_type"]:
            data["amount"] = int(x["amount"]) + int(data["amount"])
            return data
    return data


def user_type_count(dates, user_type, data):
    count = len([
                row
                for row in data
                if user_type == row['user_type']
                and int(dates['year']) == get_date_object(row).year
                and int(dates['month']) == get_date_object(row).month
            ])
    return count


def citibike_line_data(data, dates):
    user_data = [
        {
            'year' : '{}/{}'.format(dates['month'], dates['year']),
            'amount': user_type_count(dates, user_type, data),
            'usertype': user_type
        }
        for user_type in user_types
    ]
    return user_data
