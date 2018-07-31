#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
from astropy.time import Time
import numpy as np


def main():
	
	# czytaj i wyczyść dane oraz dodaj odpowiednie kolumny
	df = pd.read_fwf('gGPR1874.txt', header=None, names=["typ","YYYY","MM","DD","HH","mm","ss","NOAA","UmbraArea","SpotArea","CorUmbraArea","CorSpotArea","szerokosc","dlugosc","LongitudinalDistance","angle","Distance"])
	# poprawić dla GPR - więcej kolumn
	print(df.head(10))
	quit()
	df = df[(df[['szerokosc','dlugosc','LongitudinalDistance','angle','Distance']] != 999999).all(axis=1)].reset_index(drop=True)
	df = df.sort_values(by='ss') 
	#print(df.tail(10))
	
	#print(df.loc[df['ss'] == 60])

	# poprawka dla sekund = 60
	df.loc[df['ss'] == 60, "mm"] = df.loc[df['ss'] == 60, "mm"] + 1
	df.loc[df['ss'] == 60, "ss"] = 0
	#print("DD")
	#print(df.loc[df['ss'] == 0])
	#(df.loc[df['ss'] == 60])['mm'] = (df.loc[df['ss'] == 60])['mm'] + 1

	quit()
	
	df = df.sort_values(by='NOAA') 
	
	df['julianDay'] = df.apply(get_julian_day, axis=1)
	df['dlug*pow'] = df['dlugosc'] * df['CorSpotArea']
	df['szer*pow'] = df['szerokosc'] * df['CorSpotArea']
	df['miejsce_na_tarczy'] = (df['LongitudinalDistance'] +90)/180
	df['Carrington'] = get_carrington_rotation(df)

	# grupuj dane - wartości uśrednione dla danej grupy
	df_grouped = df.groupby('NOAA').agg({'YYYY': 'min', 'Carrington': 'min','miejsce_na_tarczy': ['min', 'max'],'dlugosc': ['min', 'max'],'szerokosc': ['min', 'max'],'julianDay': ['min', 'max'], 'CorSpotArea': 'sum', 'dlug*pow': 'sum', 'szer*pow': 'sum'})
	del(df)

	df_grouped['roznica_dlug'] = df_grouped['dlugosc']['max'] - df_grouped['dlugosc']['min']
	df_grouped['roznica_szer'] = df_grouped['szerokosc']['max'] - df_grouped['szerokosc']['min']
	df_grouped['sr_szer'] = df_grouped['szer*pow']['sum'] / df_grouped['CorSpotArea']['sum']
	df_grouped['sr_dlug'] = df_grouped['dlug*pow']['sum'] / df_grouped['CorSpotArea']['sum']

	# ustaw kolumny w odpowiedniej kolejności i zmień nagłówki 
	df_final = df_grouped
	del(df_grouped)
	
	df_final.columns = [' '.join(col).strip() for col in df_final.columns.values]
	df_final.reset_index(inplace=True)
	df_final = df_final[['YYYY min', 'Carrington min','NOAA','julianDay min','julianDay max','CorSpotArea sum','sr_dlug','sr_szer','miejsce_na_tarczy min','miejsce_na_tarczy max','dlugosc min','dlugosc max','roznica_dlug','szerokosc min','szerokosc max','roznica_szer']]
	df_final.columns = ['rok', 'rotacja Carringtona', 'nr grupy','czas pojawienia','czas konca','powierzchnia sum.','wazona dlugosc','wazona szerokosc','moment pojawienia','moment konca','min. dlugosc','maks. dlugosc','zakres dlugosci','min. szerokosc','maks. szerokosc','zakres szerokosci']

	
	# walidacja danych
	df_rows = df_final.shape[0]
	for i in range(df_rows):
		noaa = df_final.at[i,'nr grupy']
		powierzchnia = df_final.at[i,'powierzchnia sum.']
		moment_pojawienia = df_final.at[i,'moment pojawienia']
		moment_konca = df_final.at[i,'moment konca']
		dlugosc_min = df_final.at[i,'min. dlugosc']
		dlugosc_maks = df_final.at[i,'maks. dlugosc']
		szerokosc_min = df_final.at[i,'min. szerokosc']
		szerokosc_maks = df_final.at[i,'maks. szerokosc']
		dlugosc_zakres = df_final.at[i,'zakres dlugosci']
		szerokosc_zakres = df_final.at[i,'zakres szerokosci']
		
		if powierzchnia < 0 or powierzchnia >= 999999:
			print("Niepoprawne dane - sumaryczna powierzchnia: ", powierzchnia, " dla grupy: ", noaa)
			quit()
		elif moment_pojawienia < 0 or moment_pojawienia > 1:
			print("Niepoprawne dane - miejsce pojawienia na tarczy: ", moment_pojawienia, " dla grupy: ", noaa)
			quit()
		elif moment_konca < 0 or moment_konca > 1:
			print("Niepoprawne dane - miejsce zaniku na tarczy: ", moment_konca, " dla grupy: ", noaa)
			quit()
		elif dlugosc_min < 0 or dlugosc_min > 360:
			print("Niepoprawne dane - długość heliograficzna: ", dlugosc_min, " dla grupy: ", noaa)
			quit()
		elif dlugosc_maks < 0 or dlugosc_maks > 360:
			print("Niepoprawne dane - długość heliograficzna: ", dlugosc_maks, " dla grupy: ", noaa)
			quit()
		elif szerokosc_min < -180 or szerokosc_min > 180:
			print("Niepoprawne dane - szerokość heliograficzna: ", szerokosc_min, " dla grupy: ", noaa)
			quit()
		elif szerokosc_maks < -180 or szerokosc_maks > 180:
			print("Niepoprawne dane - szerokość heliograficzna: ", szerokosc_maks, " dla grupy: ", noaa)
			quit()
		elif dlugosc_zakres < 0 or dlugosc_zakres > 360:
			print("Niepoprawne dane - długość heliograficzna: ", dlugosc_maks, " dla grupy: ", noaa)
			quit()
		elif szerokosc_zakres < 0 or szerokosc_zakres > 360:
			print("Niepoprawne dane - szerokość heliograficzna: ", szerokosc_maks, " dla grupy: ", noaa)
			quit()
		
		
	df_final.to_csv('output1.txt', sep='	', header = None, index = None)



def get_julian_day(date):
	# wyznacz dzień juliański dla danej daty
	year = date['YYYY']
	month = date['MM']
	day = date['DD']
	hour = date['HH']
	minute = date['mm']
	second = date['ss']
	time = Time(datetime(year, month, day, hour, minute, second), scale='utc')
	return time.jd





def get_carrington_rotation(x):
	# wyznacz nr rotacji Carringtona dla danego dnia juliańskiego
	nr_rotacji = []
	df_rows = x.shape[0]
	rotations = []
	julian_days = []
	#print(df_rows)
	input_file = open('carrington.txt','r')
	for row in input_file:
		data = row.split("\t")
		rotation = int(data[0])
		julian_day = float(data[1])
		rotations.append(rotation)
		julian_days.append(julian_day)
	input_file.close()

	for i in range(df_rows):
		#print(i)
		current_julian_day = x.at[i,'julianDay']

		for julian_day in julian_days:
			if julian_day >= current_julian_day:
				current_rotation = rotations[julian_days.index(julian_day)-1]
				break

		nr_rotacji.append(current_rotation)
		
	del(rotations,julian_days,df_rows)
	return nr_rotacji
	
main()


