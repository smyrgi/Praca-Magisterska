#!/usr/bin/env python3

import pandas as pd


def output_data(sunspot_data, output_file_name):
	sunspot_data_grouped = group_data(sunspot_data)
	del(sunspot_data)
	
	sunspot_data_final, final_columns_names = format_data(sunspot_data_grouped)
	del(sunspot_data_grouped)
	
	incorrect_data = validate_final(sunspot_data_final)
	if incorrect_data: 
		[print('Niepoprawne dane - %s: %s dla grupy: %s' % data) for data in incorrect_data]
	else:
		sunspot_data_final.to_csv( output_file_name, sep='	', header = final_columns_names, index = None )
	
	return sunspot_data_final, final_columns_names
		
		
def group_data(sunspot_data):
	sunspot_data = fix_longitude(sunspot_data)
			
	sunspot_data_grouped = sunspot_data.groupby('NOAA').agg({'YYYY': 'min', 'CarringtonRotation': 'min','PositionOnDisk': ['min', 'max',get_center_position],
															 'Longitude': ['min', 'max'],'Latitude': ['min', 'max'],'JulianDay': 
															 ['min', 'max', lambda group: get_center_time(sunspot_data.loc[group.index])], 
															 'CorrectedWholeSpotArea': 'sum', 'Longitude*Area': 'sum', 'Latitude*Area': 'sum'})

	sunspot_data_grouped = validate_area(sunspot_data_grouped)
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

				
def get_center_position(sunspot_data_positions):
	center_position = sunspot_data_positions.iloc[(sunspot_data_positions-0.5).abs().argsort()[:1]]
	return center_position


def get_center_time(group_data): #,lambda g: get_center_time(sunspot_data.loc[g.index])
	group_data_center = group_data.iloc[(group_data['PositionOnDisk']-0.5).abs().argsort()[:1]]
	center_time = group_data_center['JulianDay']
	return center_time
	
	
def validate_area(sunspot_data_grouped):
	sunspot_data_grouped_corrected = sunspot_data_grouped[sunspot_data_grouped['CorrectedWholeSpotArea']['sum'] != 0]
	return sunspot_data_grouped_corrected
	
		
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
	final_columns_order = ['YYYY min', 'CarringtonRotation min', 'NOAA', 'JulianDay min', 'JulianDay max', 'CorrectedWholeSpotArea sum', 
						   'LongitudeAverage', 'LatitudeAverage', 'PositionOnDisk min', 'PositionOnDisk max', 'Longitude min', 'Longitude max',
						   'LongitudeRange', 'Latitude min', 'Latitude max', 'LatitudeRange', 'PositionOnDisk get_center_position', 'JulianDay <lambda>']
	
	final_columns_names = ['Year', 'CarringtonRotation', 'NOAA', 'StartJulianDay', 'EndJulianDay', 'TotalGroupArea',
						   'WeightedLongitude', 'WeightedLatitude', 'StartPosition', 'EndPosition', 'MinLongitude', 'MaxLongitude',
						   'LongitudeRange', 'MinLatitude', 'MaxLatitude', 'LatitudeRange', 'CenterPosition', 'CenterJulianDay']
	
	sunspot_data.columns = [' '.join(column_name).strip() for column_name in sunspot_data.columns.values]
	sunspot_data.reset_index(inplace=True)
	
	sunspot_data_final = sunspot_data[final_columns_order]
	sunspot_data_final.columns = final_columns_names
	
	return sunspot_data_final, final_columns_names

	
	
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
		
