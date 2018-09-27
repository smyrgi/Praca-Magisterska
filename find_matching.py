#!/usr/bin/env python3

import pandas as pd
import astropy.units as u
from sunpy.physics.differential_rotation import diff_rot

	
def main():		
	input_file_name_fixedlimits = 'groupdata_fixedlimits.txt'
	input_file_name_manually = 'groupdata_modified_manually.txt'
	output_file_name_groups = 'matched_groups.txt'
	output_file_name_data = 'matched_groups_data.txt'
	
	sunspot_data_fixedlimits = pd.read_table(input_file_name_fixedlimits, header=0)
	sunspot_data_manually = pd.read_table(input_file_name_manually, header=0)
		
	sunspot_data = sunspot_data_fixedlimits
	sunspot_data = sunspot_data.append(sunspot_data_manually, ignore_index=True)
	sunspot_data = sunspot_data.sort_values(by='CenterJulianDay')
	
	#data_on_east = sunspot_data.loc[sunspot_data['StartPosition'] < 0.1]
	data_not_disappearing = sunspot_data.loc[sunspot_data['EndPosition'] > 0.8]
	
	#data_on_east = data_on_east.sort_values(by='StartJulianDay')
	data_not_disappearing = data_not_disappearing.sort_values(by='CenterJulianDay')
	data_not_disappearing['ExpectedCenterJulianDay'] = data_not_disappearing['CenterJulianDay'] + get_rotation_period(data_not_disappearing['WeightedLatitude'])
	data_not_disappearing['CenterJulianDay'] = data_not_disappearing['CenterJulianDay'].astype(int)
	data_not_disappearing['ExpectedCenterJulianDay'] = data_not_disappearing['ExpectedCenterJulianDay'].astype(int)
	
	groups_matched = get_matched_groups(data_not_disappearing, sunspot_data)

	with open(output_file_name_groups, 'w') as ofile:
		for pair in groups_matched:
			ofile.write('\t'.join(pair)+'\n')
		
	columns_names = sunspot_data.columns
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
	
	
def get_matched_groups(data_not_disappearing, sunspot_data): #groups_matched.append([group_data_not_disappearing['NOAA'], group_data_on_east['NOAA']])
	groups_matched = []
	for index_west, group_data_not_disappearing in data_not_disappearing.iterrows():
		data_recurrent = sunspot_data.loc[abs(sunspot_data['CenterJulianDay'] - group_data_not_disappearing['ExpectedCenterJulianDay']) < 1]
		# times matched
		for index_east, group_data in data_recurrent.iterrows():
			if (check_close_position(group_data_not_disappearing, group_data)):
				# latitude matched
				groups_matched.append([group_data_not_disappearing['NOAA'], group_data['NOAA']])
				break
	return groups_matched

	
def check_close_position(group_data1, group_data2):
	precision_longitude = 10
	precision_latitude = 1
		
	if ((abs(group_data1['WeightedLongitude'] - group_data2['WeightedLongitude']) < precision_longitude) and
		(abs(group_data1['WeightedLatitude'] - group_data2['WeightedLatitude']) < precision_latitude)):
		return True
	return False

		
	
main()
	
	
