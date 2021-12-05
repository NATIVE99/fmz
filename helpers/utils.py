from helpers.object import FmzBarData, GF
import talib
import numpy as np
import pandas as pd
import traceback
import platform
import math
import redis
import re
# from kw618.k_finance.Arbitrage.getData import MarketDataReceiver
import random

# 通用类-指标扩展类
class IndicatorsExtension():
    def __init__(self):
        pass

    def get_boll_price_dict(self, bars):
        "获得布林带上各个位置的价格"
        boll_price_dict = {}
        if bars and len(bars) > 20:
            boll = talib.BBANDS(bars.Close, 20, 2)
            upLine = boll[0][-1]  # 上轨
            midLine = boll[1][-1]  # 中轨
            downLine = boll[2][-1]  # 下轨
            unit_price = (upLine - downLine) / 4  # 1个单位的价格
            boll_price_dict = {
                0: midLine,
                1: midLine + unit_price,
                2: upLine,
                2.5: upLine + unit_price * 0.5,
                3: upLine + unit_price,
                4: upLine + 2 * unit_price,
                6: upLine + 4 * unit_price,
                8: upLine + 6 * unit_price,
                10: upLine + 8 * unit_price,
                -1: midLine - unit_price,
                -2: downLine,
                -2.5: downLine - unit_price * 0.5,
                -3: downLine - unit_price,
                -4: downLine - 2 * unit_price,
                -6: downLine - 4 * unit_price,
                -8: downLine - 6 * unit_price,
                -10: downLine - 8 * unit_price,
            }
        return boll_price_dict

    def get_candle_type(self, bar):
        "获得k线的阴阳"
        open_price = bar.Open
        close_price = bar.Close
        delta_price = close_price - open_price
        if delta_price > 0:
            candle_type = "positive"
        elif delta_price < 0:
            candle_type = "negative"
        elif delta_price == 0:
            candle_type = "cross"
        return candle_type

    def get_bbw_arr(self, bars):
        """
        return: bbw的列表
        """
        boll = talib.BBANDS(bars.Close, 20, 2)
        upLine = np.array(boll[0])  # 上轨
        midLine = np.array(boll[1])  # 中轨
        downLine = np.array(boll[2])  # 下轨
        # 将前面元素的None值, 转为0, 才能进行相减
        upLine[upLine == None] = 0
        downLine[downLine == None] = 0
        bbw_arr = upLine - downLine

        bbw_arr[bbw_arr == 0] = None
        return bbw_arr

    def get_sar_arr(self, bars):
        """
        notes:
            - 传入bars, 获得SAR列表
        """
        highPrice_arr = bars.High
        lowPrice_arr = bars.Low
        sar_arr = talib.SAR(highPrice_arr, lowPrice_arr)
        return sar_arr

    def get_last_sar(self, bars):
        """
        notes:
            - 获取最近的'已完结bar'的最新的sar值
        """
        closePrice_arr = bars.Close
        sar_arr = self.get_sar_arr(bars=bars)
        last_sar = sar_arr[-1]  # 获取最新的sar值 (把最后一个元素作为sar的值)
        return last_sar

    def get_last_sar_flag(self, bars):
        """
        notes:
            - 获取最近的'已完结bar'的sar的方向  (默认bars的最后一个元素就是'最近的已完结bar')
                1: sar在上
                -1: sar在下
        """
        closePrice_arr = bars.Close
        sar_arr = self.get_sar_arr(bars=bars)
        # 差值arr
        delta_arr = sar_arr - closePrice_arr
        delta_arr = delta_arr / abs(delta_arr)  # 用 1, -1 来表示方向
        last_sar_flag = delta_arr[-1]  # 最新sar的flag
        return last_sar_flag

    def cal_diversion(self, bars):
        "计算该bar的sar是否发生'转向'"
        # 最新的sar值的flag (1/-1)
        last_sar_flag = get_last_sar_flag(bars=bars)
        if last_sar_flag * GP.global_last_sar_flag == -1:
            diversion = True
        else:
            diversion = False
        GP.global_last_sar_flag = last_sar_flag  # -1 / 1
        return diversion


    def get_avg_candles(self, bars):
        "获取平均k线的指标"
        pass

        # 在这里我们将平均K线图（Heikin-Ashi）的开市价、最高价、最低价及收市价简称为：h-open、h-high、h-low及h-close。而普通蜡烛图的开市价、最高价、最低价及收盘价则简称为：s-open、s-high、s-low及s-close，那么平均K线图中的几个关键价格的计算方法就是：
        # h-close= (s-open + s-high + s-low + s-close) / 4
        # h-open= (上一支烛的h-open + 上一支烛的s-close)/2
        # h-high= s-high , h-open, h-close 三者中取「最高值」
        # h-low= s-low、h-open、h-close 三者中取「最低值」
        # 正因为这样的计算方式，交易员无法知道某一特定时间段开盘或收盘的确切价格。对于日内交易者来说这可能是个问题。而对于长线交易员来说，这却不是什么大问题，因为在持续数周、数月或数年的交易中，K线的开盘价和收盘价并不那么重要。

        # bars = [
        # {'Time': 1621035120000,
        #   'Open': 49883.543,
        #   'High': 49883.543,
        #   'Low': 49883.543,
        #   'Close': 49883.543,
        #   'Volume': 164.7645,
        #   'OpenInterest': 0.0},
        #  {'Time': 1621035360000,
        #   'Open': 49914.056,
        #   'High': 49914.056,
        #   'Low': 49914.056,
        #   'Close': 49914.056,
        #   'Volume': 164.7645,
        #   'OpenInterest': 0.0},
        #  {'Time': 1621035960000,
        #   'Open': 49730.98,
        #   'High': 49730.98,
        #   'Low': 49730.98,
        #   'Close': 49730.98,
        #   'Volume': 164.7645,
        #   'OpenInterest': 0.0},
        #  {'Time': 1621036200000,
        #   'Open': 49813.832,
        #   'High': 49813.832,
        #   'Low': 49813.832,
        #   'Close': 49813.832,
        #   'Volume': 164.7645,
        #   'OpenInterest': 0.0},
        #  {'Time': 1621036440000,
        #   'Open': 49786.215,
        #   'High': 49786.215,
        #   'Low': 49786.215,
        #   'Close': 49786.215,
        #   'Volume': 164.7645,
        #   'OpenInterest': 0.0},
        #  {'Time': 1621036680000,
        #   'Open': 49841.45,
        #   'High': 49841.45,
        #   'Low': 49841.45,
        #   'Close': 49841.45,
        #   'Volume': 329.529,
        #   'OpenInterest': 0.0},
        #  {'Time': 1621036800000,
        #   'Open': 49844.16,
        #   'High': 49844.16,
        #   'Low': 49844.16,
        #   'Close': 49844.16,
        #   'Volume': 0.0,
        #   'OpenInterest': 0.0},
        #  {'Time': 1621036920000,
        #   'Open': 49844.161,
        #   'High': 49844.161,
        #   'Low': 49844.161,
        #   'Close': 49844.161,
        #   'Volume': 231.4324,
        #   'OpenInterest': 0.0}
        # ]


        h_bars = [] # 存放所有'平均k线'的bar

        h_bars_point = 0 # 0 还是 -1 ???
        bars_point = 1 # 从1开始 (因为h_open的计算需要知道前一个bar, 而bars_point为0时是没有'前一个bar'的)
        while bars_point < len(bars):
            bar = bars[bars_point] # 当下已经完结的bar
            pre_bar = bars[bars_point-1] # 前一个已经完结的bar

            h_close = (bar["Open"] + bar["High"] + bar["Low"] + bar["Close"]) / 4
            if bars_point == 1:
                h_open = pre_bar["Close"]
            else:
                h_open = (h_bars[h_bars_point-1]["Open"] + pre_bar["Close"]) / 2
            h_high = max(bar["High"], h_open, h_close)
            h_low = min(bar["Low"], h_open, h_close)

            h_bar = {"Open":h_open, "High":h_high, "Low":h_low, "Close":h_close}
            h_bars.append(h_bar)


            bars_point += 1
            h_bars_point += 1

        return h_bars

    def get_dc(self, bars):
        "获取DC 唐奇安通道指标，指标参数均为默认参数 20日 "

        def gh(bar: FmzBarData):
            return bar.High

        def gl(bar: FmzBarData):
            return bar.Low

        dc_length = 20 # 默认为 20

        if len(bars) > dc_length:
            lastest_bars = bars[-dc_length:]
            bars_high_price = map(gh, lastest_bars)
            highest_price = max(bars_high_price)
            bars_low_price = map(gl, lastest_bars)
            lowest_price = min(bars_low_price)
            mid_price = (highest_price + lowest_price) / 2
            return {
                "upline" : highest_price,
                "midline": mid_price,
                "downline": lowest_price
            }
        else:
            raise Exception("the bars lenght error ......")


# 通用类-发明者相关模块
class FmzUtils():
    "专门实现发明者所需的函数, 比如'打印账户余额', 下单...等都可以扔到这里来"

    def __init__(self):
        # 对象一生成时, 就会清空redis, 并获取3个账户的精度信息
        # mdr = MarketDataReceiver()
        # mdr.get_exchange_info()
        # pass
        try:
            self.r2 = redis.StrictRedis(host="localhost", port=6379, db=2, decode_responses=True) # 2号数据库(用于存储exchange_info数据)
        except ConnectionError as e:
            self.GF.Logger.log(f"connect redis error {e}", 50)
        finally:
            print(f"connect redis successful {self.r2}", 50)


    def get_symbol(self, exchange):
        exchange_name = exchange.GetName()
        symbol = exchange.GetCurrency()  # 这里直接返回的就是‘symbol’ // "BTC_USDT"
        base_asset = symbol.split("_")[0]  # "BTC"
        quote_asset = exchange.GetQuoteCurrency()  # "USDT"
        full_symbol = f"{exchange_name}.{symbol}"  # "Binance.BTC_USDT"
        return (symbol, full_symbol, base_asset, quote_asset)

    def utc0_to_utc8(self, series):
        # "把中央时区的时间转化成东八区时间"
        series = pd.to_datetime(
            series, unit="ms").dt.tz_localize('UTC').dt.tz_convert('hongkong')
        return series

    def sort_df(self, df, ordered_field_lst):
        # 1. 如果指定的字段在df中并不存在,则把该字段remove掉.确保不报错
        ordered_field_lst_copy = ordered_field_lst.copy()
        for field in ordered_field_lst_copy:
            if field not in df.columns:
                print("字段 {} 不在df中, 将其抛弃!".format(field))
                ordered_field_lst.remove(field)

        # 2. 把所需要保留的 "有序字段list" 作用在df上
        return df[ordered_field_lst]  # 指定顺序

    def get_lc_symbol(self, exchange):
        "默认就是返回币安合约的symbol"
        symbol = exchange.GetCurrency() # ETH_USDT
        lc_symbol = "".join(symbol.split("_")) + "_PERP"
        # GF.Log(f"lc_symbol:{lc_symbol}")
        return lc_symbol


    def get_random_num(self, min_digital=3):
        "获取一个 [0.0, 1.0) 的随机数"
        random_num = np.random.rand(1)[0]
        random_num = round(random_num, min_digital)
        return random_num


    # 指定概率随机数
    def p_random(self, arr1, arr2):
        assert len(arr1) == len(arr2), "Length does not match."
        assert sum(arr2) == 1 , "Total rate is not 1."

        sup_list = [len(str(i).split(".")[-1]) for i in arr2]
        top = 10 ** max(sup_list)
        new_rate = [int(i*top) for i in arr2]
        rate_arr = []
        for i in range(1,len(new_rate)+1):
            rate_arr.append(sum(new_rate[:i]))
        rand = random.randint(1,top)
        data = None
        for i in range(len(rate_arr)):
            if rand <= rate_arr[i]:
                data = arr1[i]
                break
        return data

        """e.g.

        plist = []
        for i in range(100000):
            plist.append( p_random([1,2,3],[0.209,0.291,0.5]))
        print(Counter(plist))

        """

# fmz工具对象
UTILS = FmzUtils()

class FmzLogger():
    """
        function: 基于fmz的Log方法的二次封装
                不同msg_level: 会输出不同重要程度的颜色
                不同log_level: 高于log_level的msg_level才会被打印
    """
    def __init__(self, fmz_log, log_level=10):
        self.fmz_log = fmz_log
        self.log_level = log_level

    def set_level(self, log_level=10):
        self.log_level = log_level

    def log(self, msg, msg_level=10):
        # Task：
        # 1.不同的颜色代表不同的打印分类。比如: 红色代表 debug 信息。绿色代表下单成功的信息。
        # 2.相同的颜色不同的颜色深度代表该分类的重要性比如：红色由 10 表示， 11， 12， 13， 14 ...  19 都代表红色，只是颜色的透明度不一样。

        # 1. 决定msg颜色
        if msg_level == 10:
            msg_color = "#000000"  # 黑色
        elif msg_level == 20:
            msg_color = "#459be9"  # 蓝色
        elif msg_level == 30:
            msg_color = "#2aca60"  # 绿色
        elif msg_level == 40:
            msg_color = "#f56523"  # 橙色
        elif msg_level == 50:
            msg_color = "#ff0000"  # 红色
        elif msg_level == 60:
            msg_color = "#ac66cc"  # 紫色
        elif msg_level == 70:
            msg_color = "#e96372"  # 浅粉红
        elif msg_level == 80:
            msg_color = "#f6c847"  # 黄色
        elif msg_level == 90:
            msg_color = "#717df0"  # 紫色
        elif msg_level == 100:
            msg_color = "#ec68f4"  # 深粉红
        elif msg_level == 51:
            msg_color = "#459be9"  # 蓝色 (开盘收盘分割线)
        # 2. 决定msg是否输出
        if msg_level >= self.log_level:
            self.fmz_log(msg, msg_color)


class Locker(object):

    timer_counter = 0

    @classmethod
    def lock(cls, time:int, lock_type:str, is_output:bool):
        """开仓锁

        Args:
            time (int): 锁的时间
            lock_type (str): 锁的类型： 支持：不开空， 不开多， 不开空也不开多
            is_output (bool): 是否输出状态， 比如不开多， 如果为 True 函数返回 no_long
        """

#
