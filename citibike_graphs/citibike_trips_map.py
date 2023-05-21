import pandas as pd
import requests
import json
import datetime
import geopy.distance

from os.path import dirname, abspath
from citibike_data import read_s3_file

PROJECT_DIR = dirname(dirname(abspath(__file__)))
url = 'https://api.mapbox.com/directions/v5/mapbox/cycling/{},{};{},{}'
api_key = 'MAPBOX_API_KEY'


class ClassTripObject:

    def __init__(self, start_station_name, start_station_latitude,
                 start_station_longitude, end_station_name,
                 end_station_latitude, end_station_longitude,
                 amount, trip_shape
                 ):
        self.start_station_name = start_station_name
        self.start_station_latitude = start_station_latitude
        self.start_station_longitude = start_station_longitude
        self.end_station_name = end_station_name
        self.end_station_latitude = end_station_latitude
        self.end_station_longitude = end_station_longitude
        self.amount = amount
        self.trip_shape = trip_shape


def create_citibike_trips_map_data(new_datasets, file_type='s3'):
    new_data = create_new_trip_data(new_datasets)

    if file_type == 'local':
        try:
            with open(f"{PROJECT_DIR}/datasets/trip_map.json", 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = None
    elif file_type == 's3':
        existing_data = read_s3_file('trip_map.json')

    if existing_data:
        new_data = new_combine_datasets(new_data, existing_data)

    return new_data


def fix_points(lat, lon):
    if lat > lon:
        return [lon, lat]
    else:
        return [lat, lon]


def get_trip_json(row):
    query_params = {
        "geometries": "geojson",
        "access_token": api_key
    }

    start_point = fix_points(row['start_station_longitude'], row['start_station_latitude'])
    end_point = fix_points(row['end_station_longitude'], row['end_station_latitude'])

    trip_url = url.format(start_point[0], start_point[1], end_point[0], end_point[1])

    response = requests.get(trip_url, params=query_params)
    
    if response.status_code == 200:
        data = response.json()
        data = data['routes'][0]['geometry']['coordinates']
        return data


def get_timestamp(time):
    time = datetime.datetime.timestamp(time)
    time = round(time, 2)
    return time


def get_top_trips(df):
    top_trips = df.groupby(
        [
            'start_station_name', 'start_station_latitude',
            'start_station_longitude', 'end_station_name',
            'end_station_latitude', 'end_station_longitude',
        ]).size().nlargest(10)
    
    filter_list = top_trips.reset_index().to_dict('records')
    trip_data = {
        f"{row['start_station_name']} to {row['end_station_name']}":
        ClassTripObject(
            start_station_name=row['start_station_name'],
            start_station_latitude=row['start_station_latitude'],
            start_station_longitude=row['start_station_longitude'],
            end_station_name=row['end_station_name'],
            end_station_latitude=row['end_station_latitude'],
            end_station_longitude=row['end_station_longitude'],
            amount=row[0],
            trip_shape=get_trip_json(row),
        )
        for row in filter_list
    }
    return trip_data


def get_distance(lat1, lon1, lat2, lon2):
    distance = geopy.distance.geodesic(
        (lat1, lon1),
        (lat2, lon2)
    ).km
    return distance


def divide_points(lat1, lon1, lat2, lon2, num_sections):
    points = []

    delta_longitude = lon2 - lon1
    delta_latitude = lat2 - lat1

    section_size_longitude = delta_longitude / (num_sections - 1)
    section_size_latitude = delta_latitude / (num_sections - 1)

    intermediate_points = [
        [
            lon1 + i * section_size_longitude,
            lat1 + i * section_size_latitude
        ]
        for i in range(0, num_sections - 1)]

    intermediate_points = [
        [
            round(i, 5), round(j, 5)
        ]
        for i, j in intermediate_points
    ]
    points.append([lon1, lat1])
    points.extend(intermediate_points)
    points.append([lon2, lat2])

    return points


def extend_shape(shape):
    extended_shape = []

    for i in range(len(shape) - 1):
        lon1, lat1 = shape[i]
        lon2, lat2 = shape[i+1]

        distance = get_distance(lon1, lat1, lon2, lat2)

        if 0.2 < distance < 0.37:
            between_points = divide_points(lat1, lon1, lat2, lon2, 2)
            extended_shape.extend(between_points)
        elif distance > 0.37:
            between_points = divide_points(lat1, lon1, lat2, lon2, 4)
            extended_shape.extend(between_points)
        else:
            extended_shape.append([lon1, lat1])

    extended_shape.append([lon2, lat2])

    extended_shape = [
        [
            round(y, 5)
            for y in i
        ]
        for i in extended_shape
    ]
    return extended_shape


def get_trip_times(trip, filter_list):

    shape = filter_list.get(f"{trip['start_station_name']} to {trip['end_station_name']}")

    if not shape:
        return shape

    shape = extend_shape(shape.trip_shape)
    start_time = trip['starttime']

    trip_times = [
        {
            "coordinates": [shape[0][0], shape[0][1]],
            "timestamp": get_timestamp(start_time)
        }
    ]

    for i in range(len(shape) - 1):
        lon1, lat1 = shape[i]
        lon2, lat2 = shape[i+1]

        point_time = datetime.timedelta(hours=1)
        start_time = start_time + point_time

        trip_times.append(
            {
                'timestamp': get_timestamp(start_time),
                'coordinates': [lon1, lat1],
            }
        )

    trip_times.append(
        {
            'timestamp': get_timestamp(start_time),
            'coordinates': [lon2, lat2],
        }
    )
    return trip_times


def get_trips(df, filter_list):

    if 'rideable_type' not in df.columns.tolist():
        df['rideable_type'] = 'classic_bike'

    filtered_trips = df[
        (df['start_station_name'].isin(
            [filter_list[x].start_station_name for x in filter_list]))
        & (df['end_station_name'].isin(
        [
            filter_list[x].end_station_name
            for x in filter_list
        ]))
    ][[
        'start_station_name', 'start_station_latitude',
        'start_station_longitude', 'end_station_name',
        'end_station_latitude', 'end_station_longitude',
        'starttime', 'rideable_type'
    ]]

    trips = filtered_trips.to_dict('records')

    trip_times = [
        {
            'trip_type': trip['rideable_type'],
            'top_trip_id': f"{trip['start_station_name']} to {trip['end_station_name']}",
            'waypoints':
                get_trip_times(trip, filter_list)
        }
        for trip in trips
        if get_trip_times(trip, filter_list)
    ]
    return trip_times


def create_new_trip_data(new_datasets):
    trip_data = {}

    years = set([
        df['year']
        for df in new_datasets
    ])

    for year in years:
        year_dataframe = pd.concat(
            [
                dataset['data_df']
                for dataset in new_datasets
                if dataset['year'] == year
            ]
        ).reset_index(drop=True)

        year_dataframe = year_dataframe[
            year_dataframe['start_station_name'] !=
            year_dataframe['end_station_name']
        ]
        top_trips = get_top_trips(year_dataframe)

        first_timestamp = year_dataframe['starttime'].min()
        last_timestamp = year_dataframe['starttime'].max()

        trip_times = get_trips(year_dataframe, top_trips)

        json_trips = {
            trip: vars(top_trips[trip])
            for trip in top_trips
        }

        trip_data[str(year)] = {
            "top_trips": json_trips,
            "start_time": int(first_timestamp.timestamp()),
            "end_time": int(last_timestamp.timestamp()),
            "trip_times": trip_times
        }
    return trip_data


def new_combine_datasets(new_data, existing_data):
    combined_dataset = {}

    new_data_years = set(new_data.keys())
    existing_data_years = set(existing_data.keys())

    new_years = [
        year
        for year in new_data_years
        if year not in existing_data_years
    ]

    add_data_years = [
        year
        for year in new_data_years
        if year in existing_data_years
    ]

    if new_years:
        for year in new_years:
            combined_dataset[year] = new_data[year]

    for year in add_data_years:
        existing_top_trips = existing_data[year]['top_trips']
        new_top_trips = new_data[year]['top_trips']

        existing_top_trips_keys = set(existing_top_trips.keys())
        new_top_trips_keys = set(new_top_trips.keys())

        similar_trips = new_top_trips_keys & existing_top_trips_keys
        new_trips = new_top_trips_keys - existing_top_trips_keys

        for similar_trip in similar_trips:
            existing_top_trips[similar_trip]['amount'] += new_top_trips[similar_trip]['amount']

        for new_trip in new_trips:
            existing_top_trips[new_trip] = new_top_trips[new_trip]

        top_trips = sorted(existing_top_trips.items(),
                           key=lambda x: x[1]['amount'], reverse=True)
        
        top_trips = dict(top_trips[:10])

        all_trip_times = existing_data[year]['trip_times'] + \
            new_data[year]['trip_times']

        trips_times = [
            trip
            for trip in all_trip_times
            if trip['top_trip_id'] in
            [
                trip
                for trip in top_trips
            ]
        ]

        combined_dataset[year] = {
            "top_trips": top_trips,
            "start_time": existing_data[year]['start_time'],
            "end_time": new_data[year]['end_time'],
            "trip_times": trips_times
        }
    return combined_dataset
