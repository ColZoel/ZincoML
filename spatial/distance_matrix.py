"""
This is an updated version of distance.py for speed and comprehensiveness. Included are functions for Euclidean,
driving, and walking distances.
"""
import time
import os
import pandas as pd
import numpy as np
import requests
from geopy.distance import geodesic
from dotenv import load_dotenv
from geopy.extra.rate_limiter import RateLimiter
from Zs.Z_modules import time_update
import sys


print("            Zinco Distance Matrix            \n"
      "---------------------------------------------\n"
      " Version 2.1.0 | Author: Collin Zoeller | 2023-11-17\n"
      "---------------------------------------------\n")


session = requests.Session()

api_counter = 0
row_counter = 0
col_counter = 0
start = time.perf_counter()


def euclidean(coords, unit='mi'):
    """
    :param coords: a list of coordinates in the form of (longitude, latitude)
    :param unit: 'mi' for miles, 'km' for kilometers, 'ft' for feet
    :return: a distance matrix
    """

    coords = np.array(coords)
    coords = coords.reshape(-1, 1, 2)
    coords = np.repeat(coords, len(coords), axis=1)
    coords = coords - coords.transpose(1, 0, 2)
    coords = coords ** 2
    coords = coords.sum(axis=2)
    coords = np.sqrt(coords)

    if unit == 'mi':
        coords = coords * 69.172
    elif unit == 'km':
        coords = coords * 111.325
    elif unit == 'ft':
        coords = coords * 364000
    else:
        raise ValueError("unit must be 'mi', 'km', or 'ft'")

    return coords


def vectorize(func):
    return np.vectorize(func, excluded=['anchor'])


def map2list(func, anchor, coord_list):
    return list(map(lambda coord: func(anchor, coord), coord_list))


def listize(func):
    return lambda anchor, coord_list: map2list(func, anchor, coord_list)


@listize
def geodesic_feet(coord, anchor):
    return geodesic(anchor, coord).feet


@listize
def geodesic_mi(coord, anchor):
    return geodesic(anchor, coord).miles


@listize
def geodesic_km(coord, anchor):
    return geodesic(anchor, coord).kilometers


def geodesic_row(index, coord_list, unit):
    """
    :param index: the index of the anchor location
    :param coord_list: a list of coordinates in the form of (longitude, latitude)
    :param unit: 'mi' for miles, 'km' for kilometers, 'ft' for feet
    :return: a distance matrix
    """
    anchor = coord_list[index]
    if unit == 'mi':
        coords = geodesic_mi(anchor, coord_list)
    elif unit == 'km':
        coords = geodesic_km(anchor, coord_list)
    elif unit == 'ft':
        coords = geodesic_feet(anchor, coord_list)
    else:
        raise ValueError("unit must be 'mi', 'km', or 'ft'")

    return coords


def geodesic_matrix(coords, unit='mi'):
    """
    :param coords: a list of coordinates in the form of (longitude, latitude)
    :param unit: 'mi' for miles, 'km' for kilometers, 'ft' for feet
    :return: a distance matrix
    """
    indices = list(range(len(coords)))
    # coord_tups = [tuple(coord) for coord in coords]
    mat = np.array(list(map(lambda i: geodesic_row(i, coords, unit), indices)))
    return mat


def ratelimiter(func):
    return RateLimiter(func, min_delay_seconds=0.1)

# def short_step(start, step_str, i, total_steps):
#     timer = time_update(start)
#     sys.stdout.write('\r')
#     sys.stdout.write("%s | elapsed: %s | %d%%  %-20s" % (step_str, timer,
#                                                          (i / total_steps) * 100,
#                                                          '#' * int((i / total_steps) * 15)))
#     sys.stdout.flush()
#
#     return


def iter_counter(size):
    global api_counter
    global row_counter
    global col_counter
    global start
    timer = time_update(start)
    sys.stdout.write('\r')
    sys.stdout.write("row %d of %d | col %d | API calls: %d| elapsed: %s | %d%%  %-20s" %
                     (row_counter, size, col_counter,
                      api_counter, timer,
                      ((api_counter + size) / (size ** 2)) * 100,
                      '#' * int(((api_counter + size) / (size ** 2)) * 15)))

    return


@ratelimiter
def call(loc1, loc2, api_key, mode='driving'):
    """
    :param loc1: array-like of longitude, latitude for the origin locations
    :param loc2: array-like of longitude, latitude for the second locations
    :param mode: 'driving' or 'walking'
    :param api_key: your Google Maps API key
    :return: a distance in miles
    """
    global api_counter
    api_counter += 1
    endpoint = 'https://maps.googleapis.com/maps/api/distancematrix/json?'

    if mode != 'driving' and mode != 'walking':
        raise ValueError("mode must be 'driving' or 'walking'")

    origins = [str(loc) for loc in loc1]
    origins = '%2C'.join(origins)

    destinations = [str(loc) for loc in loc2]
    destinations = '%2C'.join(destinations)

    if origins == destinations:
        return [0, 0]

    url = f'{endpoint}destinations={destinations}&origins={origins}&mode={mode}&key={api_key}'
    response = session.get(url)
    return response


def google_call(loc1, loc2, api_key, mode='driving'):
    response = call(loc1, loc2, api_key, mode=mode)
    distance, duration = parse_response(response)
    global col_counter
    col_counter += 1
    return [distance, duration]


def call_row(index, coord_list, key, mode):
    """
    :param index: the index of the anchor location
    :param coord_list: a list of coordinates in the form of (longitude, latitude)
    :param key: your Google Maps API key
    :param mode: 'driving' or 'walking'
    :return: a distance matrix
    """
    global row_counter
    row_counter += 1
    iter_counter(len(coord_list))
    anchor = coord_list[index]
    distlist = list(map(lambda coord: google_call(anchor, coord, key, mode), coord_list))
    return distlist


def call_matrix(coords, key, mode, distance_unit='mi', time_unit='min'):
    """
    :param coords: a list of coordinates in the form of (longitude, latitude)
    :param key: your Google Maps API key
    :param mode: 'driving' or 'walking'
    :param distance_unit: 'mi' for miles, 'km' for kilometers, 'ft' for feet
    :param time_unit: 'min' for minutes, 'hr' for hours, 'sec' for seconds
    :return: a distance matrix
    """
    indices = list(range(len(coords)))
    mat = np.array(list(map(lambda i: call_row(i, coords, key, mode), indices)))

    dist = mat[:, :, 0]
    dur = mat[:, :, 1]

    dist = convert_distance(dist, distance_unit)
    dur = convert_duration(dur, unit=time_unit)
    return dist, dur


def convert_distance(dist, unit):
    if unit == 'mi':
        dist = dist * 1/1609.34
    elif unit == 'km':
        dist = dist * 0.001
    elif unit == 'ft':
        dist = dist * 3.28084
    else:
        raise ValueError("unit must be 'mi', 'km', or 'ft'")

    return dist


def convert_duration(dur, unit='min'):
    if unit == 'min':
        dur = dur * 1/60
    elif unit == 'hr':
        dur = dur * 1/3600
    elif unit == 'sec':
        pass
    else:
        raise ValueError("unit must be 'min', 'hr', or 'sec'")

    return dur


def parse_response(response):
    """
    For single one-way calls A->B. The best return for distance and duration are retained (meter and seconds).
    :param response: a response from the Google Maps API
    :return: a dictionary of the response
    """

    if type(response) is list:
        distance = response[0]
        duration = response[1]
        return distance, duration

    if response.status_code != 200:
        print(f'Error {response.status_code}')

        distance = np.nan
        duration = np.nan

        return distance, duration

    response = response.json()
    call_status = response['status']
    return_status = response['rows'][0]['elements'][0]['status']

    if call_status != 'OK' or return_status != 'OK':
        item = call_status if call_status != 'OK' else return_status
        print(f'Error {item} at query')
        distance = np.nan
        duration = np.nan
        return distance, duration

    best_return = response['rows'][0]['elements']
    distance = best_return[0]['distance']['value']  # distance is in meters
    duration = best_return[0]['duration']['value']  # duration is in seconds

    return distance, duration


def mat_to_pandas(dist, dur, origin_address, destination_address):
    """
    :param dist: distance matrix
    :param dur: duration matrix
    :param origin_address: list of origin addresses
    :param destination_address: list of destination addresses
    :return: pandas dataframe
    """
    if dur is not None:
        durmat = pd.DataFrame(dur, index=origin_address)
        durmat.columns = destination_address
    else:
        durmat = None

    distmat = pd.DataFrame(dist, index=origin_address)
    distmat.columns = destination_address

    return distmat, durmat


def save_out(distmat, durmat, mode, type='both', format='csv', save_dir=None, time='min', unit='mi'):
    if format != 'csv' and format != 'excel' and format != 'stata' and format is not None:
        raise ValueError("save_type must be 'csv', 'excel', or 'stata'. None only saves Feather.")
    if type != 'both' and type != 'distance' and type != 'duration':
        raise ValueError("type must be 'both', 'distance', or 'duration'")

    if save_dir is None:
        save_dir = os.getcwd()
    filename_dist = f'distance_matrix_{mode}_{unit}'
    filename_dur = f'duration_matrix_{mode}_{time}'

    if format == 'csv':
        if type == 'both' or type == 'distance':
            distmat.to_csv(os.path.join(save_dir, f'{filename_dist}.csv'))
        if type == 'both' or type == 'duration' and durmat is not None:
            durmat.to_csv(os.path.join(save_dir, f'{filename_dur}.csv'))

    elif format == 'excel':
        if type == 'both' or type == 'distance':
            distmat.to_excel(os.path.join(save_dir, f'{filename_dist}.xlsx'))
        if type == 'both' or type == 'duration' and durmat is not None:
            durmat.to_excel(os.path.join(save_dir, f'{filename_dur}.xlsx'))

    elif format == 'stata':
        if type == 'both' or type == 'distance':
            distmat.to_stata(os.path.join(save_dir, f'{filename_dist}.dta'))
        if (type == 'both' or type == 'duration') and durmat is not None:
            durmat.to_stata(os.path.join(save_dir, f'{filename_dur}.dta'))

    distmat.to_feather(os.path.join(save_dir, f'{filename_dist}.feather'))
    if durmat is not None:
        durmat.to_feather(os.path.join(save_dir, f'{filename_dur}.feather'))
    else:
        print('------>> No duration matrix to save. Set mode to "walking" or "driving" to save a duration matrix.')
    return


def read_any(data):
    if data is str:
        if data.endswith('.csv'):
            data = pd.read_csv(data)
        elif data.endswith('.xlsx'):
            data = pd.read_excel(data)
        elif data.endswith('.dta'):
            data = pd.read_stata(data)
        elif data.endswith('.feather'):
            data = pd.read_feather(data)
        else:
            raise ValueError("data must be a pandas dataframe or a path to a csv, xlsx, dta, or feather file")
    elif isinstance(data, pd.DataFrame):
        pass
    else:
        raise ValueError("data must be a pandas dataframe or a path to a csv, xlsx, dta, or feather file")
    return data


def validate_columns(data):
    if 'lat' in data.columns:
        data.rename(columns={'lat': 'latitude'}, inplace=True)
    if 'long' in data.columns:
        data.rename(columns={'long': 'longitude'}, inplace=True)

    if ('longitude' not in data.columns or 'latitude' not in data.columns) and 'coordinates' not in data.columns:
        raise KeyError("data must have columns 'longitude' and 'latitude' or column of 'coordinates'")
    if 'name' not in data.columns:
        raise KeyError("data must have a column 'name' with the name of the entity")
    return


def sample(df, n):
    if n > len(df):
        raise ValueError(f'cannot sample {n} rows from a dataframe with {len(df)} rows')
    df = df.sample(n)
    return df


def matrix(data, api_key,
           mode='driving',
           unit='mi',
           time='min',
           save_format='stata',
           save_which='both',
           save_dir=None,
           sample_n=None):
    """
    :param data: a pandas dataframe with columns 'longitude' and 'latitude' or 'coordinates'
    :param mode: 'driving', 'walking', 'euclidean', or 'geodesic'
    :param api_key: your Google Maps API key
    :param unit: 'mi' for miles, 'km' for kilometers, 'ft' for feet (default miles)
    :param time: 'min' for minutes, 'hr' for hours, 'sec' for seconds (default minutes)
    :param save_format: 'csv', 'excel', 'stata', or 'feather'
    :param save_which: 'both', 'distance', or 'duration'
    :param save_dir: directory to save the output
    :param sample_n: number of rows to sample for low-cost debugging
    :return: distance and duration matrices
    """
    data = read_any(data)
    validate_columns(data)
    data = sample(data, sample_n) if sample_n is not None else data
    if 'coordinates' in data.columns:
        coords = data['coordinates'].values.tolist()
    else:
        coords = data[['latitude', 'longitude']].values.tolist()

    if mode == 'driving' or mode == 'walking':
        print(f'{mode} in terms of {unit} and {time}\n\n')
        dist, dur = call_matrix(coords, api_key, mode=mode, distance_unit=unit, time_unit=time)
        distmat, durmat = mat_to_pandas(dist, dur, data['name'], data['name'])

    elif mode == 'euclidean':
        print(f'euclidean in terms of {unit}. Symmetric linear distance. No time matrix to be saved.\n\n')
        distmat = euclidean(coords, unit=unit)
        durmat = None

    elif mode == 'geodesic':
        print(f'geodesic in terms of {unit}. Asymmetric linear distance. No time matrix to be saved.\n\n')
        coords = list(map(tuple, coords))
        distmat = geodesic_matrix(coords, unit=unit)
        durmat = None

    else:
        raise ValueError("mode must be 'driving', 'walking', 'euclidean', or 'geodesic'")

    distmat, durmat = mat_to_pandas(distmat, durmat, data['name'], data['name'])
    save_out(distmat, durmat, mode, type=save_which, format=save_format, save_dir=save_dir, unit=unit, time=time)

    return
