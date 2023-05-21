import csv
import json
import pandas as pd
import json
import boto3
import requests
import io


from io import BytesIO
from zipfile import ZipFile


AWS_URL = 'https://ghn-public-data.s3.amazonaws.com/citibike-data/{}'
CITIBIKE_FILE = 'https://s3.amazonaws.com/tripdata/{}'


clean_dict = {
    'member_casual': 'usertype',
    'user_type': 'usertype',
    'started_at': 'starttime',
    'ended_at': 'endtime',
    'start_time': 'starttime',
    'start_lng': 'start_station_latitude',
    'start_lat': 'start_station_longitude',
    'end_lat': 'end_station_latitude',
    'end_lng': 'end_station_longitude',
    'started_at': 'starttime',
    'rideable_type': 'rideable_type'
}

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

def standardize_df(df):
    column_lowered = {
        column: clean_dict.get(
            column.replace(' ', '_').lower(),
            column.replace(' ', '_').lower()
        )
        for column in list(df.columns)
    }

    df.rename(columns = column_lowered, inplace=True)
    df['starttime'] = pd.to_datetime(df['starttime'])
    return df


def standardize_columns(columns):
    column_lowered = [
        clean_dict.get(
            column.replace(' ', '_').lower(),
            column.replace(' ', '_').lower()
        )
        for column in columns
    ]
    return column_lowered


def import_to_s3(file, data, bucket='ghn-public-data'):
    s3 = boto3.resource('s3')
    s3object = s3.Object(bucket, file)
    s3object.put(
        Body=data
    )


def read_s3_file(file):
    file_path = AWS_URL.format(file)
    response = requests.get(file_path, timeout=10)
    if 200 == response.status_code:
        return json.loads(response.text)


def get_new_datasets(new_dates):
    new_datasets = []

    for new_date in new_dates:
        file_name = list(new_date.keys())[0]

        r = requests.get(CITIBIKE_FILE.format(file_name), timeout=10)
        files = ZipFile(BytesIO(r.content))

        csvfile_df = io.TextIOWrapper(files.open(file_name[:-4]), encoding='utf-8')
        csvfile_text = io.TextIOWrapper(files.open(file_name[:-4]), encoding='utf-8')

        df = pd.read_csv(csvfile_df, low_memory=False)
        data_df = standardize_df(df)

        csv_reader = csv.reader(csvfile_text)
        cleaned_columns = standardize_columns(next(csv_reader))
        
        data_row = [
        ClassCitibikeObject(
            start_station_id=get_index(row, cleaned_columns, 'start_station_id'),
            start_station_name=get_index(row, cleaned_columns, 'start_station_name'),
            start_station_latitude=get_index(row, cleaned_columns, 'start_station_latitude'),
            start_station_longitude=get_index(row, cleaned_columns, 'start_station_longitude'),
            starttime=get_index(row, cleaned_columns, 'starttime'),
            end_station_id=get_index(row, cleaned_columns, 'end_station_id'),
            end_station_name=get_index(row, cleaned_columns, 'end_station_name'),
            end_station_latitude=get_index(row, cleaned_columns, 'end_station_latitude'),
            end_station_longitude=get_index(row, cleaned_columns, 'end_station_longitude'),
            usertype=get_index(row, cleaned_columns, 'usertype')
        )
        for row in csv_reader
        if get_index(row, cleaned_columns, 'end_station_latitude')
        ]
        new_data = {
            'month': int(new_date[file_name][4:]),
            'year': int(new_date[file_name][:4]),
            'data': data_row,
            'data_df': data_df,
        }
        new_datasets.append(new_data)
    
    return new_datasets

def get_index(row, cleaned_columns, column_name):
    column_index = [
        index
        for index, column in enumerate(cleaned_columns)
        if column == column_name
    ][0]
    row = row[column_index]
    if row:
        return row
