#!/usr/bin/env python3

import pandas as pd
import astropy.units as u
from sunpy.physics.differential_rotation import diff_rot

	
def main():		
	input_file_name_fixedlimits = 'groupdata_fixedlimits.txt'
	input_file_name_manually = 'groupdata_modified_manually.txt'
	output_file_name_groups = 'matched_groups.txt'
	output_file_name_data = 'matched_groups_data.txt'
	
	columns_names = ['Year', 'CarringtonRotation', 'NOAA','StartJulianDay','EndJulianDay','TotalGroupArea',
						   'WeightedLongitude', 'WeightedLatitude','StartPosition','EndPosition','MinLongitude',
						   'MaxLongitude','LongitudeRange', 'MinLatitude','MaxLatitude','LatitudeRange']

	sunspot_data_fixedlimits = pd.read_table(input_file_name_fixedlimits, header=0)
	sunspot_data_manually = pd.read_table(input_file_name_manually, header=0)
	
	sunspot_data = sunspot_data_fixedlimits
	sunspot_data = sunspot_data.append(sunspot_data_manually, ignore_index=True)
	
	data_on_east = sunspot_data.loc[sunspot_data['StartPosition'] < 0.1]
	data_on_west = sunspot_data.loc[sunspot_data['EndPosition'] > 0.9]
	
	data_on_east = data_on_east.sort_values(by='StartJulianDay')
	data_on_west = data_on_west.sort_values(by='EndJulianDay')
	data_on_west['ExpectedStartJulianDay'] = data_on_west['EndJulianDay'] + get_rotation_period(data_on_west['WeightedLatitude'])
	
	groups_matched = get_matched_groups(data_on_west, data_on_east)

	with open(output_file_name_groups, 'w') as ofile:
		for pair in groups_matched:
			ofile.write('\t'.join(pair)+'\n')
		
	groups_matched_all = [group for pair in groups_matched for group in pair]
	data_groups_matched = sunspot_data.loc[sunspot_data['NOAA'].isin(groups_matched_all)]
	data_groups_matched = data_groups_matched.sort_values(by='NOAA')
	data_groups_matched.to_csv( output_file_name_data, sep='	', header = columns_names, index = None )
	
		
		
def get_rotation_period(latitude_value):
	dt = 1 * u.day
	latitude = u.Quantity(latitude_value, 'deg')
	rotation_rate = diff_rot(dt, latitude) / dt 
	rotation_period = 360 * u.deg / rotation_rate
	return rotation_period.value
	
	
def get_matched_groups(data_on_west, data_on_east):
	groups_matched = []
	for index_west, group_data_on_west in data_on_west.iterrows():
		for index_east, group_data_on_east in data_on_east.iterrows():
			if (approximately_equal(group_data_on_west['ExpectedStartJulianDay'], group_data_on_east['StartJulianDay'])):
				# times matched
				if (approximately_equal(group_data_on_west['WeightedLatitude'], group_data_on_east['WeightedLatitude'], precision = 0.5)):
					# latitude matched
					groups_matched.append([group_data_on_west['NOAA'], group_data_on_east['NOAA']])
				break
			elif (group_data_on_west['ExpectedStartJulianDay'] < group_data_on_east['StartJulianDay']):
				# times not matched
				break
	return groups_matched
	
	
def approximately_equal(value1, value2, precision = 1):
	if (value1 - precision) < value2 < (value1 + precision):
		return True
	return False
		
	
main()
	
	