#!/usr/bin/env python3

import pandas as pd

	
def main():		
	input_file_name_fixedlimits = 'groupdata_fixedlimits.txt'
	input_file_name_manually = 'groupdata_modified_manually.txt'
	output_file_name_groups = 'matched_groups.txt'
	carringtonRotation = 27.2753
	
	sunspot_data_fixedlimits = pd.read_table(input_file_name_fixedlimits, header=0)
	sunspot_data_manually = pd.read_table(input_file_name_manually, header=0)
		
	sunspot_data = sunspot_data_fixedlimits
	sunspot_data = sunspot_data.append(sunspot_data_manually, ignore_index=True)
	sunspot_data = sunspot_data.sort_values(by='CenterJulianDay')
	
	data_not_disappearing = sunspot_data.loc[sunspot_data['EndPosition'] > 0.8]
	data_not_disappearing = data_not_disappearing.sort_values(by='CenterJulianDay')
	data_not_disappearing['ExpectedCenterJulianDay'] = data_not_disappearing['CenterJulianDay'] + carringtonRotation
	
	groups_matched = get_matched_groups(data_not_disappearing, sunspot_data)

	with open(output_file_name_groups, 'w') as ofile:
		for match in groups_matched:
			ofile.write('\t'.join(match)+'\n')
					
	
def get_matched_groups(data_not_disappearing, sunspot_data): 
	groups_matched = []
	for index, group_data_not_disappearing in data_not_disappearing.iterrows():
		data_recurrent = sunspot_data.loc[abs(sunspot_data['CenterJulianDay'] - group_data_not_disappearing['ExpectedCenterJulianDay']) < 1]
		# times matched
		for index_east, group_data in data_recurrent.iterrows():
			precision_longitude = 5
			precision_latitude = 1
			if (check_close_position(group_data_not_disappearing, group_data, precision_longitude, precision_latitude)):
				# position matched
				groups_matched.append([str(precision_longitude), str(group_data_not_disappearing['Year']), 
									   str(group_data_not_disappearing['CarringtonRotation']), group_data_not_disappearing['NOAA'], 
									   group_data['NOAA']])
			else:
				precision_longitude = 10
				precision_latitude = 2
				if (check_close_position(group_data_not_disappearing, group_data, precision_longitude, precision_latitude)):
					# position matched
					groups_matched.append([str(precision_longitude), str(group_data_not_disappearing['Year']), 
										   str(group_data_not_disappearing['CarringtonRotation']), group_data_not_disappearing['NOAA'], 
										   group_data['NOAA']])
				else:
					precision_longitude = 15
					precision_latitude = 3
					if (check_close_position(group_data_not_disappearing, group_data, precision_longitude, precision_latitude)):
						# position matched
						groups_matched.append([str(precision_longitude), str(group_data_not_disappearing['Year']), 
											   str(group_data_not_disappearing['CarringtonRotation']), group_data_not_disappearing['NOAA'], 
											   group_data['NOAA']])
				
	return groups_matched

	
def check_close_position(group_data1, group_data2, precision_longitude, precision_latitude):
	if ((abs(group_data1['WeightedLongitude'] - group_data2['WeightedLongitude']) <= precision_longitude) and
		(abs(group_data1['WeightedLatitude'] - group_data2['WeightedLatitude']) <= precision_latitude)):
		return True
	return False

		
	
main()
	
	
