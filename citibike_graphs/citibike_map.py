import json

from citibike_data import get_citibike_map_data


def create_citibike_map_data(data, path, dates):
    new_data = citibike_map_data(data, dates)
    existing_data = get_citibike_map_data()
    if existing_data:
        new_data = combine_datasets(new_data, existing_data, dates)

    new_file = "{}citibike_data_map.json".format(path)
    with open(new_file, 'w+') as f:
        json.dump(new_data, f, indent=4)
    print('citibike map data created')


def combine_datasets(new_data, existing_data, dates):
    new_docks = {
        dock: existing_data[dock]
        for dock in existing_data
        if dock not in list(new_data.keys())
    }
    if new_docks:
        existing_data.update(new_docks)
    if dates['year'] not in list(existing_data['3244']['year'].keys()):
        adding_new_month = {
            dock: {
                'station_name': existing_data[dock]['station_name'],
                "lat": existing_data[dock]['lat'],
                "lon": existing_data[dock]['lon'],
                "year": adding_by_year(dates['year'], dock, existing_data, new_data)
            }
            for dock in existing_data
        }
        return adding_new_month
    elif dates['month'] not in list(existing_data['3244']['year'][dates['year']]['months'].keys()):
        adding_new_month = {
            dock: {
                'station_name': existing_data[dock]['station_name'],
                "lat": existing_data[dock]['lat'],
                "lon": existing_data[dock]['lon'],
                "year": {
                    year: {
                    'total_count':  making_total_count(year, existing_data['3244']['year'], new_data['3244']['year']),
                    'months': adding_by_month(year, dock, existing_data, new_data)
                    }
                    for year in existing_data[dock]['year']
                }
            }
            for dock in existing_data
        }
        return adding_new_month
    return existing_data


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
    new_total  = new_data[year]['total_count']
    return exist_total + new_total


def adding_by_month(year, dock, existing_data, new_data):
    existing_months = existing_data[dock]['year'][year]['months']
    if not new_data.get(dock):
        return existing_months
    if not new_data[dock]['year'].get(year):
        return existing_months
    existing_months.update(new_data[dock]['year'][year]['months'])
    return existing_months


def citibike_map_data(data, dates):
    dock_ids = { 
        dock['start_station_id']: {
            'station_name': dock['start_station_name'],
            'lat': dock['start_station_latitude'],
            'lon': dock['start_station_longitude'],
        }
        for dock in data
    }

    for dock in dock_ids:
        start_dock_count = len([
            j
            for j in data
            if j['start_station_id'] == dock
        ])
        end_dock_count = len([
            j
            for j in data
            if j['end_station_id'] == dock
        ])
        dock_ids[dock]['year'] = {
            dates['year']: {
                'total_count': len(data),
                'months': {
                    dates['month']: {
                        "start_dock_count": start_dock_count,
                        "end_dock_count": end_dock_count
                    }
                }
            }
        }
    return dock_ids
