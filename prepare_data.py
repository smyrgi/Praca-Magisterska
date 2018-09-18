#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
from astropy.time import Time
import output_grouped_data


def main():
	file_name = 'alldataDPD'
	input_file_name = file_name + '.txt'
	output_file_name_clear = file_name + '_clear.txt'
	output_file_name_grouped = 'groupdata_modified.txt'
	output_file_name_longitude = 'groupdata_longitudelimit.txt'
	output_file_name_latitude = 'groupdata_latitudelimit.txt'
	output_file_name_inlimit = 'groupdata_modified_inlimit.txt'
	latitude_limit = 10
	longitude_limit = 30
	
	columns_names = ['DataType','YYYY','MM','DD','HH','mm','ss','NOAA','UmbraArea','WholeSpotArea', 'CorrectedUmbraArea',
					 'CorrectedWholeSpotArea', 'Latitude','Longitude', 'LongitudinalDistance','PositionAngle','DistanceFromCentre']
	columns_positions = [(0, 1), (2, 6), (7, 9), (10, 12), (13, 15), (16, 18), (19, 21), (22, 28), (35, 40), (41, 46), (47, 52), (53, 58), (59, 65), (66, 72), (73, 79), (80, 86), (87, 93)]
	sunspot_data = pd.read_fwf(input_file_name, header=None, names=columns_names, colspecs=columns_positions)
	sunspot_data = validate_input(sunspot_data)	
	sunspot_data = add_data(sunspot_data)
	columns_names_extended = ['DataType', 'YYYY', 'MM', 'DD', 'HH', 'mm', 'ss', 'NOAA', 'UmbraArea', 'WholeSpotArea', 'CorrectedUmbraArea', 
						   'CorrectedWholeSpotArea', 'Latitude', 'Longitude', 'LongitudinalDistance', 'PositionAngle', 'DistanceFromCentre', 
						   'JulianDay', 'Longitude*Area', 'Latitude*Area', 'PositionOnDisk', 'CarringtonRotation']
	sunspot_data.to_csv( output_file_name_clear, sep='	', header = columns_names_extended, index = None )
	
	sunspot_data_final, final_columns_names = output_grouped_data.output_data(sunspot_data, output_file_name_grouped)
	
	sunspot_data_longitude_range = get_not_in_limit(sunspot_data_final, column_name = 'LongitudeRange', limit = longitude_limit)
	sunspot_data_latitude_range = get_not_in_limit(sunspot_data_final, column_name = 'LatitudeRange', limit = latitude_limit)
	sunspot_data_in_limit = get_in_limit(sunspot_data_final, column_names = ['LongitudeRange', 'LatitudeRange'], limits = [longitude_limit,latitude_limit])
	
	sunspot_data_longitude_range.to_csv( output_file_name_longitude, sep='	', header = final_columns_names, index = None )
	sunspot_data_latitude_range.to_csv( output_file_name_latitude, sep='	', header = final_columns_names, index = None )
	sunspot_data_in_limit.to_csv( output_file_name_inlimit, sep='	', header = final_columns_names, index = None )
	

def validate_input(sunspot_data):
	corrected_sunspot_data = remove_invalid(sunspot_data)
	corrected_sunspot_data = correct_seconds(corrected_sunspot_data)
	corrected_sunspot_data = correct_longitudinal_distance(corrected_sunspot_data)
	return corrected_sunspot_data
	
	
def remove_invalid(sunspot_data):
	columns_to_validate = ['Latitude','Longitude','LongitudinalDistance','PositionAngle','DistanceFromCentre']
	invalid_data = 999999
	valid_sunspot_data = sunspot_data[(sunspot_data[columns_to_validate] != invalid_data).all(axis=1)]
	corrected_sunspot_data = valid_sunspot_data.reset_index(drop=True)
	return corrected_sunspot_data
	
	
def correct_seconds(sunspot_data):
	sunspot_data.loc[sunspot_data['ss'] == 60, 'mm'] += 1
	sunspot_data.loc[sunspot_data['ss'] == 60, 'ss'] = 0
	return sunspot_data
	
def correct_longitudinal_distance(sunspot_data):
	sunspot_data.loc[sunspot_data['LongitudinalDistance'] < -90, 'LongitudinalDistance'] = -90
	sunspot_data.loc[sunspot_data['LongitudinalDistance'] > 90, 'LongitudinalDistance'] = 90
	return sunspot_data
	
	
def add_data(sunspot_data):
	sunspot_data['JulianDay'] = sunspot_data.apply(get_julian_day, axis=1)
	sunspot_data['Longitude*Area'] = sunspot_data['Longitude'] * sunspot_data['CorrectedWholeSpotArea']
	sunspot_data['Latitude*Area'] = sunspot_data['Latitude'] * sunspot_data['CorrectedWholeSpotArea']
	sunspot_data['PositionOnDisk'] = ( sunspot_data['LongitudinalDistance'] + 90 ) / 180
	sunspot_data['CarringtonRotation'] = get_carrington_rotations(sunspot_data)
	return sunspot_data
	
	
def get_julian_day(date):
	year = date['YYYY']
	month = date['MM']
	day = date['DD']
	hour = date['HH']
	minute = date['mm']
	second = date['ss']
	time = Time(datetime(year, month, day, hour, minute, second), scale='utc')
	return time.jd


def get_carrington_rotations(sunspot_data):
	rotations_numbers = []
	sunspot_data_records = sunspot_data.shape[0]
	
	rotations_starts = get_starts()
	
	for record in range(sunspot_data_records):
		current_julian_day = sunspot_data.at[record,'JulianDay']
		current_rotation_number = get_current( current_julian_day, rotations_starts )
		rotations_numbers.append(current_rotation_number)

	return rotations_numbers


def get_starts():
	rotations_start_days = []
	rotations_numbers = []
	julian_days = []
	
	with open('carrington.txt','r') as input_file:
		for line in input_file:
			rotation_number, julian_day = line.split('\t')
			rotations_numbers.append(int(rotation_number))
			julian_days.append(float(julian_day))
	
	return [rotations_numbers, julian_days]
	

def get_current( julian_day, rotations_start_days ):
	rotations_numbers = rotations_start_days[0]
	julian_days = rotations_start_days[1]
	for iterator in range(len(julian_days)):
		if julian_days[iterator] <= julian_day < julian_days[iterator + 1]:
			return rotations_numbers[iterator]
		
	

def get_not_in_limit(sunspot_data, column_name, limit):
	sunspot_data_exceeded_limit = sunspot_data[(sunspot_data[column_name] > limit)]
	return sunspot_data_exceeded_limit
	
	
def get_in_limit(sunspot_data, column_names, limits):
	sunspot_data_in_limit = sunspot_data[(sunspot_data[column_names[0]] <= limits[0]) & (sunspot_data[column_names[1]] <= limits[1])]
	return sunspot_data_in_limit

main()

