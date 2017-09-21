import csv
import time

import gmplot.gmplot.gmplot as gmplot
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from PIL import Image, ImageDraw, ImageFont



def create_data_frame(csv_file_name, years, filter1 = True, filter2 = True):
	# creates crime_locations.csv with data for specific year to increase performance
	with open(csv_file_name, 'r') as file_in, open('crime_locations.csv', 'w') as  file_out:
		reader = csv.reader(file_in)
		writer = csv.writer(file_out)
		headers = next(reader)
		count = 0
		for row in reader:
			if row[19] and row[17] in years and (row[5] == filter1 or row[5] == filter2):
				count += 1
				writer.writerow(row)
		print(f'{count} rows added')
	data = pd.read_csv('crime_locations.csv', chunksize=10000, names=headers)
	df = pd.concat(data, ignore_index=True)
	df = df.rename(columns={'Primary Type': 'Type'})
	df['Date'] = pd.to_datetime(df.Date)
	return df


def filter_data_by_month(df, year, month,agg):
	# takes year-range dataframe and breaks it down into month
	next_month = month + 1
	if next_month != 13:
		# error handling for December/January
		data = df.query(f'datetime.datetime({year},{next_month},1) > Date > datetime.datetime({year},{month},1)')
	else:
		next_year = year + 1
		data = df.query(f'datetime.datetime({next_year},1,1) > Date > datetime.datetime({year},{month},1)')
	agg[f'{year} - {month}'] = len(data)
	return (data,agg)


def get_lat_long(dataframe):
	# coverts dataframe lat/longs into lists
	lat_long = (dataframe[dataframe.Latitude.notnull()])
	lats = lat_long['Latitude'].tolist()
	longs = lat_long['Longitude'].tolist()
	return (lats, longs)


def generate_map(lats, longs, map_name):
	# draws map and saves .html file
	my_map = gmplot.GoogleMapPlotter(41.8486592, -87.707648, 11)
	my_map.heatmap(lats, longs,radius=16,maxIntensity=40)
	my_map.draw(f'html_files/{map_name}.html')
	return map_name


def open_map(map_name, browser):
	# opens map in selenium browser and saves screenshot as year-month.png
	url = f'file:///Users/Dave/Desktop/PythonProjects/CrimeHeatMap/html_files/{map_name}.html'
	browser.get(url)
	file_loaded = '//*[@id="map_canvas"]/div/div/div[10]/div[2]/div[1]'
	WebDriverWait(browser, 10).until(lambda driver: driver.find_element_by_xpath(file_loaded))
	time.sleep(5)
	browser.save_screenshot(f'assault_battery_images/A_B_{map_name}.png')


def run(start_year, end_year, csv_file_name,filter1,filter2):
	years = [str(year) for year in range(start_year, end_year)]
	df = create_data_frame(csv_file_name, years,filter1,filter2)
	names = []
	browser = webdriver.PhantomJS()
	browser.set_window_size(1024, 768)
	aggregate_crime_numbers = {}
	# iterates through months in years
	for year in range(start_year, end_year):
		for month in range(1, 13):
			# convert monthly datarance flat-file to dataframe
			monthly_data, agg = filter_data_by_month(df, year, month,aggregate_crime_numbers)
			# get lat/longs for that month as lists
			lats, longs = get_lat_long(monthly_data)
			# generates .html map file and adds map name to names list
			names.append(generate_map(lats, longs, (f'{year} - {month}')))
			image_name = f'{year} - {month}'
			add_filename(image_name,agg)
	for map_name in names:
		# iterates through saved maps (names), generating a map screenshot for each month
		open_map(map_name, browser)


def add_filename(image_name,agg):
	im = Image.open(f'png_images/{image_name}.png')
	draw = ImageDraw.Draw(im)
	font = ImageFont.truetype('abel-regular.ttf',30)
	draw.text((700,250),f'{image_name}',(0,0,0),font=font)
	draw.text((700, 200), f'Reports: {agg[image_name]}', (0, 0, 0), font=font)
	draw.text((700, 150), 'Assualt & Battery', (0, 0, 0), font=font)
	im.save(f'assault_battery_images/dated/ ({image_name}).png')


year_range = []
for i in range(2001, 2017, 1):
	year_group = (i, i + 1)
	year_range.append(year_group)


if __name__ == "__main__":
	for year in year_range:
		run(year[0], year[1], 'Crime.csv','ASSAULT','BATTERY')
		print(f'{year[0]} to {year[1]} has been processed')

