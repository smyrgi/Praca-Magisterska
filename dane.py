#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
from astropy.time import Time


def main():
	file_name = 'gDPD1978bb'
	file_name = 'alldataDPD'
	input_file_name = file_name + '.txt'
	#input_file_name = 'alldataDPD.txt'
	output_file_name = file_name + '_modified.txt'
	output_file_name_clear = file_name + '_clear.txt'
	output_file_name_longitude = file_name + '_longitudelimit2.txt'
	output_file_name_latitude = file_name + '_latitudelimit2.txt'
	output_file_name_inlimit = file_name + '_modified_inlimit.txt'
	latitude_limit = 15
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
	
	sunspot_data_grouped = group_data(sunspot_data)
	del(sunspot_data)
	
	sunspot_data_final = format_data(sunspot_data_grouped)
	del(sunspot_data_grouped)
	
	incorrect_data = validate_final(sunspot_data_final)
	if incorrect_data: 
		[print('Niepoprawne dane - %s: %s dla grupy: %s' % data) for data in incorrect_data]
	else:
		sunspot_data_final.to_csv( output_file_name, sep='	', header = None, index = None )
	
	sunspot_data_longitude_range = get_not_in_limit(sunspot_data_final, column_name = 'LongitudeRange', limit = longitude_limit)
	sunspot_data_latitude_range = get_not_in_limit(sunspot_data_final, column_name = 'LatitudeRange', limit = latitude_limit)
	sunspot_data_in_limit = get_in_limit(sunspot_data_final, column_names = ['LongitudeRange', 'LatitudeRange'], limits = [longitude_limit,latitude_limit])
	
	sunspot_data_longitude_range.to_csv( output_file_name_longitude, sep='	', header = None, index = None )
	sunspot_data_latitude_range.to_csv( output_file_name_latitude, sep='	', header = None, index = None )
	sunspot_data_in_limit.to_csv( output_file_name_inlimit, sep='	', header = None, index = None )
	

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
		
		
def group_data(sunspot_data):
	sunspot_data = fix_longitude(sunspot_data)
			
	sunspot_data_grouped = sunspot_data.groupby('NOAA').agg({'YYYY': 'min', 'CarringtonRotation': 'min','PositionOnDisk': ['min', 'max'],
															 'Longitude': ['min', 'max'],'Latitude': ['min', 'max'],'JulianDay': ['min', 'max'], 
															 'CorrectedWholeSpotArea': 'sum', 'Longitude*Area': 'sum', 'Latitude*Area': 'sum'})
	
	sunspot_data_grouped = get_range(sunspot_data_grouped)
	sunspot_data_grouped = get_average(sunspot_data_grouped)
	sunspot_data_grouped = recalculate_longitude(sunspot_data_grouped)
	
	return sunspot_data_grouped

def fix_longitude(sunspot_data):	
	sunspot_data_grouped = sunspot_data.groupby('NOAA').agg({'YYYY': 'min', 'CarringtonRotation': 'min','PositionOnDisk': ['min', 'max'],
															 'Longitude': ['min', 'max'],'Latitude': ['min', 'max'],'JulianDay': ['min', 'max'], 
															 'CorrectedWholeSpotArea': 'sum', 'Longitude*Area': 'sum', 'Latitude*Area': 'sum'})
	
	sunspot_data_grouped_incorrect = sunspot_data_grouped[ (sunspot_data_grouped['Longitude']['max'] > 270) & (sunspot_data_grouped['Longitude']['min'] < 90) ]
	incorrect_groups = sunspot_data_grouped_incorrect.index
	
	for group in incorrect_groups:
		sunspot_data.loc[(sunspot_data['NOAA'] == group) & (sunspot_data['Longitude'] > 270), 'Longitude'] -= 360 
	
	return sunspot_data
		
		
def get_range(sunspot_data_grouped):
	sunspot_data_grouped['LongitudeRange'] = sunspot_data_grouped['Longitude']['max'] - sunspot_data_grouped['Longitude']['min']
	sunspot_data_grouped['LatitudeRange'] = sunspot_data_grouped['Latitude']['max'] - sunspot_data_grouped['Latitude']['min']
	return sunspot_data_grouped
	
				
def get_average(sunspot_data_grouped):
	sunspot_data_grouped['LongitudeAverage'] = sunspot_data_grouped['Longitude*Area']['sum'] / sunspot_data_grouped['CorrectedWholeSpotArea']['sum']
	sunspot_data_grouped['LatitudeAverage'] = sunspot_data_grouped['Latitude*Area']['sum'] / sunspot_data_grouped['CorrectedWholeSpotArea']['sum']
	return sunspot_data_grouped


def recalculate_longitude(sunspot_data_grouped):
	sunspot_data_grouped.loc[sunspot_data_grouped['Longitude']['min'] < 0, ('Longitude', 'min')] += 360
	sunspot_data_grouped.loc[sunspot_data_grouped['Longitude']['min'] < 0, ('Longitude', 'min')] += 360
	return sunspot_data_grouped
	
		
	
def format_data(sunspot_data):
	final_columns_order = ['YYYY min', 'CarringtonRotation min','NOAA','JulianDay min','JulianDay max','CorrectedWholeSpotArea sum', 
						   'LongitudeAverage','LatitudeAverage','PositionOnDisk min','PositionOnDisk max','Longitude min', 
						   'Longitude max','LongitudeRange','Latitude min','Latitude max','LatitudeRange']
	final_columns_names = ['Year', 'CarringtonRotation', 'NOAA','StartJulianDay','EndJulianDay','TotalGroupArea',
						   'WeightedLongitude', 'WeightedLatitude','StartPosition','EndPosition','MinLongitude',
						   'MaxLongitude','LongitudeRange', 'MinLatitude','MaxLatitude','LatitudeRange']
	
	sunspot_data.columns = [' '.join(column_name).strip() for column_name in sunspot_data.columns.values]
	sunspot_data.reset_index(inplace=True)
	
	sunspot_data_final = sunspot_data[final_columns_order]
	sunspot_data_final.columns = final_columns_names
	
	return sunspot_data_final

	
	
def validate_final(sunspot_data):
	sunspot_data_records = sunspot_data.shape[0]
	incorrect_data = []
	for record_position in range(sunspot_data_records):
		noaa = sunspot_data.at[record_position,'NOAA']
		total_area = sunspot_data.at[record_position,'TotalGroupArea']
		start_position = sunspot_data.at[record_position,'StartPosition']
		end_position = sunspot_data.at[record_position,'EndPosition']
		minimum_longitude = sunspot_data.at[record_position,'MinLongitude']
		maximum_longitude = sunspot_data.at[record_position,'MaxLongitude']
		minimum_latitude = sunspot_data.at[record_position,'MinLatitude']
		maximum_latitude = sunspot_data.at[record_position,'MaxLatitude']
		longitude_range = sunspot_data.at[record_position,'LongitudeRange']
		latitude_range = sunspot_data.at[record_position,'LatitudeRange']
		
		if total_area < 0 or total_area >= 999999:
			incorrect_data.append(('sumaryczna powierzchnia', total_area, noaa))
		if start_position < 0 or start_position > 1:
			incorrect_data.append(('miejsce pojawienia na tarczy', start_position, noaa))
		if end_position < 0 or end_position > 1:
			incorrect_data.append(('miejsce zaniku na tarczy', end_position, noaa))
		if minimum_longitude < 0 or minimum_longitude > 360:
			incorrect_data.append(('długość heliograficzna', minimum_longitude, noaa))
		if maximum_longitude < 0 or maximum_longitude > 360:
			incorrect_data.append(('długość heliograficzna', maximum_longitude, noaa))
		if minimum_latitude < -180 or minimum_latitude > 180:
			incorrect_data.append(('szerokość heliograficzna', minimum_latitude, noaa))
		if maximum_latitude < -180 or maximum_latitude > 180:
			incorrect_data.append(('szerokość heliograficzna', maximum_latitude, noaa))
		if longitude_range < 0 or longitude_range > 360:
			incorrect_data.append(('długość heliograficzna', maximum_longitude, noaa))
		if latitude_range < 0 or latitude_range > 360:
			incorrect_data.append(('szerokość heliograficzna', maximum_latitude, noaa))
		
	return incorrect_data
		
	
def get_not_in_limit(sunspot_data, column_name, limit):
	sunspot_data_exceeded_limit = sunspot_data[(sunspot_data[column_name] > limit)]
	return sunspot_data_exceeded_limit
	
	
def get_in_limit(sunspot_data, column_names, limits):
	sunspot_data_in_limit = sunspot_data[(sunspot_data[column_names[0]] <= limits[0]) & (sunspot_data[column_names[1]] <= limits[1])]
	return sunspot_data_in_limit

main()

