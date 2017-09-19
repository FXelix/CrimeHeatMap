import csv
import time

import gmplot
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait


def create_data_frame(csv_file_name, years):
	with open(csv_file_name, 'r') as file_in, open('crime_locations.csv', 'w') as  file_out:
		reader = csv.reader(file_in)
		writer = csv.writer(file_out)
		headers = next(reader)
		count = 0
		for row in reader:
			if row[19] and row[17] in years:
				count += 1
				writer.writerow(row)
		print(f'{count} rows added')
	data = pd.read_csv('crime_locations.csv', chunksize=10000, names=headers)
	df = pd.concat(data, ignore_index=True)
	df = df.rename(columns={'Primary Type': 'Type'})
	df['Date'] = pd.to_datetime(df.Date)
	df = df.sort_values('Date')
	return df


def filter_data_by_year(df, year):
	next_year = year + 1
	data = df.query(f'datetime.datetime({next_year},1,1) > Date > datetime.datetime({year},1,1)')
	return data


def filter_data_by_month(df, year, month):
	next_month = month + 1
	if next_month != 13:
		data = df.query(f'datetime.datetime({year},{next_month},1) > Date > datetime.datetime({year},{month},1)')
	else:
		next_year = year + 1
		data = df.query(f'datetime.datetime({next_year},1,1) > Date > datetime.datetime({year},{month},1)')

	return data


def get_lat_long(dataframe):
	lat_long = (dataframe[dataframe.Latitude.notnull()])
	lats = lat_long['Latitude'].tolist()
	longs = lat_long['Longitude'].tolist()
	return (lats, longs)


def generate_map(lats, longs, map_name):
	my_map = gmplot.GoogleMapPlotter(41.8486592, -87.707648, 11)
	my_map.heatmap(lats, longs, radius=16)
	my_map.draw(f'/Users/Dave/Desktop/PythonProjects/CrimeHeatMap/html_files/{map_name}.html')
	print('html file saved')
	return map_name


def open_map(map_name, browser):
	url = f'file:///Users/Dave/Desktop/PythonProjects/CrimeHeatMap/html_files/{map_name}.html'
	browser.get(url)
	file_loaded = '//*[@id="map_canvas"]/div/div/div[10]/div[2]/div[1]'
	WebDriverWait(browser, 10).until(lambda driver: driver.find_element_by_xpath(file_loaded))
	time.sleep(5)
	browser.save_screenshot(f'/Users/Dave/Desktop/PythonProjects/CrimeHeatMap/png_images/{map_name}.png')


def run(start_year, end_year, csv_file_name):
	years = [str(year) for year in range(start_year, end_year)]
	df = create_data_frame(csv_file_name, years)
	names = []
	browser = webdriver.Chrome()
	for year in range(start_year, end_year):
		for month in range(1, 13):
			annual_data = filter_data_by_month(df, year, month)
			lats, longs = get_lat_long(annual_data)
			names.append(generate_map(lats, longs, (f'{year} - {month}')))
	for map_name in names:
		open_map(map_name, browser)


year_range = []
for i in range(2000, 2017, 4):
	my_tup = (i, i + 4)
	year_range.append(my_tup)
for year in year_range:
	run(year[0], year[1], 'Crime.csv')
	print(f'{year[0]} to {year[1]} has been processed')
