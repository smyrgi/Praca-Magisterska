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
	columns_positions = [(0, 4), (5, 12), (13, 20), (21, 29), (30, 38), (39, 45), (46, 55), (56, 64), (65, 73), (74, 80), (81, 88), (89, 96), (97, 106), (107, 113), (114, 120), (121, 129)]

	sunspot_data = pd.read_fwf(input_file_name, header=0, colspecs=columns_positions)
	sunspot_data = sunspot_data.sort_values(by='StartDay')
	
	data_not_disappearing = sunspot_data.loc[sunspot_data['EndPos'] > 0.8]
	data_not_disappearing = data_not_disappearing.sort_values(by='StartDay')
	
	groups_matched = get_matched_groups(data_not_disappearing, sunspot_data)
	
	with open(output_file_name, 'w') as ofile:
		groups_matched_df = pd.DataFrame(groups_matched)
		ofile.write(groups_matched_df.to_string(header = None, index = None ))
		
	
def get_matched_groups(data_not_disappearing, sunspot_data): 
	groups_matched = []
	precisions_latitude = [1,2,3]
	precisions_longitude = [5,10,15]
	precisions = [[x, y] for x in precisions_latitude for y in precisions_longitude]
	
	for index_not_disappearing, group_data_not_disappearing in data_not_disappearing.iterrows():
		data_recurrent = sunspot_data.loc[((group_data_not_disappearing['StartDay'] + 10) < sunspot_data['StartDay']) &
										  (sunspot_data['StartDay'] < (group_data_not_disappearing['StartDay'] + 30))]
					
		# times matched
		for index, group_data in data_recurrent.iterrows():
			for precision_latitude, precision_longitude in precisions:			
				if ((group_data_not_disappearing['MaxLat'] + precision_latitude) >= group_data['MinLat'] and 
				(group_data_not_disappearing['MinLat'] + precision_latitude) <= group_data['MaxLat'] and 
				(group_data_not_disappearing['MaxLong'] + precision_longitude) >= group_data['MinLong'] and 
				(group_data_not_disappearing['MinLong'] + precision_longitude) <= group_data['MaxLong']) :
					# position matched
					groups_matched.append([str(precision_longitude), str(group_data_not_disappearing['Year']), 
										   str(group_data_not_disappearing['CarrRot']), group_data_not_disappearing['NOAA'], 
										   group_data['NOAA']])
					break
			
	return groups_matched
	
	
main()
	
	
