import json
import os.path
import sqlite3
import time
import urllib.request
from datetime import datetime

import bs4 as bs
import requests

import constants as csts
import my_utils as mutils


class Scraper:
    def __init__(self, conn, curs, table_name="Stock"):
        self.conn = conn
        self.curs = curs
        self.table_name = table_name
        self.column_depth = None
        self.scrape_params = csts.stock_scrape_params
        self.columns = None

    def filter_and_convert(self, html_items, form_prms):
        splitindex_dict = {
            form_prms["split1"]: form_prms["index1"],
            form_prms["split2"]: form_prms["index2"],
        }

        item = mutils.format_with_splitindex(splitindex_dict)

        if datatype == float or datatype == int:
            if item.endswith("k"):
                item = datatype(float(item.replace("k", "")) * 1000)
            elif "M" in item:
                item = datatype(float(item.replace("M", "")) * 1000000)
            elif "B" in item:
                item = datatype(float(item.replace("B", "")) * 1000000000)
            elif "T" in item:
                item = datatype(float(item.replace("T", "")) * 1000000000000)
            elif (not "N/A" in item) and (not "-" in item):
                item = datatype(float(item))
            else:
                item = datatype(csts.unavailable_value)

        return filtered_item

    def get_soup(self, url):
        datestamp = datetime.strftime(datetime.now(), "%H:%M:%S")
        try:
            opened_url = urllib.request.urlopen(url)
        except Exception as e:
            print("-- Warning: Url {} failed to open.\rError message:".format(url), e)
            return None
        source = opened_url.read()
        soup = bs.BeautifulSoup(source, "lxml")
        return soup

    def get_datasets(self, soup, url):
        datasets = {}
        table_row_items = soup.find_all("tr")

        content = {}
        date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        for tr in table_row_items:
            tds = tr.findChildren("td", recursive=False)
            row_content = []
            for td in tds:
                item = self.filter_and_convert(html_items, filter_params)
                row_content.append(item)

            content[row_content.pop(0)] = row_content

        if not datasets:
            return None
        else:
            if len(self.columns) > 1:
                pass

        return datasets

    def add_dates(self, datasets, row_length):
        date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        dates = []
        for i in range(row_length):
            dates.append(date)

        datasets["Date"] = dates
        return datasets

    def enter_table(self, url, ticker):
        soup = self.get_soup(url)
        if not soup:
            return
        datasets = self.get_datasets(soup, url)
        if not datasets:
            print("-- Couldnt get any data for url: {}".format(url))
            return
        # print('\r\rdatasets:', datasets)

        sql_insert_command = mutils.get_sql_insert_command(
            self.columns, self.table_name
        )
        sql_select_components = mutils.get_sql_select_command(
            self.columns, self.table_name
        )
        # print('sql insert command:', sql_insert_command)
        for i in range(self.column_depth):
            table_row = [dataset[i] for dataset in datasets.values()]

            if ticker:
                table_row.append(ticker)

            sql_select_components = mutils.sql_row_entry(
                table_row,
                self.conn,
                self.curs,
                sql_insert_command,
                sql_select_components,
            )


def main(
    curs=None,
    conn=None,
    table_name_urls=csts.table_name_market_urls,
    stock_watchlist=[None],
    column_filter=None,
):
    if not curs or not conn:
        if db_path:
            conn = sqlite3.connect(db_path)
            curs = conn.cursor()
        else:
            print(
                "-- Warning: couldnt enter table because no database path or "
                "sql-connection was supplied."
            )

    scr = Scraper(conn, curs)
    for (table_name, url) in table_name_urls:
        scr.table_name = table_name
        scr.scrape_params = csts.scrape_param_lookup[url]
        scr.columns = mutils.get_columns_from_params(scr.scrape_params)
        if column_filter:
            scr.columns = mutils.filter_columns(scr.columns, column_filter)

        for ticker in stock_watchlist:
            print("Beginning scrape of url:", url.format(ticker))
            scr.enter_table(url.format(ticker), ticker)

        print('Entered data into table: "{}"'.format(table_name))


def create_tables(
    curs,
    table_name_urls=csts.table_name_market_urls,
    add_symbol=None,
    column_filter=None,
):
    for (table_name, url) in table_name_urls:
        scrape_params = csts.scrape_param_lookup[url]
        columns = mutils.get_columns_from_params(scrape_params)
        if column_filter:
            columns = mutils.filter_columns(columns, column_filter)

        mutils.create_db_table(table_name, columns, curs)


if __name__ == "__main__":
    db_file = "16_10_2020.db"
    conn = sqlite3.connect(db_file)
    curs = conn.cursor()

    create_tables(curs)
    main(curs, conn)
