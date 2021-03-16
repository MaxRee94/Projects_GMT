import sqlite3

import constants as csts
import my_utils as mutils
import rtprice_scraper_v03 as rtscraper


class Watchlist:

	def __init__(self, conn, curs):
		self.conn = conn
		self.curs = curs

	def update_watchlist(self):
		rtscraper.main(self.curs, self.conn, 
					   column_filter=['Symbol'])


def read(table_name, watchlist_path=csts.watchlist_db_path):
	conn = sqlite3.connect(watchlist_path)
	curs = conn.cursor()

	existing_tickers = mutils.read_from_db(curs, table_name)
	curs.close()
	conn.close()

	return existing_tickers

def update(watchlist_path=csts.watchlist_db_path):
	conn = sqlite3.connect(watchlist_path)
	curs = conn.cursor()
	wl = Watchlist(conn, curs)
	
	rtscraper.create_tables(curs, column_filter=['Symbol'])

	wl.update_watchlist()

	curs.close()
	conn.close()

if __name__ == '__main__':
	update()
