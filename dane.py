#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
from astropy.time import Time


def main():
	columns_names = ["DataType","YYYY","MM","DD","HH","mm","ss","NOAA","UmbraArea","WholeSpotArea", "CorrectedUmbraArea",
					 "CorrectedWholeSpotArea", "Latitude","Longitude", "LongitudinalDistance","PositionAngle","DistanceFromCentre"]
	sunspot_data = pd.read_fwf('gDPD1978aa.txt', header=None, names=columns_names)
	sunspot_data = validate_input(sunspot_data)	
	
	sunspot_data = add_data(sunspot_data)

	sunspot_data_grouped = get_average(sunspot_data)
	del(sunspot_data)

	sunspot_data_final = format_data(sunspot_data_grouped)
	del(sunspot_data_grouped)
	
	error_message = validate_final(sunspot_data_final)
	if error_message: 
		print (error_message)
	else:
		sunspot_data_final.to_csv('output1aa.txt', sep='	', header = None, index = None)
		


def validate_input(sunspot_data):
	corrected_sunspot_data = remove_invalid(sunspot_data)
	corrected_sunspot_data = correct_seconds(corrected_sunspot_data)
	return corrected_sunspot_data
	
	
def remove_invalid(sunspot_data):
	columns_to_validate = ['Latitude','Longitude','LongitudinalDistance','PositionAngle','DistanceFromCentre']
	invalid_data = 999999
	valid_sunspot_data = sunspot_data[(sunspot_data[columns_to_validate] != invalid_data).all(axis=1)]
	corrected_sunspot_data = valid_sunspot_data.reset_index(drop=True)
	return corrected_sunspot_data
	
	
def correct_seconds(sunspot_data):
	sunspot_data.loc[sunspot_data['ss'] == 60, "mm"] += 1
	sunspot_data.loc[sunspot_data['ss'] == 60, "ss"] = 0
	return sunspot_data
	
		
	
def add_data(sunspot_data):
	sunspot_data['JulianDay'] = sunspot_data.apply(get_julian_day, axis=1)
	sunspot_data['Longitude*Area'] = sunspot_data['Longitude'] * sunspot_data['CorrectedWholeSpotArea']
	sunspot_data['Latitude*Area'] = sunspot_data['Latitude'] * sunspot_data['CorrectedWholeSpotArea']
	sunspot_data['PositionOnDisk'] = ( sunspot_data['LongitudinalDistance'] + 90 ) / 180
	sunspot_data['CarringtonRotation'] = get_carrington_rotations(sunspot_data)
	return sunspot_data
	
	
def get_julian_day(date):
	# wyznacz dzień juliański dla danej daty
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
			rotation_number, julian_day = line.split("\t")
			rotations_numbers.append(int(rotation_number))
			julian_days.append(float(julian_day))
	
	return [rotations_numbers, julian_days]
	

def get_current( julian_day, rotations_start_days ):
	rotations_numbers = rotations_start_days[0]
	julian_days = rotations_start_days[1]
	for iterator in range(len(julian_days)):
		if julian_days[iterator] <= julian_day < julian_days[iterator + 1]:
			return rotations_numbers[iterator]
		
		
		
def get_average(sunspot_data):
	sunspot_data_grouped = sunspot_data.groupby('NOAA').agg({'YYYY': 'min', 'CarringtonRotation': 'min','PositionOnDisk': ['min', 'max'],
															 'Longitude': ['min', 'max'],'Latitude': ['min', 'max'],'JulianDay': ['min', 'max'], 
															 'CorrectedWholeSpotArea': 'sum', 'Longitude*Area': 'sum', 'Latitude*Area': 'sum'})
	
	sunspot_data_grouped['LongitudeRange'] = sunspot_data_grouped['Longitude']['max'] - sunspot_data_grouped['Longitude']['min']
	sunspot_data_grouped['LatitudeRange'] = sunspot_data_grouped['Latitude']['max'] - sunspot_data_grouped['Latitude']['min']
	sunspot_data_grouped['LongitudeAverage'] = sunspot_data_grouped['Longitude*Area']['sum'] / sunspot_data_grouped['CorrectedWholeSpotArea']['sum']
	sunspot_data_grouped['LatitudeAverage'] = sunspot_data_grouped['Latitude*Area']['sum'] / sunspot_data_grouped['CorrectedWholeSpotArea']['sum']
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
			return "Niepoprawne dane - sumaryczna powierzchnia: " + total_area + " dla grupy: " + noaa
		elif start_position < 0 or start_position > 1:
			return "Niepoprawne dane - miejsce pojawienia na tarczy: " + str(start_position) + " dla grupy: " + noaa
		elif end_position < 0 or end_position > 1:
			return "Niepoprawne dane - miejsce zaniku na tarczy: " + str(end_position) + " dla grupy: " + noaa
		elif minimum_longitude < 0 or minimum_longitude > 360:
			return "Niepoprawne dane - długość heliograficzna: " + minimum_longitude + " dla grupy: " + noaa
		elif maximum_longitude < 0 or maximum_longitude > 360:
			return "Niepoprawne dane - długość heliograficzna: " + maximum_longitude + " dla grupy: " + noaa
		elif minimum_latitude < -180 or minimum_latitude > 180:
			return "Niepoprawne dane - szeYearość heliograficzna: " + minimum_latitude + " dla grupy: " + noaa
		elif maximum_latitude < -180 or maximum_latitude > 180:
			return "Niepoprawne dane - szeYearość heliograficzna: " + maximum_latitude + " dla grupy: " + noaa
		elif longitude_range < 0 or longitude_range > 360:
			return "Niepoprawne dane - długość heliograficzna: " + maximum_longitude + " dla grupy: " + noaa
		elif latitude_range < 0 or latitude_range > 360:
			return "Niepoprawne dane - szeYearość heliograficzna: " + maximum_latitude + " dla grupy: " + noaa
	
	
main()



