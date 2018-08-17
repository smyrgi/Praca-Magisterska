#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
from astropy.time import Time
from scipy.stats import t
import numpy as np
import math
import dane
		
def main():	
	file_name_before_fix = 'checkmanually_data1.txt' #daily data
	file_name_after_fix = 'checkmanually_data_fixed1.txt' #daily data
	output_file_name = 'data_modified_manually.txt'
	
	# t-student - done
	# dane.group_data
	# dane.format_data
	# dane.validate_final
	# save to file
	
	
	sunspot_data_before_fix = pd.read_table(file_name_before_fix, header=0)
	sunspot_data_after_fix = pd.read_table(file_name_after_fix, header=0)
	
	sunspot_data_tested = validate_fixed_data(sunspot_data_before_fix, sunspot_data_after_fix)
	
	output_data(sunspot_data_tested, output_file_name)
	
	
	"""
	sunspot_data_grouped = group_data(sunspot_data)
	del(sunspot_data)
	
	sunspot_data_final = format_data(sunspot_data_grouped)
	del(sunspot_data_grouped)
	
	incorrect_data = validate_final(sunspot_data_final)
	if incorrect_data: 
		[print('Niepoprawne dane - %s: %s dla grupy: %s' % data) for data in incorrect_data]
	else:
		sunspot_data_final.to_csv( output_file_name, sep='	', header = None, index = None )
	"""
	
	
	
	#print (sunspot_data_final)

		
	
	
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
	### validate if outliner correctly removed
	
	group_data_removed = group_data_before_fix[(~(group_data_before_fix.NOAA.isin(group_data_after_fix.NOAA) & 
												  group_data_before_fix.Longitude.isin(group_data_after_fix.Longitude) & 
												  group_data_before_fix.Latitude.isin(group_data_after_fix.Latitude)))]
	
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
	t_critical = t.ppf(1-0.025, n-2)
	s = np.std(list(group_data_after_fix[coordinate]))
	
	g_min = mean - t_critical * math.sqrt(n/(n-2))*s
	g_max = mean + t_critical * math.sqrt(n/(n-2))*s
	
	if (removed_value < g_min or removed_value > g_max):
		return True
	return False


def output_data(sunspot_data_tested, output_file_name):
	sunspot_data_grouped = dane.group_data(sunspot_data_tested)
	del(sunspot_data_tested)
	
	sunspot_data_final = dane.format_data(sunspot_data_grouped)
	del(sunspot_data_grouped)
	
	incorrect_data = dane.validate_final(sunspot_data_final)
	if incorrect_data: 
		[print('Niepoprawne dane - %s: %s dla grupy: %s' % data) for data in incorrect_data]
	else:
		sunspot_data_final.to_csv( output_file_name, sep='	', header = None, index = None )
	
	

main()
	
	
	
	
	
	