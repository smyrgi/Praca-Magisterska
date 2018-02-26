#!/usr/bin/env python2

import pandas as pd
from datetime import datetime
from astropy.time import Time
import numpy as np

def main():
	
	df = pd.read_fwf('gDPD1993.txt', header=None, names=["typ","YYYY","MM","DD","HH","mm","ss","NOAA","UmbraArea","SpotArea","CorUmbraArea","CorSpotArea","szerokosc","dlugosc","LongitudinalDistance","angle","Distance"])
	#print (df.head(10))

	df = df.sort_values(by='NOAA') 
	#print (df.head(10))

	df['julianDay'] = df.apply(julian_day, axis=1)
	#df['three'] = df['one'] * df['two']
	df['dlug*pow'] = df['dlugosc'] * df['CorSpotArea']
	df['szer*pow'] = df['szerokosc'] * df['CorSpotArea']
	df['miejsce_na_tarczy'] = (df['LongitudinalDistance'] +90)/180
	df['Carrington'] = carrington_rotation(df)
		
	#print (df.head(10))
	
     	
	#print (df.head(10))

	#print (df.at[0,'J3'])  



	#df_filtered = df.query('NOAA== 7379 ')
	#print(df_filtered)
	#print("AA")
	#print(df.groupby('NOAA')['julianDay']['SpotArea'].min().sum())	

	#df_grouped = df.groupby('NOAA')
	#df.groupby('A').agg({'B': ['min', 'max'], 'C': 'sum'})
	df_grouped = df.groupby('NOAA').agg({'YYYY': 'min', 'Carrington': 'min','miejsce_na_tarczy': ['min', 'max'],'dlugosc': ['min', 'max'],'szerokosc': ['min', 'max'],'julianDay': ['min', 'max'], 'CorSpotArea': 'sum', 'dlug*pow': 'sum', 'szer*pow': 'sum'})
	del(df)

	df_grouped['roznica_dlug'] = df_grouped['dlugosc']['max'] - df_grouped['dlugosc']['min']
	df_grouped['roznica_szer'] = df_grouped['szerokosc']['max'] - df_grouped['szerokosc']['min']
	df_grouped['sr_szer'] = df_grouped['szer*pow']['sum'] / df_grouped['CorSpotArea']['sum']
	df_grouped['sr_dlug'] = df_grouped['dlug*pow']['sum'] / df_grouped['CorSpotArea']['sum']

	df_final = df_grouped
	del(df_grouped)
	
	df_final.columns = [' '.join(col).strip() for col in df_final.columns.values]
	df_final.reset_index(inplace=True)
	df_final = df_final[['YYYY min', 'Carrington min','NOAA','julianDay min','julianDay max','CorSpotArea sum','sr_dlug','sr_szer','miejsce_na_tarczy min','miejsce_na_tarczy max','dlugosc min','dlugosc max','roznica_dlug','szerokosc min','szerokosc max','roznica_szer']]
	df_final.columns = ['rok', 'rotacja Carringtona', 'nr grupy','czas pojawienia','czas konca','powierzchnia sum.','wazona dlugosc','wazona szerokosc','moment pojawienia','moment konca','min. dlugosc','maks. dlugosc','zakres dlugosci','min. szerokosc','maks. szerokosc','zakres szerokosci']

	print(df_final.head(5))

	
def julian_day(x):
	year = x['YYYY']
	month = x['MM']
	day = x['DD']
	hour = x['HH']
	minute = x['mm']
	second = x['ss']
	t = Time(datetime(year, month, day, hour, minute, second), scale='utc')
	return t.jd

def carrington_rotation(x):
	#rotacjeCarr = {}
	inputFile = open('carrington.txt','r')
	nr_rotacji = []
	df_rows = x.shape[0]
	listRotacje = []
	listDni = []
	
	for row in inputFile:
		data = row.split("\t")
		rozpoczeta_rotacja = int(data[0])
		dzien_rozpoczecia = float(data[1])
		#rotacjeCarr[dzien_rozpoczecia] = rozpoczeta_rotacja
		listRotacje.append(rozpoczeta_rotacja)
		listDni.append(dzien_rozpoczecia)
	inputFile.close()

	#rotacjeCarr_sorted = sorted(rotacjeCarr)
	for i in range(df_rows):
		julianday = x.at[i,'julianDay']

		"""
		for dzien in rotacjeCarr_sorted:
			if dzien < julianday:
				rotacja = rotacjeCarr[dzien]
			else:
				break
		"""
		for dzien in listDni:

			if dzien >= julianday:
				rotacja = listRotacje[listDni.index(dzien)-1]
				break

		nr_rotacji.append(rotacja)
	del(listRotacje,listDni,df_rows)
	#del(rotacjeCarr)
	return nr_rotacji

main()








