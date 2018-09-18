#!/usr/bin/env python3

import pandas as pd
from scipy.stats import t
import numpy as np
import math
import output_grouped_data

	
def main():	
	input_file_name_before_fix = 'checkmanually_data.txt'
	input_file_name_after_fix = 'checkmanually_data_fixed.txt'
	output_file_name = 'groupdata_modified_manually.txt'
	
	sunspot_data_before_fix = pd.read_table(input_file_name_before_fix, header=0)
	sunspot_data_after_fix = pd.read_table(input_file_name_after_fix, header=0)
	
	sunspot_data_tested = validate_fixed_data(sunspot_data_before_fix, sunspot_data_after_fix)
	
	sunspot_data_final, final_columns_names = output_grouped_data.output_data(sunspot_data_tested, output_file_name)
			
	
	
def validate_fixed_data(sunspot_data_before_fix, sunspot_data_after_fix):
	noaa_groups = set(sunspot_data_before_fix['NOAA'])
	sunspot_data_final = pd.DataFrame()
	
	for group in noaa_groups:
		group_data_final = validate_group_data(sunspot_data_before_fix, sunspot_data_after_fix, group)
		sunspot_data_final = sunspot_data_final.append(group_data_final, ignore_index=True)
		
	return sunspot_data_final
	
		
def validate_group_data(sunspot_data_before_fix, sunspot_data_after_fix, group):
	group_data_before_fix = sunspot_data_before_fix[(sunspot_data_before_fix['NOAA'] == group)]
	group_data_after_fix = sunspot_data_after_fix[(sunspot_data_after_fix['NOAA'] == group)]

	ind_data_removed_correctly = test_removed_data(group_data_before_fix, group_data_after_fix)

	if (ind_data_removed_correctly):
		return group_data_after_fix
	else:
		return group_data_before_fix
		

def test_removed_data(group_data_before_fix, group_data_after_fix):
	group_data_removed = group_data_before_fix[(~(group_data_before_fix.NOAA.isin(group_data_after_fix.NOAA) & 
												  group_data_before_fix.Longitude.isin(group_data_after_fix.Longitude) & 
												  group_data_before_fix.Latitude.isin(group_data_after_fix.Latitude)))]
	
	if not (group_data_removed.empty):
		number_of_records = len(group_data_before_fix)

		t_student_passed_latitude = check_t_student_test(number_of_records, group_data_after_fix, group_data_removed, coordinate = 'Latitude')
		t_student_passed_longitude = check_t_student_test(number_of_records, group_data_after_fix, group_data_removed, coordinate = 'Longitude')

		if (t_student_passed_latitude or t_student_passed_longitude):
			return True
	return False
	
	
def check_t_student_test(n, group_data_after_fix, group_data_removed, coordinate):	
	removed_record = group_data_removed.index.tolist()[0]
	removed_value = group_data_removed.at[removed_record, coordinate]

	mean = np.mean(list(group_data_after_fix[coordinate]))
	t_critical = t.ppf(1-0.025, n-1)
	s = np.std(list(group_data_after_fix[coordinate]))
	
	t_calculated = abs(removed_value - mean) * math.sqrt(n-1) / s
	
	if (t_calculated > t_critical):
		return True
	return False
	

main()
	
