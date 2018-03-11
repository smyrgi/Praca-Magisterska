#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
from astropy.time import Time
import numpy as np


def main():
	
	# czytaj i wyczyśc dane oraz dodaj odpowiednie kolumny
	df = pd.read_fwf('gDPD1993.txt', header=None, names=["typ","YYYY","MM","DD","HH","mm","ss","NOAA","UmbraArea","SpotArea","CorUmbraArea","CorSpotArea","szerokosc","dlugosc","LongitudinalDistance","angle","Distance"])
	df = df.sort_values(by='NOAA') 

	df['julianDay'] = df.apply(julian_day, axis=1)
	df['dlug*pow'] = df['dlugosc'] * df['CorSpotArea']
	df['szer*pow'] = df['szerokosc'] * df['CorSpotArea']
	df['miejsce_na_tarczy'] = (df['LongitudinalDistance'] +90)/180
	df['Carrington'] = carrington_rotation(df)

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

	print(df_final.head(5))



def julian_day(x):
	# wyznacz dzień juliański dla danej daty
	year = x['YYYY']
	month = x['MM']
	day = x['DD']
	hour = x['HH']
	minute = x['mm']
	second = x['ss']
	t = Time(datetime(year, month, day, hour, minute, second), scale='utc')
	return t.jd

def carrington_rotation(x):
	# wyznacz nr rotacji Carringtona dla danego dnia juliańskiego
	inputFile = open('carrington.txt','r')
	nr_rotacji = []
	df_rows = x.shape[0]
	listRotacje = []
	listDni = []
	
	for row in inputFile:
		data = row.split("\t")
		rozpoczeta_rotacja = int(data[0])
		dzien_rozpoczecia = float(data[1])
		listRotacje.append(rozpoczeta_rotacja)
		listDni.append(dzien_rozpoczecia)
	inputFile.close()

	for i in range(df_rows):
		julianday = x.at[i,'julianDay']

		for dzien in listDni:
			if dzien >= julianday:
				rotacja = listRotacje[listDni.index(dzien)-1]
				break

		nr_rotacji.append(rotacja)
		
	del(listRotacje,listDni,df_rows)
	return nr_rotacji

main()


