#!/usr/bin/env python3

import pandas as pd
		
def main():
	input_file_name_daily_all = 'dailydata_allDPD_clear.txt'
	input_file_name_daily_fixed = 'dailydata_modified_manually.txt'
	input_file_name_north = 'matched_groups_north.txt'
	input_file_name_south = 'matched_groups_south.txt'
	output_file_name_north = 'matched_groups_data_north.txt'
	output_file_name_south = 'matched_groups_data_south.txt'
	
	sunspot_data_all = pd.read_table(input_file_name_daily_all, header=0)
	sunspot_data_fixed = pd.read_table(input_file_name_daily_fixed, header=0)
	sunspot_data_no_fix = sunspot_data_all[~(sunspot_data_all.NOAA.isin(sunspot_data_fixed.NOAA))]
		
	sunspot_data_final_daily = sunspot_data_fixed
	sunspot_data_final_daily = sunspot_data_final_daily.append(sunspot_data_no_fix, ignore_index=True)
	
	output_matched_groups_data(sunspot_data_final_daily, input_file_name_north, output_file_name_north)
	output_matched_groups_data(sunspot_data_final_daily, input_file_name_south, output_file_name_south)
	
	
def output_matched_groups_data(sunspot_data, input_file_name, output_file_name):
	with open(input_file_name, 'r+') as ifile:
		matched_groups = [line[:-1] for line in ifile.readlines()]
	
	with open(output_file_name, 'a') as ofile:
		for row in matched_groups:
			row_list = row.split()
			group1 = row_list[3]
			group2 = row_list[4]

			data_group1 = sunspot_data[(sunspot_data['NOAA'] == group1)]
			data_group1 = data_group1[['YYYY','MM','DD','NOAA','CorrectedWholeSpotArea','Longitude','Latitude','PositionOnDisk']]

			data_group2 = sunspot_data[(sunspot_data['NOAA'] == group2)]
			data_group2 = data_group2[['YYYY','MM','DD','NOAA','CorrectedWholeSpotArea','Longitude','Latitude','PositionOnDisk']]

			ofile.write(row+'\n')
			ofile.write(data_group1.to_string(header = False, index = False))
			ofile.write('\n\n')
			ofile.write(data_group2.to_string(header = False, index = False))
			ofile.write('\n\n')

	
main()
