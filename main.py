#!/usr/bin/env python
"""
    GOES Timelapse Generator
    Maintained At: https://github.com/Temporal-Driver/goes-timelapse-generator
    This script downloads and assembles satellite data from NOAA's CDN.
"""

import argparse
import math
import os
from datetime import datetime, timedelta

from modules import image_handling
from modules import command_parser

image_path = os.getcwd() + '/images'
ssl = True  # I wouldn't change this unless you know what you're doing


def main():
    if not os.path.exists(image_path):
        os.makedirs(image_path)
    args.band = 'geocolor'
    start = datetime.strptime(args.start, '%d-%b-%Y %H:%M')
    end = datetime.strptime(args.end, '%d-%b-%Y %H:%M')
    filename = generate_file_name(start, end)
    url = build_url(args.sat, args.region, args.band)
    resolution = command_parser.sizes[args.size][0] if args.region == 'disk' else command_parser.sizes[args.size][1]
    file_codes = generate_file_codes(start, end, args.region)
    results = image_handling.list_images(file_codes, resolution, url, ssl)
    image_handling.download_images(results, image_path, ssl)
    image_handling.generate_gif(file_codes, filename, resolution, image_path)
    quit()


def generate_file_name(d1, d2):
    date_string_1 = datetime.strftime(d1, '%d-%b-%Y %H%M')
    date_string_2 = datetime.strftime(d2, '%d-%b-%Y %H%M')
    filename = date_string_1 + ' - ' + date_string_2 + '.gif'
    if os.path.isfile(os.getcwd() + '/' + filename):
        name_taken = True
        attempt = 1
        while name_taken:
            new_filename = filename.split('.')[0] + ' (' + str(attempt) + ').gif'
            if os.path.isfile(os.getcwd() + '/' + new_filename):
                attempt += 1
            else:
                return new_filename
    else:
        return filename


def generate_file_codes(d1, d2, region):
    def round_to_closest(n):
        values = []
        if region == 'disk':
            values = [0, 10, 20, 30, 40, 50]
        elif region == 'conus':
            values = [6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]
        closest = min(values, key=lambda x: abs(x - n))
        return closest

    times = [d1.minute, d2.minute]
    for time in times:
        rounded = round_to_closest(time)
        times[times.index(time)] = rounded
    d1 = d1.replace(minute=times[0])
    d2 = d2.replace(minute=times[1])
    file_code_list = []
    current_code = d1.strftime('%Y%j%H%M')
    current_time = datetime.strptime(current_code, '%Y%j%H%M')
    file_code_list.append(current_code)
    while True:
        min_to_add = 10 if region == 'disk' else 5
        added_time = current_time + timedelta(minutes=min_to_add)
        file_code_list.append(datetime.strftime(added_time, '%Y%j%H%M'))
        if added_time == d2:
            return file_code_list
        else:
            current_time = added_time


def build_url(sat, region, band):
    band_mapping = {
        'airmass': 'AirMass/',
        'daycloudphase': 'DayCloudPhase/',
        'dust': 'Dust/',
        'firetemperature': 'FireTemperature/',
        'geocolor': 'GEOCOLOR/',
        'sandwich': 'Sandwich/'
    }
    url = 'https://cdn.star.nesdis.noaa.gov/{sat}/{region}/{band}'.format(
        sat='GOES16/ABI' if sat == 'east' else 'GOES18/ABI',
        region='FD' if region == 'disk' else 'CONUS',
        band=band_mapping.get(band, '')
    )
    return url


# Takes a value in bytes and returns it as megabytes rounded to the nearest hundredth
def bytes_to_megabytes(bytes_value):
    megabytes = bytes_value / (1024 * 1024)
    megabytes_string = str(math.floor(megabytes * 100) / 100)
    return megabytes_string


if __name__ == '__main__':
    cmd_parser = argparse.ArgumentParser(description='GOES Timelapse Generator')
    command_parser.process_args(cmd_parser)
    args = cmd_parser.parse_args()
    main()
