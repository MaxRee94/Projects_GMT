import constants as csts
import my_utils as mutils

import degiroapi
from degiroapi.product import Product
from degiroapi.order import Order
from degiroapi.utils import pretty_json

from datetime import datetime, timedelta


class ProductData:
    #RESIST_RANGE = 0.1

    def __init__(self, degiro, ticker='TRUP'):
        self.date = datetime.now().strftime("%m/%d/%Y")
        self.degiro = degiro
        self.ticker = ticker
        self.product = self.get_product(ticker)
        self.hist_1yr = self.get_hist_1yr()
        self.dsma = self.get_dsma()
        self.dopen = self.get_dopen()
        self.dclose = self.get_dclose()
        self.rtprice = self.get_rtprice()
        self.atr14 = self.get_atr14()
        self.atr_percent = self.get_percent_atr(self.atr14)
        self.atr_relative = self.get_atr_relative()
        self.dhist = None
        #self.hist_14day = self.get_hist_14day()
        self.dlow = None
        self.dhigh = None
        self.pivot_point = None
        self.resist = None
        self.support = self.get_support()
        self.stocksplit_date, self.stocksplit_ratio = self.get_stocksplit()

        self.update_dhist(self.ticker, self.product.id)
        self.update_drange()
        self.update_pivot_point()
        self.update_resistance()

    def get_product(self, ticker):
        try:
            products = self.degiro.search_products(ticker)
            product = Product(products[0])
        except KeyError as e:
            print('Unable to get product of {}. Error:'.format(ticker), e)
            return None

        return product

    def update_pivot_point(self):
        if not (self.dlow and (self.dhigh and self.rtprice)):
            return

        # print('dlow:', self.dlow)
        # print('dhigh:', self.dhigh)
        # print('rtprice:', self.rtprice)
        self.pivot_point = (self.dlow + self.dhigh + self.rtprice) / 3
        # print('pivot:', self.pivot_point)

    def get_atr_relative(self):
        if not self.atr_percent:
            return None

        atr_relative = self.atr_percent * self.rtprice
        return atr_relative

    def update_resistance(self):
        # if (not self.hist_1yr) or (not self.atr_relative):
        #     return None, None

        # period_range = period_end - period_start
        # if period_range == 1:
        #     highs = self.update_dhist()['']
        # else:
        #     highs = self.get_datapoint_period(self.hist_1yr, 'high', 
        #                                       period_start, period_end)

        # highs = list(highs.values())
        # highs.sort()
        # period_high = highs[-1]

        # resist_range = self.RESIST_RANGE * self.atr_relative
        # minimum_price = period_high - resist_range

        # resistance_highs = []
        # for high in highs:
        #     if high >= minimum_price:
        #         resistance_highs.append(high)

        # stability = (len(resistance_highs) - 1) / (len(highs)) * 100
        # resistance = sum(resistance_highs) / len(resistance_highs)
        
        if not self.dlow or not self.pivot_point:
            return

        self.resist = self.pivot_point * 2 - self.dlow
        print('resistance:', self.resist)

    def get_support(self):
        if not self.pivot_point or not self.dhigh:
            return 

        support = self.pivot_point * 2 - self.dhigh
        return support

    def get_dsma(self):
        pass

    def get_dopen(self):
        pass

    def get_dclose(self):
        pass

    def get_rtprice(self):
        pass

    def get_datapoint_period(self, source_data, data_key, period_start, period_end):
        if not self.hist_1yr:
            return

        source_data = list(source_data.items())
        datapoint = {}
        for time, info in source_data[period_start:period_end]:
            if type(info) == float:
                datapoint[time] = info
            elif type(info) == dict:
                datapoint[time] = info[data_key]

        return datapoint

    def calc_atr(self, highs, lows):
        tr_sum = 0
        for (high, low) in zip(highs, lows):
            tr = abs(high-low)
            tr_sum += tr

        atr = tr_sum / len(highs)

        return atr

    def get_atr14(self):
        if not self.hist_1yr:
            return

        highs_14d = self.get_datapoint_period(self.hist_1yr, 'high', 0, 14)
        lows_14d = self.get_datapoint_period(self.hist_1yr, 'low', 0, 14)
        atr14 = self.calc_atr(list(highs_14d.values()), list(lows_14d.values()))
        return atr14

    def get_percent_atr(self, abs_atr):
        atr_percent = None
        if abs_atr:
            atr_percent = abs_atr / self.rtprice
        return atr_percent

    def get_hist_1yr(self):
        pass

    def add_padding(self, my_int, padding):
        my_str = str(my_int)
        while len(my_str) < padding:
            my_str = '0{}'.format(my_str)

        return my_str

    def get_next_minute(self, time):
        next_minute = int(time.split('.')[1]) + 1
        current_hour = time.split('.')[0]
        time = mutils.add_padding('{}.{}'.format(current_hour, '{}'), next_minute, 2)
        if time.split('.')[1] == '60':
            next_hour = int(current_hour) + 1
            time = '{}.{}'.format(str(next_hour), '00')

        return time

    def convert_degiro_time(self, rawdate, rawtime):
        rawdate = rawdate.replace('-', '/')
        time_string = '{}, {}'.format(rawdate, rawtime)
        time = datetime.strptime(time_string, "%Y/%m/%d, %H:%M:%S")
        return time

    def update_dhist(self, ticker, product_id, recursion_depth=0, time=None):
        try:
            interval_data = self.degiro.real_time_price(product_id, 
                                                    degiroapi.Interval.Type.One_Day)
        except KeyError as e:
            print('Couldnt get price data for {}. Error:'.format(ticker), e)
            return None, None

        if 'error' in interval_data[0].keys():
            print('Couldnt get price data for {}. Error-keys in returned data dict.')
            return None, None

        general_data = interval_data[0]['data']
        #print('gen data:', general_data)
        date = general_data['lastTime'].split('T')[0]
        time = general_data['tradingStartTime']
        dhist_raw = interval_data[1]['data']
        self.dhist = {}
        time = self.convert_degiro_time(date, time)
        for rawtime, price in dhist_raw:
            self.dhist[time.strftime("%m/%d/%Y, %H:%M:%S")] = price
            #print('time string:', time.strftime("%m/%d/%Y, %H:%M:%S"))
            time += timedelta(minutes=1)

        if self.dhist == {}:
            if recursion_depth > 10:
                print('Recursion limit reached. Failed to receive a data dict for {}.'.format(ticker))
                return None, None

            print('Prices could not be obtained. Retrying...')
            self.update_dhist(ticker, product_id, recursion_depth=recursion_depth+1)
        else:
            return self.dhist, time

    def update_drange(self):
        prices = list(self.dhist.values())

        for i in range(int(len(prices) * csts.pivotpoint_cutoff)):
            prices.pop(-1)

        self.dlow = min(prices)
        self.dhigh = max(prices)
        self.dtrue_range = self.dhigh - self.dlow

    def get_stocksplit(self):
        if self.product.id == '1153605':
            stocksplit_ratio = 5
            stocksplit_date = '2020-08-31 00:00:00.000000'
            return stocksplit_date, stocksplit_ratio
        else:
            return None, None

def main():
    degiro = degiroapi.DeGiro()
    degiro.login(csts.degiro_username, 
                 csts.degiro_password)

    pdata = ProductData(degiro)
    return pdata

if __name__ == '__main__':
    main()
