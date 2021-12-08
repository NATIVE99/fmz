'''
version: v1.0.1
修改持仓的判断bug，开仓量和平仓量可能不同，这时候如果小于等于0.001，就会从交易所获取一次
修改没有过滤器的时候，不考虑肯定器与否定器

'''
from helpers import *
from functools import reduce
import talib as ta
import numpy as np
import pandas as pd
import time
import json
import math
import re

class StrategyWave(BaseStrategy):
    """
    策略逻辑:盈利翻倍亏损不减仓
    """
    author = "mahao"

    # 可调参数

    parameters = [
        # 策略通用参数
        "base_qty",
        "quote_qty",
        "trading_toggle",
        "buy_trading_toggle",
        "sell_trading_toggle",
        # 实盘通用参数
        "choose_running_num",  # 限制一天开几次仓
        "increase_position_num",  # 第一笔订单的加仓倍数
        "init_reboot",  # 策略刚启动是否撤单和平仓
        # 策略的参数
        #"increase_mul", # 加仓倍数
        # "multiplier",  # 加仓倍数
        # "init_position", # 初始仓位
        # "exit_conditions"# 退出条件

    ]
    # 状态变量
    """使用self.print_variables(score=100)可以打印状态变量
    """
    variables = []

    def __init__(self, cta_engine):  # 这里应该是默认的参数，
        super().__init__(cta_engine)

        # 添加策略必备的'子组件'
        self.add_trade(TradeWave)
        self.add_analysis(AnalysisWave)
        # self.add_pm(BasePositionManager)
        self.add_pm(MyBasePositionManager)
        self.log = self.GF.Logger.log  # 自己写的打印

    def initialize(self):
        """初始化参数，包括策略参数，通用函数，通用参数 
        """
        self.init_strategy_param()
        # 计算初始的价格，因为框架刚启动，价格为None
        if not self.tick.price:
            self.tick.price = self.GF.exchange.GetTicker().Last
        # 获取下单的数量精度和价格精度
        self.get_symbol_precision()
        self.init_param()

    def init_param(self):
        """策略初始化的时候，通用的参数
        """
        # 必须参数
        self.old_bar = []  # 用于判断K线是否更新了
        self.old_order_lst = []  # 用于is_order_profit_or_loss()收益率的计算
        self.position_new_flag = None  # 持仓的方向
        self.refresh_position = False  # 是否刷新仓位
        # 信号
        # self.open_tick_signal = {'buy':False,'sell':False}
        self.open_bar_signal = {'buy': False, 'sell': False}  # bar信号可以保存为类变量，tick信号是实时刷新，不需要类变量
        # self.close_tick_signal = {'buy':False,'sell':False}
        self.close_bar_signal = {'buy': False, 'sell': False}

        # 止盈挂单价格
        self.sell_profit_price = self.buy_profit_price = 0

        # 收益率计算，该值为初始的收益率
        self.first_balance = self.trade.get_future_quote_qty_tatal()

        # 打印参数
        self.print_account_info = 0  # 重复打印账户信息的判断参数
        self.print_account_info2 = 0  # 重复打印账户信息的判断参数

        # 可删除
        # self.running_time = time.time()  # 策略启动时候的时间，
        # self.running_num = 0  # 策略启动后，完成一笔订单后，将该次数 + 1,一天最多开仓几次
        self.increase_position()  # 增加初始的下单次数

        # 初始更新仓位
        if self.init_reboot:
            self.trade.end_of_close_position()

    def init_strategy_param(self):
        """策略初始化时候的，可变参数
        """
        pass

    def increase_position(self):
        """策略重启后，初始的加仓次数，不影响原来的仓位
        """
        while self.increase_position_num:
            self.trade.pm.update(op="increase")
            self.increase_position_num -= 1
            if self.increase_position_num < 0:
                self.increase_position_num = 0

    # def _get_running_num(self):
    #     """限制开仓的次数，回测时候因为time.time()会遇到无法回测的问题
    #     """
    #     is_open = True
    #     if self.running_num >= self.choose_running_num:
    #         # is_open = False
    #         self.log(f"一天开仓次数达到{self.running_num}次，程序停止运行", 100)
    #         exit()
    #     if self.running_time + 60 * 60 * 24 < time.time():
    #         self.running_num = 0
    #         self.running_time = time.time()
    #     return is_open

    def get_symbol_precision(self):
        "返回合约的价格精度"
        lc_symbol = UTILS.get_lc_symbol(exchange=self.GF.exchange)
        asset_info = UTILS.r2.hget(lc_symbol, 'symbol_info')
        asset_info = json.loads(asset_info)
        if asset_info:
            tick_pre = float(asset_info['filters'][0]['tickSize'])  # 0.0000100
            asset_pre = float(asset_info['filters'][1]['stepSize'])  # 0.00100
            # 将对应的数字寻找他的小数位
            # 寻找价格的小数位
            tick_num = math.floor(math.log10(1 / tick_pre) + 0.9)
            self.price_precision = min(max(tick_num, 0), 6)
            asset_num = math.floor(math.log10(1 / asset_pre) + 0.9)
            self.asset_precision = min(max(asset_num, 0), 6)
            self.log(f"price_precision:{self.price_precision}", 100)
            self.log(f"asset_precision:{self.asset_precision}", 100)
        else:
            self.log(f"没有获取到价格和数量精度，需要重启策略", 100)
            exit()

    def show_profit(self):
        """显示收益曲线
        """
        new_balance = self.trade.get_future_quote_qty_tatal()
        diff_banlance = new_balance - self.first_balance
        GF.LogProfit(diff_banlance)

    @staticmethod
    def cache_boll_data(bars):
        '''talib里的boll计算方式,为空部分返回nan，fmz计算boll为空返回None，因为是连续的，计算时候需要砍掉空值
        return: boll
        '''
        # talib计算boll的方法
        boll = ta.BBANDS(bars.Close, 20, 2)
        upLine, midLine, downLine = boll[0], boll[1], boll[2]  # 上，中，下轨
        # talib为空部分返回nan，需要进行删除处理
        upLine, midLine, downLine = upLine[~np.isnan(upLine)], midLine[~np.isnan(midLine)], downLine[~np.isnan(downLine)]

        # 对他们进行最小长度截取 , 计算bbw的值，每根K线对应一个bbw
        min_len = min(len(upLine), len(midLine), len(downLine))
        upLine, midLine, downLine = upLine[-min_len:], midLine[-min_len:], downLine[-min_len:]
        return upLine, midLine, downLine

    @staticmethod
    def cache_all_grid(bars):
        """获取所有的网格
        """
        high_price = bars.High[-1]
        low_price = bars.Low[-1]
        all_grid = {"up": high_price, "down": low_price}
        return all_grid

    def get_all_indicators(self):
        """放在循环
        进行所有技术指标的更新,包括boll，bbw，abbw，ma20，sar，网格
        放在循环前面，获取必要的指标，
        【必须每隔一根K线更新一次】
        """
        pass

    def get_open_indicators(self, trade_type='bar'):
        """放在循环
        计算开仓的bar和tick指标
        trade_type 输入 'bar' 或 'tick'
        【如果为bar放在循环的第2个位置，为tick就放在】
        """
        if trade_type == 'tick':
            return self.get_open_tick_signals()
        elif trade_type == 'bar':
            return self.get_open_bar_signals()
        else:
            raise Exception('开仓的trade_type的参数只能为bar或 tick')

    def get_close_indicators(self, trade_type='bar'):
        """放在循环
        计算平仓的bar和tick指标
        trade_type 输入 'bar' 或 'tick'
        """
        if trade_type == 'tick':
            return self.get_close_tick_signals()
        elif trade_type == 'bar':
            return self.get_close_bar_signals()
        else:
            raise Exception('平仓的trade_type的参数只能为bar或 tick')

    def get_open_tick_signals(self):
        """单个条件，在这里改，根据tick的价格，来判断开仓逻辑
        【如果有多个条件，可以写在一起，或者定义为def _get*(self):】
        """
        signal = {'buy': False, 'sell': False}
        pass
        return signal

    def get_open_bar_signals(self):
        """单个条件，在这里改，获取开仓的bar信号
        【如果有多个条件，可以写在一起，或者定义为def _get*(self):】
        """
        open_bar_signal = {'buy': False, 'sell': False}
        pass
        return open_bar_signal

    def get_close_tick_signals(self):
        """单个条件，在这里改，获取平仓的tick信号，
        当一根K线完结，就执行平仓
        【如果有多个条件，可以写在一起，或者定义为def _get*(self):】
        """
        signal = {'buy': False, 'sell': False}
        pass
        return signal

    def get_close_bar_signals(self):
        """单个条件，在这里改，获取平仓的bar信号
        【如果有多个条件，可以写在一起，或者定义为def _get*(self):】
        """
        close_bar_signal = {'buy': False, 'sell': False}
        return close_bar_signal

    def is_close_order_done(self):
        """判断最新的一笔订单是否完结了，return new_order_lst
        将多笔相同方向的订单 转为1笔订单，只有当订单长度为2时，才代表已经完结
        """
        order_dict = self.trade.strategy_trade_dict_dict
        order_id = self.trade.strategy_trade_id
        new_order_lst = order_dict.get(order_id, list())
        total_open_qty = total_close_qty = 0
        order_lst = []  # 用来存储新的订单
        for order in new_order_lst:
            if order['offset'] == 'open':
                total_open_qty += order['base_qty']
            elif order['offset'] == 'close':
                total_close_qty += order['base_qty']
        # 开平单均有记录，且数量相加为0，代表已经完全平仓了,有时候出现订单数量相加不为0的情况，这时候要查询持仓信息
        if total_open_qty and total_close_qty:
            if (total_open_qty + total_close_qty) == 0:
                order_closed = True
            elif abs(total_open_qty + total_close_qty) <= 0.001:  # 对订单再次做修改
                futures_base_qty_total = self.trade.get_futures_base_qty_total(exchange=GF.exchange)
                if futures_base_qty_total == 0:
                    order_closed = True
            if order_closed:
                order0 = dict(
                    zip(['offset', 'direction', 'price', 'base_qty'],
                        [new_order_lst[0]['offset'], new_order_lst[0]['direction'], new_order_lst[0]['price'], total_open_qty]))
                order1 = dict(
                    zip(['offset', 'direction', 'price', 'base_qty'], [
                        new_order_lst[-1]['offset'], new_order_lst[-1]['direction'], new_order_lst[-1]['price'], total_close_qty
                    ]))
                return [order0, order1]
        # 当开平单数量不等，而开单数量不为0，此时只有开仓单，平仓单数量未知
        elif total_open_qty and (total_open_qty + total_close_qty) != 0:
            order0 = dict(
                zip(['offset', 'direction', 'price', 'base_qty'],
                    [new_order_lst[0]['offset'], new_order_lst[0]['direction'], new_order_lst[0]['price'], total_open_qty]))
            order_lst = [order0]
        return order_lst

    def get_position_new_flag(self, new_order_lst):
        '''获取单项持仓的 position_new_flag，根据成交订单重新计算position_flag
        '''
        if not new_order_lst or len(new_order_lst) == 2:
            position_new_flag = 0
        elif len(new_order_lst) == 1:
            if new_order_lst[0].get('offset') == 'open':
                if new_order_lst[0].get('direction') == 'buy':
                    position_new_flag = 1
                elif new_order_lst[0].get('direction') == 'sell':
                    position_new_flag = -1
                else:
                    raise Exception('仓位计算错误')
        return position_new_flag

    def post_trade_signal(self, offset, direction, price=-1, signal_type='open_order', trade_rate=1):
        """发送下单信号,
        offset 输入 'open' or 'close'
        direction 输入'buy' or 'sell'
        price 如果不传就是市价 -1
        trade_rate 是下单的比例，默认为1
        【平仓单和开仓单不能同时发出，因为平仓单是获取的持仓数量】
        """
        if direction != 'buy' and direction != 'sell':
            raise Exception('direction的方向只能为buy 和 sell')
        if offset != 'open' and offset != 'close':
            raise Exception('offset只能为open 和 close')
        if offset == 'open':
            base_qty = self.trade.get_base_qty(base_qty=self.base_qty, quote_qty=self.trade.pm.quote_qty * trade_rate)
        elif offset == 'close':
            base_qty = abs(self.trade.get_futures_base_qty_total(exchange=self.GF.exchange)) * trade_rate
            signal_type = "close_order"
        tick_signal = {"signal_type": signal_type, "offset": offset, "direction": direction, "price": price, "base_qty": base_qty}
        return tick_signal

    # def get_position_new_flag(self):
    #     '''获取单项持仓的 position_new_flag，根据成交订单重新计算position_flag
    #     '''
    #     position_new_flag = 0
    #     futures_base_qty_total = self.trade.get_futures_base_qty_total(exchange=GF.exchange)
    #     if futures_base_qty_total < 0:
    #         position_new_flag = -1
    #     elif futures_base_qty_total > 0:
    #         position_new_flag = 1
    #     return position_new_flag

    def _get_tick_signals(self):
        """
            notice:
                - [重要]: 通过'止盈单'的数量来判断当前是否还有持仓!!!
                - 新k线生产后的流程:
                    1. 止盈挂单的撤单后, 重新挂单
                    2. 判断止损单是否能市价止损
                - 一旦发现止盈单被成交, 便从'stop_profit_order_dict'字典中删掉该止盈单 (该字典只存放'未成交的挂单')
                - 同理: 一旦止损单市价吃掉, 便从'stop_profit_order_dict'字典中删掉所有止盈单 (该字典只存放'未成交的挂单')
        """
        # 0. 初始化
        tick_signals = []
        tick_price = self.tick.price  # 这是实时价
        bars = self.bars  # 第一次运行时候self.bars为空
        if not bars:
            return tick_signals

        # 可删除
        # run_time = self._get_running_num()  # 一天开仓次数
        # 1. 获取必要指标
        if bars[-1] != self.old_bar:
            order_lst = self.is_close_order_done()  # 根据订单记录，判断一笔订单是否完结了
            self.position_new_flag = self.get_position_new_flag(order_lst)  # 返回持仓信息
            self.trade.is_order_profit_or_loss(order_lst)  # 开仓后是盈利还是亏损
            self.get_all_indicators()  # 计算所有的指标
            self.open_bar_signal = self.get_open_indicators()  # 计算开仓的信号
            self.close_bar_signal = self.get_close_indicators()  # 计算平仓的信号
            self.old_bar = bars[-1]

        # 计算tick的实时信号
        open_tick_signal = self.get_open_indicators('tick')
        close_tick_signal = self.get_close_indicators('tick')

        # 当判断到了持仓刷新
        if self.refresh_position:
            order_lst = self.is_close_order_done()  # 根据订单记录，判断一笔订单是否完结了
            self.position_new_flag = self.get_position_new_flag(order_lst)  # 返回持仓信息
            self.trade.is_order_profit_or_loss(order_lst)  # 开仓后是盈利还是亏损
            self.refresh_position = False

        # 2. 开仓操作
        if (open_tick_signal['buy'] or self.open_bar_signal['buy']) and self.position_new_flag == 0:
            # 若'做多开关'开启, 允许做多:
            if self.buy_trading_toggle.toggle:  # 做多开关开启，
                # 市价开仓做多
                tick_signal = self.post_trade_signal(offset='open', direction='buy', trade_rate=1)
                # 将开仓时候的止盈价保存下来
                self.stop_profit_maker_sell_price = self.sell_profit_price
                tick_signals.append(tick_signal)  # 将开仓单的信息加入到开仓列表里面
                return tick_signals

        elif (open_tick_signal['sell'] or self.open_bar_signal['sell']) and self.position_new_flag == 0:
            # 若'做空开关'开启, 允许做空:
            if self.sell_trading_toggle.toggle:
                # 市价开仓做空
                tick_signal = self.post_trade_signal(offset='open', direction='sell', trade_rate=1)
                # 将开仓时候的止盈价保存下来
                self.stop_profit_maker_buy_price = self.buy_profit_price
                tick_signals.append(tick_signal)
                return tick_signals

        # 3. 平仓操作
        if self.position_new_flag:
            # 当持有空单，发出平空，close， buy信号
            if (close_tick_signal['buy'] or self.close_bar_signal['buy']) and self.position_new_flag < 0:
                tick_signal = self.post_trade_signal(offset='close', direction='buy', trade_rate=1)
                tick_signals.append(tick_signal)
                return tick_signals

            # 当持有多单，发出平多， close ，sell信号
            elif (close_tick_signal['sell'] or self.close_bar_signal['sell']) and self.position_new_flag > 0:
                tick_signal = self.post_trade_signal(offset='close', direction='sell', trade_rate=1)
                tick_signals.append(tick_signal)
                return tick_signals
        return tick_signals

    def get_tick_signals(self):
        """
        获取 tick 的信号
        """
        self.tick.signals = []
        tick_signals = self._get_tick_signals()
        self.tick.signals.extend(tick_signals)

    def process_tick_signals(self):  # tick的开仓信号
        """
        处理 tick 的信号
        """
        super().process_tick_signals()

        # 遍历'tick的开仓信号'
        for _ in range(len(self.tick.signals)):
            # self.GF.Log(self.tick.signals)
            signal = self.tick.signals.pop(0)
            signal["exchange"] = GF.exchange
            # self.GF.Log(signal)
            signal_type = signal.pop("signal_type")
            if signal_type == "open_order":
                self.trade.open_order(**signal)
            elif signal_type == "close_order":
                self.trade.close_order(**signal)

    def get_bar_signals(self):  # 收盘的开仓信号
        """
        获取 bar 的信号
        """
        self.bar.signals = []
        # bar_signals = self._get_bar_signals()
        # self.bar.signals.extend(bar_signals)

    def process_bar_signals(self):
        """
        处理 bar 的信号
        """
        super().process_bar_signals()
        # 遍历'bar的开仓信号'
        for _ in range(len(self.bar.signals)):
            signal = self.bar.signals.pop(0)
            # signal["exchange"] = GF.exchange
            # print(signal)
            # signal_type = signal.pop("signal_type")
            # if signal_type == "open_order":
            #     self.trade.open_order(**signal)

    def draw(self, bars, draw_all=True):  # 画图的函数，应该要一个一个添加
        # 继承父类
        super().draw(bars, draw_all=draw_all)

        # 画网格线
        if self.all_grid:
            self.chart.fmz_chart.add(self.chart.get_series_index(self.chart.chart_config, "网格下轨"),
                                     [self.bar.time, self.all_grid['down']])
            self.chart.fmz_chart.add(self.chart.get_series_index(self.chart.chart_config, "网格上轨"),
                                     [self.bar.time, self.all_grid['up']])

    def trans_f_to_s(self, filters):
        """肯定器和否定器的解释
        为了规范理解，如下约定
        约定：
            1. 肯定器是: 1 表示肯定，0 表示否定
            2. 否定器: 1 代表否定， 0 表示肯定
            3. 方向器: 1 表示只能做多， -1 表示只能做空， 0 表示可以多空
        """
        pos_neg_signal = 0
        director_signal = 0

        affirmer_flags = []  # 肯定器列表
        negetor_flags = []  # 否定器列表
        director_flags = []  # 方向器列表（1 代表只能多， 0 可以空）

        def muti(x, y):
            return x * y

        def sum(x, y):
            return x + y

        # 1.过滤分类，过滤器的 flag 值集合
        for f_name, filter in filters.items():
            if filter.filter_type == "Affirmer":
                affirmer_flags.append(filter.flag)
            elif filter.filter_type == "Negator":
                if f_name == "FilterSidewaySar":  # dirty code 遗留问题
                    sar_flag = 0 if filter.flag == 1 else 1
                    negetor_flags.append(sar_flag)
                else:
                    negetor_flags.append(filter.flag)
            elif filter.filter_type == "Director":
                if f_name == "FilterEma":  # dirty code 遗留问题
                    director_flags.append(0)
                else:
                    director_flags.append(filter.flag)
        self.GF.Logger.log(f"肯定器:{affirmer_flags} 否定器: {negetor_flags} 方向器:{director_flags}.....", 50)

        # 2. 对肯定器和否定器的集合做布尔计算
        # 当2个都有的时候
        self.log(f"affirmer_flags{affirmer_flags}, negetor_flags{negetor_flags}", 50)
        if affirmer_flags and negetor_flags:
            # 当肯定器为1，否定器为0时，才可以开仓，其他均不能开仓
            if reduce(sum, affirmer_flags) and reduce(sum, negetor_flags) == 0:
                pos_neg_signal = 1
            else:
                pos_neg_signal = 0
        # 当只有肯定器
        elif affirmer_flags and len(negetor_flags) == 0:
            if reduce(sum, affirmer_flags):
                pos_neg_signal = 1
            else:
                pos_neg_signal = 0
        # 当只有否定器
        elif len(affirmer_flags) == 0 and negetor_flags:
            if reduce(sum, negetor_flags) == 0:
                pos_neg_signal = 1
            else:
                pos_neg_signal = 0
        # 当2个都没有
        elif len(affirmer_flags) ==0 and len(negetor_flags)==0:
            pos_neg_signal = 1

        # 3. 对方向过滤器做计算
        if director_flags:
            if len(set(director_flags)) == 1:  # 方向过滤器
                director_signal = director_flags[0]  # 开仓方向的信号
            else:
                raise Exception("the director error ......")
        return pos_neg_signal, director_signal

    def through_filters(self, bars):
        "在执行策略之前, 统一处理过滤器的信号"
        for filter_name, filter in self.filters.items():
            filter.on_bars(bars)
        open_pos_signal, director_signal = self.trans_f_to_s(self.filters)
        self.GF.Logger.log(f"获取开仓信号： {open_pos_signal}", 50)
        if not open_pos_signal:
            self.trading_toggle.close(1)

        if director_signal == 1:
            self.sell_trading_toggle.close(1)
        elif director_signal == -1:
            self.buy_trading_toggle.close(1)
        elif director_signal == 0:
            pass

    def through_the_filter(self, bars):
        "在完结一笔订单之后，进行亏损否定器的判断，但是他的次数要+1，因为多运行了一次"
        order_filter = ["FilterConLossNegator"]
        for filter_name, filter in self.filters.items():
            if filter_name in order_filter:
                filter.on_bars(bars)
        open_pos_signal, director_signal = self.trans_f_to_s(self.filters)
        self.GF.Logger.log(f"获取开仓信号： {open_pos_signal}", 50)
        if not open_pos_signal:
            self.trading_toggle.close(1)
        if director_signal == 1:
            self.sell_trading_toggle.close(1)
        elif director_signal == -1:
            self.buy_trading_toggle.close(1)
        elif director_signal == 0:
            pass


class TradeWave(BaseTrade):
    # 可调参数
    parameters = [
        "base_qty",
        "quote_qty",
        "trading_toggle",
        "trade_type",
        "stop_loss_type",
    ]
    # 全局变量
    variables = []

    def __init__(self, strategy_inst):
        super().__init__(strategy_inst=strategy_inst)

        self.strategy = strategy_inst
        self.GF = self.strategy.GF
        self.fmz_order_id_lst = []  # 包含所有fmz订单的id
        self.fmz_order_dict_lst = []  # 包含所有fmz订单的dict
        self.strategy_trade_id = 0  # 策略逻辑内的trade_id (成交的id)
        self.strategy_trade_dict_lst = []  # 包含策略逻辑内的所有strategy_trade_dict
        self.strategy_trade_dict_dict = {}  # 包含策略逻辑内的所有strategy_trade_dict

        # 4个持仓标识
        self.position_flag = 0
        self.stop_profit_maker_order_lst = []  # 止盈委托单的'未成交'的订单列表
        self.stop_loss_bar_order_lst = []  # K线完结止损订单
        self.stop_loss_tick_order_lst = []  # tick信号实时止损

        # 挂单的订单列表
        self.open_maker_order_lst = []  # 开仓挂单
        self.close_maker_order_lst = []  # 平仓挂单
        self.log = self.GF.Logger.log

    def reset_position_flag(self):  #
        """
            策略逻辑内的一个订单'已经完结', 重置各种'持仓标识'
        """
        self.position_flag = 0  # '持仓标识'变为空仓。因为之前使用的时候有bug，所以就没有用了自己写了个
        self.cancel_stop_profit_orders()
        self.cancel_stop_loss_orders()
        self.strategy.refresh_position = True

    def is_order_profit_or_loss(self, new_order):
        '''根据已完成的一笔订单的最后一笔，查询订单是止盈还是止损，
           打印成交信息，根据成交信息输出是亏损还是盈利多少百分比
           【注：】只适合单项持仓的订单查询，多次开仓会失效，因为是根据订单的长度来的
        '''
        order_status = {}  # 已完结订单的止盈止损情况
        is_get_new_order = False
        # 根据已经添加到订单列表的order_id来选择订单
        order_id = self.strategy_trade_id
        if len(new_order) == 2 and order_id not in self.strategy.old_order_lst:
            # self.GF.Log(f"{new_order}")
            is_get_new_order = True
            self.strategy.old_order_lst.append(order_id)
            if len(self.strategy.old_order_lst) > 10:
                self.strategy.old_order_lst.pop(0)

        # 如果产生新的key,且新的订单必须完结
        # self.log(order_dict)
        if is_get_new_order:
            # 打印订单记录
            order0 = dict(
                zip(['offset', 'direction', 'price', 'base_qty'],
                    [new_order[0]['offset'], new_order[0]['direction'], new_order[0]['price'], new_order[0]['base_qty']]))
            order1 = dict(
                zip(['offset', 'direction', 'price', 'base_qty'],
                    [new_order[1]['offset'], new_order[1]['direction'], new_order[1]['price'], new_order[1]['base_qty']]))

            # 进行止盈还是止损的判断
            if new_order[0]['direction'] == 'buy' and new_order[1]['direction'] == 'sell':  # 开多，平多
                # 开仓价大于平仓价，该订单止损
                order_status['loss'] = True if new_order[0]['price'] >= new_order[1]['price'] else False
                # 开仓价小于平仓价，该订单止盈
                order_status['profit'] = True if new_order[0]['price'] < new_order[1]['price'] else False

                # 计算盈亏的百分比
                m = (new_order[1]['price'] - new_order[0]['price']) / new_order[0]['price'] * 100
                self.log(f'做多{"亏损" if m < 0 else "盈利"}{self.GF._N(m,2)}%', 90)

            elif new_order[0]['direction'] == 'sell' and new_order[1]['direction'] == 'buy':  # 开空，平空
                # 开仓价大于平仓价，该订单止损
                order_status['profit'] = True if new_order[0]['price'] > new_order[1]['price'] else False
                # 开仓价小于平仓价，该订单止盈
                order_status['loss'] = True if new_order[0]['price'] <= new_order[1]['price'] else False

                # 计算盈亏的百分比
                m = (new_order[0]['price'] - new_order[1]['price']) / new_order[0]['price'] * 100
                self.log(f'做空{"亏损" if m < 0 else "盈利"}{self.GF._N(m,2)}%', 90)

            # 掉收益率进行计算，如果大于0，就是盈亏，小于0就是亏损
            if m > 0:
                self.pm.update(op="increase")  # 更新'每次下单金额'
            elif m <= 0:
                self.pm.update(op="reset")  # 更新'每次下单金额'
                # 禁止开仓 (默认10次)
                self.strategy.trading_toggle.close()

            self.log(f'成交明细, {order0}, {order1}', 90)
            self.end_of_close_position()
            self.strategy.show_profit()  # 显示收益曲线
            # self.strategy.running_num += 1
            self.strategy.through_the_filter(self.strategy.bars)
            self.log(f'=' * 50, 90)

    def end_of_close_position(self):
        """一笔订单结束，判断挂单信息和持仓信息，进行撤单，并对持仓进行平仓
        """
        # 查询挂单，如果有，就进行撤单
        all_orders = self.GF.exchange.GetOrders()
        for order in all_orders:
            self.log(f"有挂单，进行撤单操作", 100)
            self.cancel_order(order_id=order['Id'], exchange=GF.exchange)  # 撤单
        futures_base_qty_total = self.get_futures_base_qty_total(exchange=GF.exchange)
        if futures_base_qty_total < 0:
            direction = 'buy'
        elif futures_base_qty_total > 0:
            direction = 'sell'
        futures_base_qty_total = abs(futures_base_qty_total)
        if futures_base_qty_total != 0:
            self.log(f'持仓不为0，进行平仓操作', 100)
            self.send_order(offset="close", direction=direction, price=-1, base_qty=futures_base_qty_total, exchange=GF.exchange)

    def open_order(self, offset, direction, price, base_qty, exchange=None, **kwargs):
        # if offset == 'open':
        #     base_qty = self.get_base_qty(base_qty=self.strategy.base_qty, quote_qty=self.strategy.trade.pm.quote_qty)
        # elif offset == 'close':
        #     base_qty = abs(self.get_futures_base_qty_total(exchange=exchange))
        open_price = self.strategy.tick.price
        if self.trading_toggle.toggle and base_qty:
            if direction == "buy" and offset == 'open' and self.strategy.buy_trading_toggle.toggle:
                # 开多下单:
                self.log(f'开仓触发价：, {open_price}', 90)
                # base_qty = self.get_base_qty(base_qty=self.strategy.base_qty, quote_qty=self.strategy.trade.pm.quote_qty)
                order_id = self.send_order(offset=offset, direction=direction, price=price, base_qty=base_qty, exchange=exchange)
                # 记录交易信息
                self.record_strategy_trade(order_id=order_id, offset=offset, direction=direction, price=price, base_qty=base_qty)

                # 挂单止盈
                stop_profit_maker_price = self.strategy.stop_profit_maker_sell_price
                self.stop_profit_maker(direction="sell", price=stop_profit_maker_price, base_qty=base_qty, exchange=GF.exchange)

                # 止损:
                stop_loss_base_qty = base_qty
                stop_loss_bar_price = open_price * (1 - self.strategy.grid_ratio / 2)  # grid_ratio/2 代表收盘止损比例
                stop_loss_tick_price = open_price * (1 - self.strategy.grid_ratio)     # grid_ratio 代表瞬间止损比例
                self.log(f'收盘止损bar, {stop_loss_bar_price}', 90)
                self.log(f'瞬间止损tick, {stop_loss_tick_price}', 90)
                self.stop_loss(
                    direction="sell",
                    stop_loss_type=self.stop_loss_type,
                    stop_loss_base_qty=stop_loss_base_qty,
                    stop_loss_bar_price=stop_loss_bar_price,
                    stop_loss_tick_price=stop_loss_tick_price,
                )

            elif direction == "sell" and offset == "open" and self.strategy.sell_trading_toggle.toggle:
                # 开空下单:
                # open_price = self.strategy.tick.price
                self.log(f'开仓触发价：, {open_price}', 90)
                # base_qty = self.get_base_qty(base_qty=self.strategy.base_qty, quote_qty=self.strategy.trade.pm.quote_qty)
                order_id = self.send_order(offset=offset, direction=direction, price=price, base_qty=base_qty, exchange=exchange)
                # 记录交易信息
                self.record_strategy_trade(order_id=order_id, offset=offset, direction=direction, price=price, base_qty=base_qty)

                # 挂单止盈
                stop_profit_maker_price = self.strategy.stop_profit_maker_buy_price
                self.stop_profit_maker(direction="buy", price=stop_profit_maker_price, base_qty=base_qty, exchange=GF.exchange)

                # 止损:
                stop_loss_base_qty = base_qty
                stop_loss_bar_price = open_price * (1 - self.strategy.grid_ratio / 2)
                stop_loss_tick_price = open_price * (1 - self.strategy.grid_ratio)
                self.log(f'收盘止损bar, {stop_loss_bar_price}', 90)
                self.log(f'瞬间止损tick, {stop_loss_tick_price}', 90)
                self.stop_loss(
                    direction="buy",
                    stop_loss_type=self.stop_loss_type,
                    stop_loss_base_qty=stop_loss_base_qty,
                    stop_loss_bar_price=stop_loss_bar_price,
                    stop_loss_tick_price=stop_loss_tick_price,
                )

    def close_order(self, offset, direction, price, base_qty, exchange=None, **kwargs):
        # 止盈挂单，止损市价成交
        # 先把止盈单撤销
        cancel_success = self.cancel_stop_profit_orders(exchange=exchange)
        if not cancel_success:
            return
        if direction == "sell" and offset == 'close':
            # base_qty = abs(self.get_futures_base_qty_total(exchange=exchange))
            self.log(f'平仓触发价：, {self.strategy.tick.price}', 90)
            order_id = self.send_order(offset=offset, direction=direction, price=price, base_qty=base_qty, exchange=exchange)
            # 记录交易信息
            self.record_strategy_trade(order_id=order_id, offset=offset, direction=direction, price=price, base_qty=base_qty)
            self.reset_position_flag()
            # self.pm.update(op="reset")  # 更新'每次下单金额'

        elif direction == "buy" and offset == 'close':
            # base_qty = abs(self.get_futures_base_qty_total(exchange=exchange))
            self.log(f'平仓触发价：, {self.strategy.tick.price}', 90)
            order_id = self.send_order(offset=offset, direction=direction, price=price, base_qty=base_qty, exchange=exchange)
            # 记录交易信息
            self.record_strategy_trade(order_id=order_id, offset=offset, direction=direction, price=price, base_qty=base_qty)
            self.reset_position_flag()
            # self.pm.update(op="reset")  # 更新'每次下单金额'

    # 重写父类的止损方法，去掉了止损后更新仓位
    def check_stop_loss_bar(self, exchange=None):
        """修改父类,去掉了止损后更新仓位
            检查是否满足'收盘止损单'止损条件
                若满足条件: 则以'市价'立马止损
        """
        # 打印排错
        GF.Logger.log(f"未成交的收盘止损单:{self.stop_loss_bar_order_lst}", 10)

        close_price = self.strategy.bar.close_price
        futures_base_qty_total = abs(self.get_futures_base_qty_total(exchange=exchange))
        for stop_loss_bar_order_info in self.stop_loss_bar_order_lst:
            """
            # 如果按钮为2，就把实时的boll中轨价格赋值给stop_loss_bar_order_info["price"]
            # self.log(f"{self.stop_loss_bar_order_lst}",100)
            if self.choose_stop_loss_bar_button == 2:
                if self.strategy.bars:
                    boll = self.strategy.cache_boll_data(self.strategy.bars)
                    stop_loss_bar_order_info["price"] = round(boll[1][-1], 2)
                    # self.log(f"实时的收盘布林中轨止损价{round(boll[1][-1],2)}", 100)
            # self.log(f"{self.stop_loss_bar_order_lst}", 100)
            """
            stop_loss_bar_price = stop_loss_bar_order_info["price"]
            direction = stop_loss_bar_order_info["direction"]
            base_qty = stop_loss_bar_order_info["base_qty"]
            if direction == "sell":
                # 若收盘价低于止损价, 市价卖出止损
                if close_price <= stop_loss_bar_price:
                    # 先把止盈单撤销
                    cancel_success = self.cancel_stop_profit_orders(exchange=exchange)
                    if not cancel_success:
                        return
                    # 再市价止损
                    self.log(f'收盘价止损的实时价：, {self.strategy.tick.price}', 90)
                    order_id = self.send_order(offset="close",
                                               direction=direction,
                                               price=-1,
                                               base_qty=futures_base_qty_total,
                                               exchange=exchange)
                    self.record_strategy_trade(order_id=order_id,
                                               offset="close",
                                               direction=direction,
                                               price=-1,
                                               base_qty=futures_base_qty_total,
                                               stop_type="stop_loss")
                    self.reset_position_flag()
                    # self.pm.update(op="increase")  # 更新'每次下单金额'
                    # 禁止开仓 (默认10次)
                    # self.strategy.trading_toggle.close()
            elif direction == "buy":
                # 若收盘价高于止损价, 市价买入止损
                if close_price >= stop_loss_bar_price:
                    # 先把止盈单撤销
                    cancel_success = self.cancel_stop_profit_orders(exchange=exchange)
                    if not cancel_success:
                        return
                    # 再市价止损
                    self.log(f'收盘价止损的实时价：, {self.strategy.tick.price}', 90)
                    order_id = self.send_order(offset="close",
                                               direction=direction,
                                               price=-1,
                                               base_qty=futures_base_qty_total,
                                               exchange=exchange)
                    self.record_strategy_trade(order_id=order_id,
                                               offset="close",
                                               direction=direction,
                                               price=-1,
                                               base_qty=futures_base_qty_total,
                                               stop_type="stop_loss")
                    self.reset_position_flag()
                    # self.pm.update(op="increase")  # 更新'每次下单金额'
                    # 禁止开仓 (默认10次)
                    # self.strategy.trading_toggle.close()

    def check_stop_loss_tick(self, exchange=None):
        """修改父类,去掉了止损后更新仓位
            检查是否满足'瞬时止损单'止损条件
                - 若满足条件: 则以'市价'瞬时止损
        """
        # 打印排错
        GF.Logger.log(f"未成交的瞬间止损单:{self.stop_loss_tick_order_lst}", 10)
        latest_price = self.strategy.tick.price
        futures_base_qty_total = abs(self.get_futures_base_qty_total(exchange=exchange))

        for stop_loss_tick_order_info in self.stop_loss_tick_order_lst:
            stop_loss_tick_price = stop_loss_tick_order_info["price"]
            direction = stop_loss_tick_order_info["direction"]
            base_qty = stop_loss_tick_order_info["base_qty"]
            if direction == "sell":
                # 若'最新价'低于止损价, 市价卖出止损 (全部仓位止损)
                if latest_price <= stop_loss_tick_price:
                    # 先把止盈单撤销
                    cancel_success = self.cancel_stop_profit_orders(exchange=exchange)
                    if not cancel_success:
                        return
                    # 再市价止损
                    self.log(f'瞬间止损价：, {latest_price}', 90)
                    order_id = self.send_order(offset="close",
                                               direction=direction,
                                               price=-1,
                                               base_qty=futures_base_qty_total,
                                               exchange=exchange)
                    self.record_strategy_trade(order_id=order_id,
                                               offset="close",
                                               direction=direction,
                                               price=-1,
                                               base_qty=futures_base_qty_total,
                                               stop_type="stop_loss")
                    self.reset_position_flag()
                    # self.pm.update(op="increase")  # 更新'每次下单金额'
                    # 禁止开仓 (默认10次)
                    # self.strategy.trading_toggle.close()
            elif direction == "buy":
                # 若'最新价'高于止损价, 市价买入止损 (全部仓位止损)
                if latest_price >= stop_loss_tick_price:
                    # 先把止盈单撤销
                    cancel_success = self.cancel_stop_profit_orders(exchange=exchange)
                    if not cancel_success:
                        return
                    # 再市价止损
                    self.log(f'瞬间止损价：, {latest_price}', 90)
                    order_id = self.send_order(offset="close",
                                               direction=direction,
                                               price=-1,
                                               base_qty=futures_base_qty_total,
                                               exchange=exchange)
                    self.record_strategy_trade(order_id=order_id,
                                               offset="close",
                                               direction=direction,
                                               price=-1,
                                               base_qty=futures_base_qty_total,
                                               stop_type="stop_loss")
                    self.reset_position_flag()
                    # self.pm.update(op="increase")  # 更新'每次下单金额'
                    # 禁止开仓 (默认10次)
                    # self.strategy.trading_toggle.close()

    def send_order(self, offset="open", direction="buy", price=-1, base_qty=0, exchange=None):
        """修改父类，增加下单精度，休眠，打印订单id
        args:
            price:
                -1: 表示市价下单
                正数: 表示限价下单
            base_qty:
                这里传入的参数统一指代'币'的base_qty
            quote_qty:
                交易金额 (主要用USDT来计价)
            check:
                是否需要检验下单成功: True/False
        [注意]:
            - send_order 的前置操作: 往往会有 get_base_qty()
        """
        # base_qty = self.get_base_qty(base_qty=base_qty, quote_qty=self.strategy.tick.price * base_qty)

        # 对下单的价格和数量做精度处理
        base_qty = self.GF._N(base_qty, self.strategy.asset_precision)
        price = self.GF._N(price, self.strategy.price_precision)

        if direction == "buy":
            if offset == "open":  # 开仓
                self.GF.Logger.log(f"[开多]: 价格:{price}; 数量:{base_qty}", 30)
                exchange.SetDirection("buy")
                order_id = exchange.Buy(price, base_qty)
                self.strategy.chart.draw_operation(price=price, name="开多", draw_offset=0.998)
            elif offset == "close":  # 平仓
                self.GF.Logger.log(f"[平空]: 价格:{price}; 数量:{base_qty}", 30)
                exchange.SetDirection("closesell")
                order_id = exchange.Buy(price, base_qty)
                self.strategy.chart.draw_operation(price=price, name="平空", draw_offset=1.001)  # 平仓暂时不画图, 后期待优化

        elif direction == "sell":
            if offset == "open":  # 开仓
                self.GF.Logger.log(f"[开空]: 价格:{price}; 数量:{base_qty}", 30)
                exchange.SetDirection("sell")
                order_id = exchange.Sell(price, base_qty)
                self.strategy.chart.draw_operation(price=price, name="开空", draw_offset=1.002)
            elif offset == "close":  # 平仓
                self.GF.Logger.log(f"[平多]: 价格:{price}; 数量:{base_qty}", 30)
                exchange.SetDirection("closebuy")
                order_id = exchange.Sell(price, base_qty)
                self.strategy.chart.draw_operation(price=price, name="平多", draw_offset=0.999)  # 平仓暂时不画图, 后期待优化

        self.strategy.refresh_position = True
        self.GF.Sleep(3000)
        self.log(f'order_id:{order_id}', 100)
        return order_id

    def check_order_status(self, order_id):
        """
            修改父类,反复获取订单的'成交状态'
        """
        fmz_order_dict = self.GF._C(GF.exchange.GetOrder, order_id)
        self.log(f'查询的订单:{fmz_order_dict}', 100)
        Amount = fmz_order_dict["Amount"]
        DealAmount = fmz_order_dict["DealAmount"]
        if DealAmount == Amount:
            order_status = "all_traded"  # 全部成交
        elif DealAmount == 0:
            order_status = "not_traded"  # 无成交
        else:
            order_status = "part_traded"  # 部分成交
        return order_status

    def cancel_order(self, order_id, exchange=None):
        "修改父类，增加休眠,当策略开始新的一单时, 启动该方法"
        self.log(f"撤销的订单，{order_id}", 90)
        order_id = exchange.CancelOrder(order_id)
        self.GF.Sleep(2000)
        return order_id

    def get_futures_base_qty_total(self, exchange):
        "修改父类,获取合约账户, '该币种'的仓位的总数量 (多头为正, 空头为负)"
        "futures_base_qty: 指合约账户的'标的资产'的仓位数量"
        account_info = self.get_account_info(exchange=exchange)
        position_lst = account_info["position_lst"]
        # 打印持仓信息
        #为空的时候，只打印一次
        if not position_lst and not self.strategy.print_account_info2:
            self.log(f"position_lst{position_lst}", 90)
            self.log(f"account_info{account_info}", 90)
            self.strategy.print_account_info2 = 1
        # 有数据时候，打印一次，并将为空的打印限制去掉
        if position_lst and position_lst[-1].get('futures_base_qty', 0) != self.strategy.print_account_info:
            self.log(f"position_lst{position_lst}", 90)
            self.log(f"account_info{account_info}", 90)
            self.strategy.print_account_info = position_lst[-1].get('futures_base_qty', 0)
            self.strategy.print_account_info2 = 0
        futures_base_qty_total = 0
        for position_dict in position_lst:
            futures_base_qty = position_dict["futures_base_qty"]
            direction = position_dict["direction"]
            if direction == "多头":
                futures_base_qty_total += futures_base_qty
            elif direction == "空头":
                # 修改框架里面的计算方式
                futures_base_qty_total += futures_base_qty

        return futures_base_qty_total

    def get_account_info(self, exchange):
        """获取账户的持仓信息，修改父类
        """
        symbol, full_symbol, base_asset, quote_asset = UTILS.get_symbol(exchange)
        # self.GF.Log(f"symbol:{symbol}")
        account_dict = GF._C(exchange.GetAccount)
        # self.GF.Log(f"account_dict:{account_dict}")
        exchange_name = GF._C(exchange.GetName)
        # self.GF.Log(f"exchange_name:{exchange_name}")
        exchange_name_prefix = exchange_name.split("_")[0]  # 交易所的前缀  （期货的话前面会带有‘Futures’）
        if exchange_name_prefix == "Futures":
            # self.GF.Log(f"进入Futures...")
            #position_dict = exchange.GetPosition()[0] if exchange.GetPosition() else {}
            #contract_type = exchange.GetContractType()
            # contractType即使是合约， 若当前没有仓位的话，还是会返回空[]
            position_dict_lst = GF._C(exchange.GetPosition) if GF._C(exchange.GetPosition) else []
            # self.GF.Log(f"position_dict_lst:{position_dict_lst}")
            contract_type = GF._C(exchange.GetContractType)
            # self.GF.Log(f"contract_type:{contract_type}")
        else:
            position_dict_lst = []
            contract_type = ""

        # 1. 余额：
        # 如果account_type 是'futures', 这里的balance也是指'合约账户'的余额!!
        quote_qty = account_dict.get("Balance")
        quote_qty_frozen = account_dict.get("FrozenBalance")
        # 2. 币数：(这里特指现货， 所以合约的持仓量不会显示在这里）
        base_qty = account_dict.get("Stocks")
        base_qty_frozen = account_dict.get("FrozenStocks")
        account_info = {
            "contract_type": contract_type,
            "full_symbol": full_symbol,
            "symbol": symbol,
            "quote_asset": quote_asset,
            "quote_qty": quote_qty,
            "quote_qty_frozen": quote_qty_frozen,  # 合约账户的现金余额
            # '标的资产'的数据 (只有'现货账户'才有, '合约账户'这个数据为空, 忽略)
            "base_qty": base_qty,
            "base_qty_frozen": base_qty_frozen,
        }

        position_lst = []
        # 3. 仓位：
        if contract_type:  # 若是合约账户:
            for position_dict in position_dict_lst:
                amount = position_dict.get("Amount", 0)
                frozen_amount = position_dict.get("FrozenAmount", 0)
                flag = position_dict.get("Type", 0)
                if flag == 0:  # 0表示正值
                    position_direction = "多头"
                    pass
                elif flag == 1:  # 1表示负值
                    position_direction = "空头"
                    amount = amount * -1
                    frozen_amount = frozen_amount * -1
                margin_level = position_dict.get("MarginLevel", 0)
                margin = position_dict.get("Margin", 0)
                floating_profit = position_dict.get("Profit", 0)
                _d = {
                    "direction": position_direction,
                    "margin": margin,
                    "margin_level": margin_level,
                    "futures_base_qty": amount,
                    "futures_base_qty_frozen": frozen_amount,
                    "floating_profit": floating_profit,
                }
                position_lst.append(_d)

        account_info.update({"position_lst": position_lst})
        return account_info

    def record_strategy_trade(self, order_id, offset, direction, price, base_qty, **kwargs):
        """重写父类，增加多笔订单的判断，不会每次出现open的时候，将id+1

            tips:
                - 默认: 若原本就有仓位, 必须要先平完所有仓位后, 才会再重新开仓!! (基本原则!)
        """
        # 订单成交状态
        order_status = self.check_order_status(order_id=order_id)
        if order_status != "all_traded":
            msg = f"[订单未全部成交] order_status:{order_status}"
            raise Exception(msg)
        # 新的订单'已经全部成交'
        else:
            # 1. 添加order_id
            self.fmz_order_id_lst.append(order_id)
            """下面的position_flag可以用可以不用，要用的话，就按照策略的逻辑来，或者修改上方
            的get_position_new_flag()函数
            """
            # 2. 修改'position_flag'
            # if offset == "open":
            #     if direction == "buy":
            #         self.position_flag += 1
            #     elif direction == "sell":
            #         self.position_flag -= 1
            # elif offset == "close":
            #     stop_type = kwargs.get("stop_type")
            #     if direction == "buy":
            #         self.position_flag += 1
            #     elif direction == "sell":
            #         self.position_flag -= 1

            # 3. 标记为新的一单 (策略逻辑内的自定义的'一单'),且将订单id+1后获取到的长度为0时，才标记为新的一笔
            if offset == "open" and (not self.strategy_trade_dict_dict or self.strategy_trade_dict_dict
                                     and not self.strategy_trade_dict_dict.get(self.strategy_trade_id + 1)):
                self.strategy_trade_id += 1
            # 4. 添加 strategy_trade_dict
            # i. 市价: 获得真实的成交价格!
            if price == -1:
                # 市价下单需要获取当前的价格 (但是还有个问题: 当前价格和实际成交价格可能是不一样! [待优化])
                # todo: 后续用 'Exchange.GetOrder(order_id)' 来获取真实成交的'量/价' // [坑点]: 市价单得到的price会显示为0....
                # // 最新更新: 可以通过'AvgPrice'的key获取到
                fmz_order_dict = self.GF.exchange.GetOrder(order_id)
                price = fmz_order_dict["AvgPrice"]
                # price = self.strategy.tick.price
                # ii. 记录strategy_trade_dict
            if direction == "sell":
                base_qty = -base_qty  # 卖出的话标记为'负值'
            strategy_trade_dict = {
                "time": self.strategy.bar.time,
                "strategy_trade_id": self.strategy_trade_id,  # 策略逻辑内的订单id
                "order_id": order_id,  # 服务器返回的订单id
                "offset": offset,
                "direction": direction,
                "price": price,
                "base_qty": base_qty,
                "stop_type": kwargs.get("stop_type", None),
            }
            # 计算每单利润 [待优化: 目前写得过于凌乱...]

            self.strategy_trade_dict_lst.append(strategy_trade_dict)
            if self.strategy_trade_dict_dict.get(self.strategy_trade_id):
                self.strategy_trade_dict_dict[self.strategy_trade_id].append(strategy_trade_dict)
            else:
                self.strategy_trade_dict_dict[self.strategy_trade_id] = [strategy_trade_dict]

    def get_future_quote_qty_tatal(self):
        """获取账户的USDT的总数，模拟盘：可用+冻结,并对实盘与回测进行分开处理
        """
        marginBalance = 0
        account = GF._C(GF.exchange.GetAccount)
        # 模拟盘回测运行的数据
        if 'Info' not in account:
            marginBalance = account['Balance'] + account['FrozenBalance']
        # 实盘运行的数据
        elif account and 'Info' in account:
            marginBalance = account['Info']['assets'][1]['marginBalance']  # USDT的账户资产
        # 对实盘的异常做处理，有时候没正常获取到数据
        if marginBalance == 0:
            self.GF.Sleep(10 * 1000)
            account = GF._C(GF.exchange.GetAccount)
            marginBalance = account['Info']['assets'][1]['marginBalance']
        marginBalance = GF._N(float(marginBalance), 2)
        self.log(f"marginBalance:{marginBalance}", 100)
        return marginBalance


class AnalysisWave(BaseAnalysis):
    parameters = ["maker_fee_rate", "taker_fee_rate"]
    variables = []

    def __init__(self, strategy_inst):
        super().__init__(strategy_inst=strategy_inst)
        self.strategy = strategy_inst
        self.GF = self.strategy.GF
        self.period_info_lst = []  # 收集所有日常资产数据
        self.log = self.strategy.GF.Logger.log

    def statistics(self):
        "统计盈亏数据"

        def _get_prefix():
            doc = self.doc
            # self.GF.Log({type(doc)}, {doc})
            start_date_time = re.findall("start: (.*?)\n", doc)[-1]  # '2021-05-03 03:00:00'
            # self.GF.Log({start_date_time})
            end_date_time = re.findall("end: (.*?)\n", doc)[-1]
            start_date = "".join(start_date_time.split(" ")[0].split("-"))  # '20210503'
            end_date = "".join(end_date_time.split(" ")[0].split("-"))
            file_name_prefix = f"{start_date}_{end_date}"
            return file_name_prefix

        # 得到文件前缀名
        prefix = _get_prefix()

        # 得到 period_df
        period_df = self._get_period_df()
        period_df.to_csv(f"{prefix}_每周期资产涨跌表.csv", index=False, encoding="gb18030")

        # 得到 daily_df
        daily_df = self._get_daily_df(period_df)
        daily_df.to_csv(f"{prefix}_每日资产涨跌表.csv", index=False, encoding="gb18030")
        daily_df.to_csv(f"每日资产涨跌表.csv", index=False, encoding="gb18030")
        # self.log(f"每日资产{daily_df.head()}", 100)

        # 得到 final_trade_df
        final_trade_df = self._get_final_trade_df()
        final_trade_df.to_csv(f"{prefix}_所有交易记录表.csv", index=False, encoding="gb18030")
        # self.log(f"所有交易记录{final_trade_df.shape}{final_trade_df.index}{final_trade_df.columns}", 100)

        # 得到 profit_df
        profit_df = self._get_profit_df(final_trade_df=self.final_trade_df)
        profit_df.to_csv(f"逐笔交易利润{prefix}_逐笔交易利润表.csv", index=False, encoding="gb18030")
        # self.log(f"{profit_df.shape}{profit_df.index}{profit_df.columns}", 100)

        # 计算胜率
        self._cal_win_rate()

        # 计算盈亏比
        self._cal_win_fail_ratio()

        # 得到'期望df'
        expectation_df = self.get_expectation_df(profit_df=self.profit_df)
        expectation_df.to_csv(f"{prefix}_期望值表.csv", index=False, encoding="gb18030")

        #合成一个整体 excel 表格
        #self.get_complete_excel(daily_df, final_trade_df, profit_df, expectation_df)

        # 计算整体的期望值
        sum_expectation = expectation_df["期望值"].sum()
        self.strategy.GF.Log(f"[策略总期望值]: {sum_expectation:.3%} ", "#ff0000")

        # 以上是常规统计, 如果有其他个性化统计, 需要在子类中继承父类并实现其他方法
        # ================================

        pass




"""
重写update increase 方法

"""

class MyBasePositionManager(BasePositionManager):
    
    def update(self, op="increase"):
        """
            更新'每次下单金额' (更改下单仓位):
                盈利: '每次下单金额'开始翻倍增加
                亏损: '每次下单金额'保持当前仓位
                多次: '若出现连续盈利 max_increase_times，则下笔交易的仓位回归到初始仓位'
        """

        if op == "increase":
            
            self.increase()
            self.GF.Logger.log(f"[盈利] (连续次数:{self.increase_times})", 100)
        elif op == "reset":

            # 亏损仓位保持不变
            self.GF.Logger.log(f"[维持仓位]", 100)
        
        self.GF.Logger.log(f"[更新'每次下单金额'] self.strategy.quote_qty:{self.strategy.trade.pm.quote_qty}", 100)

    def increase(self):
        "增加仓位(增加每次下单金额)"
        if self.increase_times <= self.max_increase_times:
            self.strategy.trade.pm.quote_qty *= self.multiplier # 仓位根据乘数翻倍
            self.increase_times += 1
        else:
            "连续盈利max_increase_times次数回到原始仓位"
            self.reset()
