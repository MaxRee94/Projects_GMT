import os.path


pf_base_dir = os.path.normpath('E:/Algo/v1/pf_database')
pf_db_default = [{'id': '15694498', 'positionType': 'CASH', 'value': 10000.0}]
pf_db_filename = 'pf_database_v{}.json'

order_db_default = []
order_base_dir = os.path.normpath('E:/Algo/v1/order_database')
order_db_filename = 'order_database_v{}.json'

pricelog_fullpath = os.path.normpath('E:/Algo/v1/price_log/pricelog_database.json')
pricelog_fullpath_backup_pc = os.path.normpath('E:/Algo/v1/price_log/pricelog_database_backup_pc.json')
market_db_fpath = os.path.normpath('E:/Algo/v1/market_database/market_database.db')
watchlist_db_path = os.path.normpath('E:/Algo/v1/watchlist_database/watchlist_database.db')
slow_daily_db_path = os.path.normpath('E:/Algo/v1/slow_daily_database/slow_daily_database.db')

yahoo_active_url = 'https://finance.yahoo.com/most-active?offset=0&count=100'
yahoo_gainers_url = 'https://finance.yahoo.com/gainers?offset=0&count=100'
yahoo_losers_url = 'https://finance.yahoo.com/losers?offset=0&count=100'
yahoo_etf_url = 'https://finance.yahoo.com/etfs?offset=0&count=100'
yahoo_futures_url = 'https://finance.yahoo.com/commodities'
yahoo_indices_url = 'https://finance.yahoo.com/world-indices'
yahoo_currencies_url = 'https://finance.yahoo.com/currencies'
#yahoo_watchlist_url = 'https://finance.yahoo.com/portfolio/p_0/view' #doesnt work (need to be logged in but can't)
yahoo_asset_valuation_url = 'https://finance.yahoo.com/quote/{0}/key-statistics?p={0}'

unavailable_value = 9999999

table_name_market_urls = [
	('ETFs', yahoo_etf_url),
	('Stock', yahoo_active_url),
	('Stock', yahoo_gainers_url),
	('Stock', yahoo_losers_url),
	('Indices', yahoo_indices_url),
	('Currencies', yahoo_currencies_url),
	('Futures', yahoo_futures_url)
]
table_name_slowdaily_urls = [
	('Stock', yahoo_asset_valuation_url)
]

stock_scrape_params = {
	'html_params':{
		'Symbol': {
			'sql_datatype':'TEXT',
			'split1':'</a', 
			'split2':'>', 
			'index1':0, 
			'index2':-1,
			'datatype':str,
			'column_info':{
				'Symbol':{'sql_datatype':'TEXT', 'datatype':str}
				},
			'tag':'td'
			},
		'Price (Intraday)':{
			'sql_datatype':'REAL', 
			'split1':'</span', 
			'split2':'>', 
			'index1':0, 
			'index2':-1, 
			'datatype':float,
			'column_info':{
				'Price':{'sql_datatype':'REAL', 'datatype':float}},
			'tag':'td'
			},
		'Volume':{
			'sql_datatype':'INTEGER',
			'split1':'</span', 
			'split2':'>', 
			'index1':0, 
			'index2':-1, 
			'datatype':int,
			'column_info':{
				'Volume':{'sql_datatype':'INTEGER', 'datatype':int}
				},
			'tag':'td'
			} 
		}
}
watchlist_scrape_params = {
	'html_params': {
		'Symbol':stock_scrape_params['html_params']['Symbol']
		}
}
indices_scrape_params = {
	'html_params':{
		"data-col0 Ta(start) Pstart(6px)":{
			'sql_datatype':'TEXT',
			'split1':'</a', 
			'split2':'>', 
			'index1':0, 
			'index2':-1, 
			'datatype':str,
			'column_info':{
				'Symbol':{'sql_datatype':'TEXT', 'datatype':str}
				},
			'tag':'td'
			},
		"data-col2 Ta(end) Pstart(20px)":{
			'sql_datatype':'REAL',
			'split1':'</td', 
			'split2':'>',
			'index1':0, 
			'index2':-1, 
			'datatype':float,
			'column_info':{
				'Price':{'sql_datatype':'REAL', 'datatype':float}},
			'tag':'td'
			},
		"data-col5 Ta(end) Pstart(20px)":{
			'sql_datatype':'INTEGER',
			'split1':'</td', 
			'split2':'>', 
			'index1':0, 
			'index2':-1, 
			'datatype':int,
			'column_info':{
				'Volume':{'sql_datatype':'INTEGER', 'datatype':int}
				},
			'tag':'td'
			} 
		}
}

futures_scrape_params = {
	'html_params': {
		"data-col0 Ta(start) Pstart(6px)":{
			'split1':'</a', 
			'split2':'>', 
			'index1':0, 
			'index2':-1, 
			'column_info':{
				'Symbol':{'sql_datatype':'TEXT', 'datatype':str}
				},
			'tag':'td'
			},
		"data-col2 Ta(end) Pstart(20px)":{
			'split1':'</td', 
			'split2':'>',
			'index1':0, 
			'index2':-1, 
			'column_info':{
				'Price':{'sql_datatype':'REAL', 'datatype':float}},
			'tag':'td'
			},
		"data-col6 Ta(end) Pstart(20px)":{
			'split1':'</td', 
			'split2':'>', 
			'index1':0, 
			'index2':-1, 
			'column_info':{
				'Volume':{'sql_datatype':'INTEGER', 'datatype':int}
				},
			'tag':'td'
			} 
		}
}

currencies_scrape_params = {
	'html_params':{
		"data-col0 Ta(start) Pstart(6px)": {
			'split1':'</a', 
			'split2':'>', 
			'index1':0, 
			'index2':-1, 
			'column_info':{
				'Symbol':{'sql_datatype':'TEXT', 'datatype':str}
				},
			'tag':'td'
			}, 
		"data-col2 Ta(end) Pstart(20px)":{
			'split1':'</td', 
			'split2':'>',
			'index1':0, 
			'index2':-1, 
			'column_info':{
				'Price':{'sql_datatype':'REAL', 'datatype':float}
				},
			'tag':'td'
			} 
		}
}
statistics_scrape_params = {
	'html_params':{
		"Ta(c) Pstart(10px) Miw(60px) Miw(80px)--pnclg Bgc($lv1BgColor) fi-row:h_Bgc($hoverBgColor)": {
			'sql_datatype':'REAL',
			'split1':'</', 
			'split2':'">', 
			'index1':0, 
			'index2':-1, 
			'datatype':float,
			'column_info':{
				'Market_Cap_intraday':{'sql_datatype':'REAL', 'datatype':float}, 
				'Enterprise_Value':{'sql_datatype':'REAL', 'datatype':float}, 
				'Trailing_P_E':{'sql_datatype':'REAL', 'datatype':float},
				'Forward_P_E':{'sql_datatype':'REAL', 'datatype':float},
				'PEG_Ratio_5_yr_expected':{'sql_datatype':'REAL', 'datatype':float},
				'Price_Sales_ttm':{'sql_datatype':'REAL', 'datatype':float},
				'Price_Book_mrq':{'sql_datatype':'REAL', 'datatype':float}, 
				'Enterprise_Value_Revenue':{'sql_datatype':'REAL', 'datatype':float},
				'Enterprise_Value_EBITDA':{'sql_datatype':'REAL', 'datatype':float}
				},
			'tag':'td',
			},
		"Fw(500) Ta(end) Pstart(10px) Miw(60px)": {
			'sql_datatype':'REAL',
			'split1':'</td>', 
			'split2':'">', 
			'index1':0, 
			'index2':-1, 
			'datatype':float,
			'column_info':{
				'Beta_5Y_Monthly':{'sql_datatype':'REAL', 'datatype':float}, 
				'_52_Week_Change':{'sql_datatype':'REAL', 'datatype':float},
				'S_and_P500_52_Week_Change':{'sql_datatype':'REAL', 'datatype':float}, 
				'_52_Week_High':{'sql_datatype':'REAL', 'datatype':float}, 
				'_52_Week_Low':{'sql_datatype':'REAL', 'datatype':float}, 
				'_50_Day_Moving_Average':{'sql_datatype':'REAL', 'datatype':float}, 
				'_200_Day_Moving_Average':{'sql_datatype':'REAL', 'datatype':float}, 
				'Avg_Vol_3_month':{'sql_datatype':'REAL', 'datatype':float}, 
				'Avg_Vol_10_day':{'sql_datatype':'REAL', 'datatype':float}, 
				'Shares_Outstanding':{'sql_datatype':'INTEGER', 'datatype':int}, 
				'Float':{'sql_datatype':'REAL', 'datatype':float}, 
				'Percent_Held_by_Insiders':{'sql_datatype':'REAL', 'datatype':float}, 
				'Percent_Held_by_Institutions':{'sql_datatype':'REAL', 'datatype':float}, 
				'Shares_Short':{'sql_datatype':'INTEGER', 'datatype':int}, 
				'Short_Ratio':{'sql_datatype':'INTEGER', 'datatype':float}, 
				'Short_Percent_of_Float':{'sql_datatype':'REAL', 'datatype':float}, 
				'Short_Percent_of_Shares_Outstanding':{'sql_datatype':'REAL', 'datatype':float},
				'Shares_Short_prior_month':{'sql_datatype':'INTEGER', 'datatype':int}, 
				'Forward_Annual_Dividend_Rate':{'sql_datatype':'REAL', 'datatype':float}, 
				'Forward_Annual_Dividend_Yield':{'sql_datatype':'REAL', 'datatype':float}, 
				'Trailing_Annual_Dividend_Rate':{'sql_datatype':'REAL', 'datatype':float}, 
				'Trailing_Annual_Dividend_Yield':{'sql_datatype':'REAL', 'datatype':float}, 
				'_5_Year_Average_Dividend_Yield':{'sql_datatype':'REAL', 'datatype':float}, 
				'Payout_Ratio':{'sql_datatype':'REAL', 'datatype':float}, 
				'Dividend_Date':{'sql_datatype':'TEXT', 'datatype':str}, 
				'Ex_Dividend_Date':{'sql_datatype':'TEXT', 'datatype':str}, 
				'Last_Split_Factor':{'sql_datatype':'INTEGER', 'datatype':int}, 
				'Last_Split_Date':{'sql_datatype':'TEXT', 'datatype':str},
				None:{'sql_datatype':'TEXT', 'datatype':str},
				'Most_Recent_Quarter_mrq':{'sql_datatype':'TEXT', 'datatype':str}, 
				'Profit_Margin':{'sql_datatype':'REAL', 'datatype':float}, 
				'Operating_Margin_ttm':{'sql_datatype':'REAL', 'datatype':float},
				'Return_on_Assets_ttm':{'sql_datatype':'REAL', 'datatype':float}, 
				'Return_on_Equity_ttm':{'sql_datatype':'REAL', 'datatype':float},
				'Revenue_ttm':{'sql_datatype':'REAL', 'datatype':float},
				'Revenue_Per_Share_ttm':{'sql_datatype':'REAL', 'datatype':float}, 
				'Quarterly_Revenue_Growth_yoy':{'sql_datatype':'REAL', 'datatype':float},
				'Gross_Profit_ttm':{'sql_datatype':'REAL', 'datatype':float},
				'EBITDA':{'sql_datatype':'REAL', 'datatype':float}, 
				'Net_Income_Avi_to_Common_ttm':{'sql_datatype':'REAL', 'datatype':float},
				'Diluted_EPS_ttm':{'sql_datatype':'REAL', 'datatype':float}, 
				'Quarterly_Earnings_Growth_yoy':{'sql_datatype':'REAL', 'datatype':float},
				'Total_Cash_mrq':{'sql_datatype':'REAL', 'datatype':float}, 
				'Total_Cash_Per_Share_mrq':{'sql_datatype':'REAL', 'datatype':float},
				'Total_Debt_mrq':{'sql_datatype':'REAL', 'datatype':float}, 
				'Total_Debt_Equity_ratio_mrq':{'sql_datatype':'REAL', 'datatype':float},
				'Current_Ratio_mrq':{'sql_datatype':'REAL', 'datatype':float}, 
				'Book_Value_Per_Share_mrq':{'sql_datatype':'REAL', 'datatype':float},
				'Operating_Cash_Flow_ttm':{'sql_datatype':'REAL', 'datatype':float}, 
				'Levered_Free_Cash_Flow_ttm':{'sql_datatype':'REAL', 'datatype':float}
				},
			'tag':'td'
			}
		},
}

scrape_param_lookup = {
	yahoo_etf_url:stock_scrape_params,
	yahoo_gainers_url:stock_scrape_params,
	yahoo_active_url:stock_scrape_params,
	yahoo_losers_url:stock_scrape_params,
	yahoo_indices_url:indices_scrape_params,
	yahoo_futures_url:futures_scrape_params,
	yahoo_currencies_url:currencies_scrape_params,
	yahoo_asset_valuation_url:statistics_scrape_params
}

#market_db_columns = {'Symbol':'TEXT', 'Price':'REAL', 'Volume':'INTEGER', 'Date':'TEXT'} # don't use this one, use the (...)_scrape_params variables.

yahoo_login_data = {
	'crumb': 'nQGzz7XNfeL',
	'acrumb': 'kCQGaFj2',
	'sessionIndex': 'QQ--',
	'verifyPassword': 'Next'
}
web_login_headers = {
	'user-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36 Edg/86.0.622.38'
}
web_login_params = {'priority':'normal'}

yahoo_scrape_url = 'https://finance.yahoo.com/quote/{}/history?p={}'
businsider_stock_scrape_url = 'https://markets.businessinsider.com/stocks/{}-stock'
businsider_index_scrape_url = 'https://markets.businessinsider.com/index/{}'
yahoo_rtprice_httpclass = 'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)'
businsider_rtprice_httpclass = "price-section__current-value"

magnitudes = {'M':1000000, 'B':1000000000}

yahoo_tickers = ['TSLA', 'GOOG', 'AAPL', 'AMZN', 'SHOP', 'BABA', 'SQ', 'MELI',
			     'FB', 'JD', 'CRM', 'NVDA', 'ZM', 'ADBE', 'PYPL', 
			     '^GSPC', '^RUT']
businsider_tickers = ['NLS', 'NFLX']
businsider_indices = ['dow-jones-composite-average']

'''
dataset_html_params = [
	{
		'attr': (attribute)
		'column': (column)
		'filtr_params': (split1, split2, index1, index2, datatype)
	},
]
'''

#price database keys
datestamp_key = 'datestamp'
tickers_key = 'ticker'
compnames_key = 'company_name'
prices_key = 'price'
volumes_key = 'volume'
mcaps_key = 'market_cap'
pe_ratios_key = 'pe_ratio'

stock_actives_key = 'Stock_Actives'
stock_gainers_key = 'Stock_Gainers'
stock_losers_key = 'Stock_Losers'
tables_urls = {stock_actives_key:yahoo_active_url, stock_gainers_key:yahoo_gainers_url,
			   stock_losers_key:yahoo_losers_url}
# tables_struct = {stock_actives_key:stock_table_columns, stock_gainers_key:stock_table_columns,
# 				 stock_losers_key:stock_table_columns}

pid_key = 'productId'
ordertype_key = 'orderType'
orderid_key = 'orderId'
size_key = 'size'
stop_key = 'stopPrice'
limit_key = 'limitPrice'
buysell_key = 'buysell'

order_types = ['limit', 'market', 'stoploss', 'stoplimit']

entry_threshold = 0.1
target_threshold = 2
stop_threshold = 1.5
danger_margin = 0.3
pivotpoint_cutoff = 0.2

realtrade_countdown = 3

order_duration_def = 1

max_recurse_depth = 3