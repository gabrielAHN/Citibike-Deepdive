import json
import re
from datetime import datetime

from citibike_data import get_citibike_heatmap_data

months = list(range(1, 13))
hours = list(range(1, 25))


def get_date_object(date):
    date = date['starttime']
    date = re.sub('\..+', '', date)
    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    return date


def count_hours_by_month(date_list, year, month, hour):
    count = len([
                trip
                for trip in date_list
                if int(year) == trip.year
                and month == trip.month
                and hour == trip.hour
            ])
    return count


def create_citibike_heat_map_data(data, path, dates):
    new_data = citibike_heat_map_data(data, dates)
    existing_data = get_citibike_heatmap_data()
    if existing_data:
        if dates['year'] not in list(existing_data.keys()):
            existing_data[dates['year']] = new_data[dates['year']]
            new_data = existing_data
        else:
            existing_months = existing_data[dates['year']]
            new_months = new_data[dates['year']]
            existing_data[dates['year']] = existing_months + new_months
            new_data = existing_data

    new_file = "{}citibike_data_heatmap.json".format(path)
    with open(new_file, 'w+') as f:
        json.dump(new_data, f, indent=4)
    print('heat_map created')


def citibike_heat_map_data(data, dates):
    date_list = [
        get_date_object(date)
        for date in data
    ]
    json_data = {
        year: [
            {
                'month': month,
                'hour' : hour,
                'amount': count_hours_by_month(date_list, year, month, hour)
            }
            for month in months
            for hour in hours
            if count_hours_by_month(date_list, year, month, hour) > 0
        ]
        for year in [dates['year']]
    }
    return json_data
