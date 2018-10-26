#!/usr/bin/env python3

import pandas as pd
import output_grouped_data


def main():
	input_file_name_all = 'dailydata_allDPD_clear.txt'
	input_file_name_dixon = 'dailydata_fixed_dixon.txt'
	input_file_name_manually = 'dailydata_modified_manually.txt'
		
	sunspot_data_all = pd.read_table(input_file_name_all, header=0)
	sunspot_data_dixon = pd.read_table(input_file_name_dixon, header=0)
	sunspot_data_manually = pd.read_table(input_file_name_manually, header=0)
	sunspot_data_modified = sunspot_data_dixon.append(sunspot_data_manually, ignore_index=True)
		
	sunspot_data_all_north = sunspot_data_all.loc[sunspot_data_all['Latitude'] >= 0]
	sunspot_data_all_south = sunspot_data_all.loc[sunspot_data_all['Latitude'] < 0]
				
	sunspot_data_modified_north = sunspot_data_modified.loc[sunspot_data_modified['Latitude'] >= 0]
	sunspot_data_modified_south = sunspot_data_modified.loc[sunspot_data_modified['Latitude'] < 0]
		
	print("Liczba usuniętych pomiarów dla półkuli N:",len(sunspot_data_all_north) - len(sunspot_data_modified_north))
	print("Liczba usuniętych pomiarów dla półkuli S:",len(sunspot_data_all_south) - len(sunspot_data_modified_south))
	print("Liczba usuniętych pomiarów:",len(sunspot_data_all) - len(sunspot_data_modified))
	
	removed_groups = sunspot_data_all[~(sunspot_data_all.NOAA.isin(sunspot_data_modified.NOAA))]
	removed_groups = removed_groups.groupby('NOAA').sum()
	print("W tym liczba całkowicie usuniętych grup:",len(removed_groups))
	
main()
	
	
	
