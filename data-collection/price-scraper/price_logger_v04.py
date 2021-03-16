from datetime import datetime, timedelta
import sqlite3
import time
import random
import os

import rtprice_scraper_v03 as rtscraper
import constants as csts
import my_utils as mutils
import watchlist
import product_data


class Logger:
	def __init__(self, db_fpath=csts.market_db_fpath):
		self.failed_tickers = []
		self.log = {}
		self.conn = sqlite3.connect(db_fpath)
		self.curs = self.conn.cursor()

	def update_minute_res_data(self, table_name_urls=csts.table_name_market_urls):
		pdata = product_data.main()
		previous_table_name = None
		#table_name_urls = {table_name:url for table_name, url in table_name_urls}
		for (table_name, url) in table_name_urls:
			print('\r-- Getting data for "{}"'.format(table_name))
			tickers = watchlist.read(table_name)
			scrape_params = csts.scrape_param_lookup[url]
			columns = mutils.get_columns_from_params(scrape_params)

			sql_insert_command = mutils.get_sql_insert_command(columns, table_name)
			sql_select_components = mutils.get_sql_select_command(columns, table_name)
			time = None
			for i, ticker in enumerate(tickers):
				# if i > 3:
				# 	exit()

				product = pdata.get_product(ticker)
				if product:
					minute_res_data, time = pdata.update_dhist(ticker=ticker, product_id=product.id, time=time)
				else:
					continue

				if minute_res_data:
					#print('minute res data:', minute_res_data)
					for date, price in minute_res_data.items():
						row = [ticker, price, csts.unavailable_value, date]
						sql_select_components = mutils.sql_row_entry(row, self.conn, self.curs, 
																	 sql_insert_command, sql_select_components)

	

def update_minute_res_data():
	logger = Logger()
	rtscraper.create_tables(logger.curs)
	logger.update_minute_res_data()

	return logger

def update_slow_daily_data():
	logger = Logger(db_fpath=csts.slow_daily_db_path)
	scrape_params = csts.statistics_scrape_params
	columns = mutils.get_columns_from_params(scrape_params)
	stock_watchlist = watchlist.read('Stock')
	rtscraper.create_tables(logger.curs, table_name_urls=csts.table_name_slowdaily_urls)
	rtscraper.main(logger.curs, logger.conn, table_name_urls=csts.table_name_slowdaily_urls,
				   stock_watchlist=stock_watchlist)
	return logger

def update_high_freq_data():
	logger = Logger()
	rtscraper.create_tables(logger.curs)

	interrupt = False
	time = datetime.now()
	while True:
		if interrupt or time.weekday() >= 5 or time.hour < 15 or time.hour >= 22:
			exit()
		elif time.hour == 15:
			if time.minute < 30:
				exit()

		time = datetime.now()
		rtscraper.main(logger.curs, logger.conn)
		print('\r-- High-frequency data entered. Duration:', (datetime.now() - time))
		start = False

	return logger

if __name__ == '__main__':
	#watchlist.update()
	#logger = update_slow_daily_data()
	#logger = update_minute_res_data()

	logger = update_high_freq_data()
	logger.curs.close()
	logger.conn.close()
