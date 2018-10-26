#!/usr/bin/env python3

import pandas as pd

	
def main():	
	input_file_name_north = 'groupdata_final_north.txt'
	input_file_name_south = 'groupdata_final_south.txt'
	output_file_name_north = 'matched_groups_north.txt'
	output_file_name_south = 'matched_groups_south.txt'
	
	find_matching(input_file_name_north, output_file_name_north)
	find_matching(input_file_name_south, output_file_name_south)
	
	
def find_matching(input_file_name, output_file_name):
	sunspot_data = pd.read_table(input_file_name, header=0)		
	sunspot_data = sunspot_data.sort_values(by='StartJulianDay')
	
	data_not_disappearing = sunspot_data.loc[sunspot_data['EndPosition'] > 0.8]
	data_not_disappearing = data_not_disappearing.sort_values(by='StartJulianDay')
	
	groups_matched = get_matched_groups(data_not_disappearing, sunspot_data)

	with open(output_file_name, 'w') as ofile:
		for match in groups_matched:
			ofile.write('\t'.join(match)+'\n')
		
	
def get_matched_groups(data_not_disappearing, sunspot_data): 
	groups_matched = []
	for index_not_disappearing, group_data_not_disappearing in data_not_disappearing.iterrows():
		data_recurrent = sunspot_data.loc[((group_data_not_disappearing['StartJulianDay'] + 10) < sunspot_data['StartJulianDay']) &
										  (sunspot_data['StartJulianDay'] < (group_data_not_disappearing['StartJulianDay'] + 30))]
					
		# times matched
		for index, group_data in data_recurrent.iterrows():
			precisions = [[1,5], [2,10], [3,15]]
			for precision_latitude, precision_longitude in precisions:			
				if ((group_data_not_disappearing['MaxLatitude'] + precision_latitude) >= group_data['MinLatitude'] and 
				(group_data_not_disappearing['MinLatitude'] + precision_latitude) <= group_data['MaxLatitude'] and 
				(group_data_not_disappearing['MaxLongitude'] + precision_longitude) >= group_data['MinLongitude'] and 
				(group_data_not_disappearing['MinLongitude'] + precision_longitude) <= group_data['MaxLongitude']) :
					# position matched
					groups_matched.append([str(precision_longitude), str(group_data_not_disappearing['Year']), 
										   str(group_data_not_disappearing['CarringtonRotation']), group_data_not_disappearing['NOAA'], 
										   group_data['NOAA']])
					break
			
	return groups_matched
	
	
main()
	
	
