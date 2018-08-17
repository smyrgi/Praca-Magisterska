#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
from astropy.time import Time
from scipy.stats import t
import numpy as np
import math

		
def main():
	file_name_limit_exceded_latitude = 'alldataDPD_latitudelimit2'
	file_name_limit_exceded_longitude = 'alldataDPD_longitudelimit2'
	file_name_daily = 'alldataDPD_clear'
	output_file_manually_groups = 'checkmanually_groups.txt'
	output_file_manually_data = 'checkmanually_data.txt'

	input_file_name_daily = file_name_daily + '.txt'
	sunspot_data_daily = pd.read_table(input_file_name_daily, header=0)
	sunspot_data_fixed = sunspot_data_daily
		
	sunspot_data_fixed, groups_check_manually_longitude = fix_exceeded_data(coordinate = 'Longitude', sunspot_data = sunspot_data_fixed, 
																			file_name = file_name_limit_exceded_longitude)
	sunspot_data_fixed, groups_check_manually_latitude = fix_exceeded_data(coordinate = 'Latitude', sunspot_data = sunspot_data_fixed, 
																		   file_name = file_name_limit_exceded_latitude)
	
	print('groups_check_manually_longitude', len(groups_check_manually_longitude))
	print('groups_check_manually_latitude', len(groups_check_manually_latitude))
	
	print(len(set(groups_check_manually_longitude + groups_check_manually_latitude)))
	
	groups_check_manually = set(groups_check_manually_longitude + groups_check_manually_latitude)
	
	groups_check_manually = list(groups_check_manually)
	groups_check_manually.sort()
	with open(output_file_manually_groups, 'w') as ofile:
		ofile.write('\n'.join(groups_check_manually))
	
	
	columns_names_daily = ['DataType', 'YYYY', 'MM', 'DD', 'HH', 'mm', 'ss', 'NOAA', 'UmbraArea', 'WholeSpotArea', 'CorrectedUmbraArea', 
						   'CorrectedWholeSpotArea', 'Latitude', 'Longitude', 'LongitudinalDistance', 'PositionAngle', 'DistanceFromCentre', 
						   'JulianDay', 'Longitude*Area', 'Latitude*Area', 'PositionOnDisk', 'CarringtonRotation']
	
	data_check_manually = sunspot_data_daily.loc[sunspot_data_daily['NOAA'].isin(list(groups_check_manually))]
	data_check_manually = data_check_manually.sort_values(by='NOAA')
	data_check_manually.to_csv( output_file_manually_data, sep='	', header = columns_names_daily, index = None )
	
	

	
def fix_exceeded_data(coordinate, sunspot_data, file_name):
	groups_check_manually = []
	noaa_exceded = get_groups_exceeded_limit(file_name)
	for group in noaa_exceded:
		validation_result, value_to_remove = validate_exceeded_data(coordinate, sunspot_data, group)
		if (validation_result == 'remove group data'):
			sunspot_data = sunspot_data[(sunspot_data['NOAA'] != group)]
		elif (validation_result == 'remove value'):
			sunspot_data = sunspot_data[(sunspot_data['NOAA'] != group) | (sunspot_data[coordinate] != value_to_remove)]
		elif (validation_result == 'check manually'):
			groups_check_manually.append(group)
	return sunspot_data, groups_check_manually
	
	
			
def get_groups_exceeded_limit(file_name):	
	input_file_name = file_name + '.txt'
	columns_names = ['Year', 'CarringtonRotation', 'NOAA','StartJulianDay','EndJulianDay','TotalGroupArea',
							   'WeightedLongitude', 'WeightedLatitude','StartPosition','EndPosition','MinLongitude',
							   'MaxLongitude','LongitudeRange', 'MinLatitude','MaxLatitude','LatitudeRange']

	sunspot_data_exceded = pd.read_table(input_file_name, header=None, names=columns_names)

	return list(sunspot_data_exceded['NOAA'])
	
	
def validate_exceeded_data(coordinate, sunspot_data_daily, group):
	group_data = sunspot_data_daily.loc[sunspot_data_daily['NOAA'] == group]
	group_data_sorted = group_data.sort_values(by=[coordinate])
	group_data_sorted = group_data_sorted.reset_index(drop=True)
	records_number = len(group_data)

	if records_number < 3: 
		return 'remove group data', None
		group_data_sorted_fixed = [group_data.drop(group_data.index[record]) for record in range(records_number)]
	else:
		value_to_remove = test_outliners(coordinate, group_data_sorted, records_number)
		if (value_to_remove):
			return 'remove value', value_to_remove
		else:
			return 'check manually', None
	
	
	
def test_outliners(coordinate, group_data_sorted, records_number):
	record_to_remove, ind_remove_outliner = check_outliner_with_dixon_q_test(coordinate, group_data_sorted, records_number)
	
	if (ind_remove_outliner):
		value_to_remove = group_data_sorted.at[record_to_remove,coordinate]
		#result_t_test, value_to_remove = remove_outliner(coordinate, group_data_sorted, record_to_remove)
		#print (record_to_remove,value_to_remove)
		return value_to_remove
		if (result_t_test == 'Pass'): 
			return value_to_remove
				
	
		
def check_outliner_with_dixon_q_test(coordinate, group_data_sorted, records_number):
	global dixon_q95_table 
	
	min_value = group_data_sorted.at[0,coordinate]
	max_value = group_data_sorted.at[records_number-1,coordinate]
	data_range = max_value - min_value 
	min_q = calculate_q(min_value, group_data_sorted.at[1,coordinate], data_range)
	max_q = calculate_q(max_value, group_data_sorted.at[records_number-2,coordinate], data_range)

	if (min_q > max_q):
		record_to_remove = 0
		final_q = min_q
	else:
		record_to_remove = records_number-1
		final_q = max_q

	critical_q =  dixon_q95_table[records_number]
	if (final_q > critical_q):
		ind_remove_outliner = True
	else:
		ind_remove_outliner = False
	#print (min_q,max_q,critical_q)
	return record_to_remove, ind_remove_outliner
	
	
def calculate_q(questionable_record, closest_record, data_range):
	gap = abs(questionable_record - closest_record)
	Q_dixon = gap / data_range
	return Q_dixon
	

	
def remove_outliner(coordinate, group_data, record_to_remove):
	global testi, testj
	testi = testi +1
	### validate if outliner should be removed
	group_data_clear = group_data.drop(group_data.index[record_to_remove])
	t_student_result, removed_value = t_student_test(coordinate, group_data, group_data_clear, record_to_remove)
	#print('test:',testi)
	if (t_student_result == 'Pass'):
		testj = testj +1 
		#print('pass:', testj)
		#return group_data_clear, None
		return t_student_result, removed_value 
	return t_student_result, None
	
	
def t_student_test(coordinate, group_data, group_data_clear,record_to_remove):
	#group_data = [17.0, 17.1, 17.1, 17.2, 17.2, 17.3, 17.3, 17.4, 17.5, 16.4]
	#group_data_clear = [17.0, 17.1, 17.1, 17.2, 17.2, 17.3, 17.3, 17.4, 17.5]
	#removed_value = 16.4
	removed_value = group_data.at[record_to_remove,coordinate]
	n = len(group_data)
	
	mean = np.mean(list(group_data_clear[coordinate]))
	t_critical = t.ppf(1-0.025, n-2)
	s = np.std(list(group_data_clear[coordinate]))
	
	g_min = mean - t_critical * math.sqrt(n/(n-2))*s
	g_max = mean + t_critical * math.sqrt(n/(n-2))*s
	
	if (removed_value < g_min or removed_value > g_max):
		return 'Pass', removed_value
	
	return 'Fail', None


	
dixon_q95_values = [0.97, 0.829, 0.71, 0.625, 0.568, 0.526, 0.493, 0.466, 0.444, 0.426, 0.41, 0.396, 0.384, 0.374, 
					0.365, 0.356, 0.349, 0.342, 0.337, 0.331, 0.326, 0.321, 0.317, 0.312, 0.308, 0.305, 0.301, 0.29]
dixon_q95_table = {n:q for n,q in zip(range(3,len(dixon_q95_values)+1), dixon_q95_values)}

testi = 0
testj = 0
		  
main()
	
	
	
	
	
	