import datetime
import json
import os
import requests

from citibike_data import get_new_data, citibike_dates, create_json_file
from citibike_graphs.citibike_map import create_citibike_map_data
from citibike_graphs.citibike_heatmap import create_citibike_heat_map_data
from citibike_graphs.citibike_line_graph import create_citibike_line_graph_data

from datetime import datetime
from dateutil.relativedelta import relativedelta


now = datetime.now()

month = now.strftime('%m')
year = now.strftime('%Y')

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/')
zip_path = 'https://s3.amazonaws.com/tripdata/{}'
data_dates = citibike_dates(path)


def check_date(data_dates, new_month, new_year):
    if new_year in list(data_dates.keys()):
        data_dates[new_year].append(new_month)
    else:
        data_dates[new_year] = [new_month]
    create_json_file(data_dates, path, 'file_dates.json')


def check_for_new_data(count):
    file_date = datetime.now()
    file_date = datetime.today() + relativedelta(months=count)
    new_month = file_date.strftime('%m')
    new_year = file_date.strftime('%Y')
    check_dates = [
        [year, month]
        for year in data_dates
        for month in data_dates[year]
        if year == new_year
        and month == new_month
    ]
    if not check_dates:
        file_name = download_new_data(new_month, new_year)
        if not file_name:
            return None, None
        return file_name, {'month': new_month, 'year': new_year, 'exist_data': data_dates}
    return None, None


def download_new_data(month, year):
    file_name = '{}{}-citibike-tripdata.csv.zip'.format(year, month)
    if file_name in os.listdir(path):
        return None
    chunk_size = 200
    new_file = '{}/{}'.format(path, file_name)
    zip_request = requests.get(zip_path.format(file_name), stream=True)
    if 'The specified key does not exist' in str(zip_request.content):
        return None
    with open(new_file, 'wb') as fd:
        for chunk in zip_request.iter_content(chunk_size=chunk_size):
            fd.write(chunk)
    return file_name


def main():
    count = -2
    new_file, new_date = check_for_new_data(count)
    if new_file:
        new_data = get_new_data(new_file, path)
        create_citibike_map_data(new_data, path, new_date)
        create_citibike_heat_map_data(new_data, path, new_date)
        create_citibike_line_graph_data(new_data, path, new_date)
        os.remove("{}{}".format(path, new_file))
        check_date(
            new_date['exist_data'],
            new_date['month'],
            new_date['year']
        )


if __name__ == "__main__":
    main()
