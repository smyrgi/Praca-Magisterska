#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
from astropy.time import Time
from scipy.stats import t
import numpy as np
import math

def calculate_q(questionable_record, closest_record, data_range):
	gap = abs(questionable_record - closest_record)
	Q_dixon = gap / data_range
	return Q_dixon
	

	
def remove_outliner(coordinate, group_data, removed_record):
	group_data_clear = group_data.drop(group_data.index[removed_record])
	t_student_result = t_student_test(coordinate, group_data, group_data_clear, removed_record)
	if (t_student_result == "Pass"):
		return group_data_clear, None
	return group_data, t_student_result
	
	
	
	
	
def t_student_test(coordinate, group_data, group_data_clear,removed_record):
	#group_data = [17.0, 17.1, 17.1, 17.2, 17.2, 17.3, 17.3, 17.4, 17.5, 16.4]
	#group_data_clear = [17.0, 17.1, 17.1, 17.2, 17.2, 17.3, 17.3, 17.4, 17.5]
	#removed_value = 16.4
	removed_value = group_data.at[removed_record,coordinate]
	n = len(group_data)
	
	mean = np.mean(list(group_data_clear[coordinate]))
	t_critical = t.ppf(1-0.025, n-2)
	s = np.std(list(group_data_clear[coordinate]))
	
	g_min = mean - t_critical * math.sqrt(n/(n-2))*s
	g_max = mean + t_critical * math.sqrt(n/(n-2))*s
	
	if (removed_value < g_min or removed_value > g_max):
		return "Pass"
	
	return "Fail"

		
def main():
	coordinate = 'Latitude'
	#coordinate = 'Longitude'
	file_name_limit_exceded = 'alldataDPD_latitudelimit'
	#file_name_limit_exceded = 'alldataDPD_longitudelimit'
	file_name_daily = 'alldataDPD_clear'
	input_file_name_limit_exceded = file_name_limit_exceded + '.txt'
	input_file_name_daily = file_name_daily + '.txt'

	columns_names = ['Year', 'CarringtonRotation', 'NOAA','StartJulianDay','EndJulianDay','TotalGroupArea',
							   'WeightedLongitude', 'WeightedLatitude','StartPosition','EndPosition','MinLongitude',
							   'MaxLongitude','LongitudeRange', 'MinLatitude','MaxLatitude','LatitudeRange']

	sunspot_data_exceded = pd.read_table(input_file_name_limit_exceded, header=None, names=columns_names)
	sunspot_data_daily = pd.read_table(input_file_name_daily, header=0)

	noaa_exceded = list(sunspot_data_exceded['NOAA'])
	data_check_manually = []
	group_check_manually = []

	for group in noaa_exceded:
		group_data = sunspot_data_daily.loc[sunspot_data_daily['NOAA'] == group]
		group_data_sorted = group_data.sort_values(by=[coordinate])
		group_data_sorted = group_data_sorted.reset_index(drop=True)
		records_number = len(group_data)
	
		if records_number < 3: 
			group_data_sorted_fixed = [group_data.drop(group_data.index[record]) for record in range(records_number)]
		else:
			removed_record, ind_remove_outliner = check_outliner_with_dixon_q_test(coordinate, group_data_sorted, records_number)

			if (ind_remove_outliner):
				group_data_sorted_fixed, result_t_test = remove_outliner(coordinate, group_data_sorted, removed_record)

				if (result_t_test == "Fail"): 
					data_check_manually.append(group_data)		
					group_check_manually.append(group)
			else:
				data_check_manually.append(group_data)
				group_check_manually.append(group)
	
	print(group_check_manually, len(group_check_manually))

		
def check_outliner_with_dixon_q_test(coordinate, group_data_sorted, records_number):
	global dixon_q95_table 
	
	min_value = group_data_sorted.at[0,coordinate]
	max_value = group_data_sorted.at[records_number-1,coordinate]
	data_range = max_value - min_value 
	min_q = calculate_q(min_value, group_data_sorted.at[1,coordinate], data_range)
	max_q = calculate_q(max_value, group_data_sorted.at[records_number-2,coordinate], data_range)

	if (min_q > max_q):
		removed_record = 0
		final_q = min_q
	else:
		removed_record = records_number-1
		final_q = max_q

	critical_q =  dixon_q95_table[records_number]
	if (final_q > critical_q):
		ind_remove_outliner = True
	else:
		ind_remove_outliner = False
		
	return removed_record, ind_remove_outliner
	
	
dixon_q95_values = [0.97, 0.829, 0.71, 0.625, 0.568, 0.526, 0.493, 0.466, 0.444, 0.426, 0.41, 0.396, 0.384, 0.374, 
					0.365, 0.356, 0.349, 0.342, 0.337, 0.331, 0.326, 0.321, 0.317, 0.312, 0.308, 0.305, 0.301, 0.29]
dixon_q95_table = {n:q for n,q in zip(range(3,len(dixon_q95_values)+1), dixon_q95_values)}

main()
	
	
	
	
	
	