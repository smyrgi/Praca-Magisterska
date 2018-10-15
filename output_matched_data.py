#!/usr/bin/env python3

import pandas as pd
import output_grouped_data
		
def main():
	input_file_name_daily_all = 'dailydata_allDPD_clear.txt'
	input_file_name_daily_fixed = 'dailydata_modified_manually.txt'
	input_file_name_matched_groups = 'matched_groups.txt'
	output_file_name_matched_groups_data = 'matched_groups_data_final.txt'
	
	sunspot_data_all = pd.read_table(input_file_name_daily_all, header=0)
	sunspot_data_fixed = pd.read_table(input_file_name_daily_fixed, header=0)
	sunspot_data_no_fix = sunspot_data_all[~(sunspot_data_all.NOAA.isin(sunspot_data_fixed.NOAA))]
		
	sunspot_data_final_daily = sunspot_data_fixed
	sunspot_data_final_daily = sunspot_data_final_daily.append(sunspot_data_no_fix, ignore_index=True)
	
	with open(input_file_name_matched_groups, 'r+') as ifile:
		matched_groups = [line[:-1] for line in ifile.readlines()]

	ofile = open(output_file_name_matched_groups_data, 'a')
	for row in matched_groups:
		row_list = row.split("\t")
		group1 = row_list[3]
		group2 = row_list[4]
		
		data_group1 = sunspot_data_final_daily[(sunspot_data_final_daily['NOAA'] == group1)]
		data_group1 = data_group1[['YYYY','MM','DD','NOAA','CorrectedWholeSpotArea','Longitude','Latitude','PositionOnDisk']]
		
		data_group2 = sunspot_data_final_daily[(sunspot_data_final_daily['NOAA'] == group2)]
		data_group2 = data_group2[['YYYY','MM','DD','NOAA','CorrectedWholeSpotArea','Longitude','Latitude','PositionOnDisk']]
		
		ofile.write(row+'\n')
		ofile.write(data_group1.to_string(header = False, index = False))
		ofile.write('\n\n')
		ofile.write(data_group2.to_string(header = False, index = False))
		ofile.write('\n\n')
				
	ofile.close()
	
main()