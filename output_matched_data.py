#!/usr/bin/env python3

import pandas as pd
		
def main():
	input_file_name_daily_all = 'dailydata_allDPD_clear.txt'
	input_file_name_daily_fixed = 'dailydata_modified_manually.txt'
	input_file_name_matched_groups = 'matched_groups.txt'
	output_file_name_matched_groups_data_north = 'matched_groups_data_final_north.txt'
	output_file_name_matched_groups_data_south = 'matched_groups_data_final_south.txt'
	
	sunspot_data_all = pd.read_table(input_file_name_daily_all, header=0)
	sunspot_data_fixed = pd.read_table(input_file_name_daily_fixed, header=0)
	sunspot_data_no_fix = sunspot_data_all[~(sunspot_data_all.NOAA.isin(sunspot_data_fixed.NOAA))]
		
	sunspot_data_final_daily = sunspot_data_fixed
	sunspot_data_final_daily = sunspot_data_final_daily.append(sunspot_data_no_fix, ignore_index=True)
	
	with open(input_file_name_matched_groups, 'r+') as ifile:
		matched_groups = [line[:-1] for line in ifile.readlines()]

	ofile_data_north = open(output_file_name_matched_groups_data_north, 'a')
	ofile_data_south = open(output_file_name_matched_groups_data_south, 'a')
	
	sunspot_data_final_daily['Latitude*Area'] = sunspot_data_final_daily['Latitude'] * sunspot_data_final_daily['CorrectedWholeSpotArea']
	sunspot_data_grouped = sunspot_data_final_daily.groupby('NOAA').agg({'CorrectedWholeSpotArea': 'sum', 'Latitude*Area': 'sum'})
	sunspot_data_grouped['LatitudeAverage'] = sunspot_data_grouped['Latitude*Area'] / sunspot_data_grouped['CorrectedWholeSpotArea']
	sunspot_data_grouped.reset_index(inplace=True)
	
	for row in matched_groups:
		row_list = row.split("\t")
		group1 = row_list[3]
		group2 = row_list[4]
		
		data_group1 = sunspot_data_final_daily[(sunspot_data_final_daily['NOAA'] == group1)]
		data_group1 = data_group1[['YYYY','MM','DD','NOAA','CorrectedWholeSpotArea','Longitude','Latitude','PositionOnDisk']]
		
		data_group2 = sunspot_data_final_daily[(sunspot_data_final_daily['NOAA'] == group2)]
		data_group2 = data_group2[['YYYY','MM','DD','NOAA','CorrectedWholeSpotArea','Longitude','Latitude','PositionOnDisk']]
		
		data_group1_grouped = sunspot_data_grouped[(sunspot_data_grouped['NOAA'] == group1)].reset_index()
		latitudeAverage = data_group1_grouped.at[0,'LatitudeAverage']
		
		if latitudeAverage >= 0:
			ofile = ofile_data_north
		elif latitudeAverage:
			ofile = ofile_data_south
			
		ofile.write(row+'\n')
		ofile.write(data_group1.to_string(header = False, index = False))
		ofile.write('\n\n')
		ofile.write(data_group2.to_string(header = False, index = False))
		ofile.write('\n\n')
						
	ofile_data_north.close()
	ofile_data_south.close()
	
main()
