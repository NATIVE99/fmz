"""

"""
from helpers import *
import time
import json
import math


import time

class StrategyEnvelopeLine(BaseStrategy):
    """
    策略逻辑:最高最低价包络线策略
    """
    author = "Byron"

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
        "N_high",
        "N_close",
        "N_lower",
        "stop_profit_rate",
    ]  # yapf:disable

    # 状态变量
    variables = []

    def __init__(self, cta_engine):
        super().__init__(cta_engine)
        self.EMA_high = []
        self.EMA_close = []
        self.EMA_lower = []

        # 添加策略必备的'子组件'
        self.add_trade(TradeEnvelopeLine)
        self.add_analysis(BaseAnalysis)
        self.add_pm(BasePositionManager)
        self.log = self.GF.Logger.log

    def initialize(self):
        super().initialize()
        # 计算初始的价格，因为框架刚启动，价格为None
        if not self.tick.price:
            self.tick.price = self.GF.exchange.GetTicker().Last
        self.get_symbol_precision()
        self.old_order_list = []  # 获取成交订单进行去重处理的列表

        # 收益率计算，该值为初始的收益率
        self.first_balance = self.trade.get_future_quote_qty_tatal()

        # 可删除的参数
        self.print_account_info = self.print_account_info2 = 0  # 重复打印账户信息的判断参数
        self.running_time = time.time()  # 策略启动时候的时间，
        self.running_num = 0  # 策略启动后，完成一笔订单后，将该次数 + 1,一天最多开仓几次
        self.increase_position()  # 增加初始的下单次数
        if self.init_reboot:
            self.trade.end_of_close_position()

    def _get_running_num(self):
        """限制开仓的次数
        """
        is_open = True
        if self.running_num >= self.choose_running_num:
            # is_open = False
            self.log(f"一天开仓次数达到{self.running_num}次，程序停止运行", 100)
            exit()
        if self.running_time + 60 * 60 * 24 < time.time():
            self.running_num = 0
            self.running_time = time.time()
        return is_open

    def increase_position(self):
        """策略重启后，初始的加仓次数，不影响原来的仓位
        """
        while self.increase_position_num:
            self.trade.pm.update(op="increase")
            self.increase_position_num -= 1
            if self.increase_position_num < 0:
                self.increase_position_num = 0

    def show_profit(self):
        """显示收益曲线
        """
        new_balance = self.trade.get_future_quote_qty_tatal()
        diff_banlance = new_balance - self.first_balance
        GF.LogProfit(diff_banlance)

    def is_close_order_done(self):
        """
        判断最新的一笔订单是否完结了，return new_order_lst
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

    def get_EMA(self,bars):
        if bars != []:
            self.EMA_high = talib.EMA(bars.High, timeperiod=self.N_high)
            self.EMA_close = talib.EMA(bars.Close, timeperiod=self.N_close)
            self.EMA_lower = talib.EMA(bars.Low, timeperiod=self.N_lower)
            return True
        return False

    def compare_the_price(self ,bars):
        if bars[-1].Close > self.EMA_high[-1] and bars[-2].Close <= self.EMA_high[-2]:
            #收盘价超过最高价平均移动线做多
            self.log(f"收盘价: {bars[-1].Close} --  最高价EMA： {self.EMA_high[-1]} -- 上个收盘价: {bars[-2].Close} --  上个最高价EMA： {self.EMA_high[-2]}  收盘价超过最高价平均移动线做多 ", 100)
            return 1
        elif bars[-1].Close <= self.EMA_lower[-1] and bars[-2].Close > self.EMA_lower[-2]:
            #收盘价跌过最低价平均移动线做空
            self.log(f"收盘价: {bars[-1].Close} --  最高价EMA： {self.EMA_lower[-1]} -- 上个收盘价: {bars[-2].Close} --  上个最低价EMA： {self.EMA_lower[-2]}  收盘价跌过最低价平均移动线做空 ", 100)
            return -1
        else:
            #self.log("无任何情况", 100)
            return 0

    def _get_bar_signals(self):
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
        LenIsEnough = True
        klinelst = []
        bar_signals = []

        # 1. 获取必要指标(获取长度为len_kline的K线)
        if self.bars == None:  # 当前所有的bars
            return bar_signals
        else:
            this_bars = self.bars

        LenLongIsEnough = False
        if len(this_bars.Close) >=self.N_close:
            LenLongIsEnough = True
            self.get_EMA(this_bars)

        order_lst = self.is_close_order_done()  # 根据订单记录，判断一笔订单是否完结了
        self.position_new_flag = self.get_position_new_flag(order_lst)  # 返回持仓信息
        self.trade.is_order_profit_or_loss()  # 查询订单的成交状态

        open_singal={"buy":False,"sell":False}
        i = self.compare_the_price(this_bars)
        if  i == 1:open_singal["buy"] = True 
        elif i == -1:open_singal["sell"] = True 

        run_time = self._get_running_num()  # 一天开仓次数
        if run_time:
            # 2. 开平仓操作
            # K线出现排序满足给定要求就开多
            if LenLongIsEnough and open_singal["buy"]:
                if self.position_new_flag == -1:
                    # 止损
                    bar_signal = self.post_trade_signal(offset='close', direction='buy', trade_rate=1)
                    bar_signals.append(bar_signal)
                    self.log(f"止损bar_signal:{bar_signal}",100)
                elif self.buy_trading_toggle.toggle and self.position_new_flag == 0:
                    # 市价开仓做多
                    bar_signal = self.post_trade_signal(offset='open', direction='buy', trade_rate=1)
                    bar_signals.append(bar_signal)  # 将开仓单的信息加入到开仓列表里面
                    self.log(f"做多bar_signal:{bar_signal}",100)
            elif LenLongIsEnough and open_singal["sell"]:
                if self.position_new_flag == 1:
                    # 止损
                    bar_signal = self.post_trade_signal(offset='close', direction='sell', trade_rate=1)
                    bar_signals.append(bar_signal)
                    self.log(f"止损bar_signal:{bar_signal}",100)
                if self.sell_trading_toggle.toggle and self.position_new_flag ==0:
                    # 市价开仓做空
                    bar_signal = self.post_trade_signal(offset='open', direction='sell', trade_rate=1)
                    bar_signals.append(bar_signal)  # 将开仓单的信息加入到开仓列表里面
                    self.log(f"做空bar_signal:{bar_signal}",100)
        return bar_signals

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

        bar_signal = {"signal_type": signal_type, "offset": offset, "direction": direction, "price": price,
                       "base_qty": base_qty}


        return bar_signal


    def get_tick_signals(self):
        """
        获取 tick 的信号
        """
        self.tick.signals = []

    def process_tick_signals(self):
        """
        处理 tick 的信号
        """
        super().process_tick_signals()

        # 遍历'tick的开仓信号'
        for _ in range(len(self.tick.signals)):
            signal = self.tick.signals.pop(0)
            print(signal)

    def get_bar_signals(self):
        """
        获取 bar 的信号
        """
        self.bar.signals = []
        bar_signals = self._get_bar_signals()
        self.bar.signals.extend(bar_signals)

    def process_bar_signals(self):
        """
        处理 bar 的信号
        """

        super().process_bar_signals()

        # 遍历'bar的开仓信号'
        #self.log("self.bar.signals:" + str(self.bar.signals), 100)
        for _ in range(len(self.bar.signals)):
            signal = self.bar.signals.pop(0)
            signal["exchange"] = GF.exchange
            signal_type = signal.pop("signal_type")
            if signal_type == "open_order":
                self.trade.open_order(**signal)
            elif signal_type == "close_order":
                self.trade.close_order(**signal)


    


    def draw(self, bars, draw_all=True):
        # 继承父类
        super().draw(bars, draw_all=draw_all)

        # ii. 布林轨
        boll_price_dict = self.ie.get_boll_price_dict(bars=self.bars)
        # 上轨
        self.chart.fmz_chart.add(self.chart.get_series_index(
            self.chart.chart_config, "EMA-最高价"), [self.bar.time, self.EMA_high[-1]])
        # 中轨
        self.chart.fmz_chart.add(self.chart.get_series_index(
            self.chart.chart_config, "EMA-收盘价"), [self.bar.time, self.EMA_close[-1]])
        # 下轨
        self.chart.fmz_chart.add(self.chart.get_series_index(
            self.chart.chart_config, "EMA-最低价"), [self.bar.time, self.EMA_lower[-1]])
        # 画网格线
        pass




class TradeEnvelopeLine(BaseTrade):
    # 可调参数
    parameters = [
        "base_qty",
        "quote_qty",
        "trading_toggle",
        "stop_loss_type",

    ]
    # 全局变量
    variables = ["position_flag"]

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
        self.stop_loss_bar_order_lst = []
        self.stop_loss_tick_order_lst = []

        # 挂单的订单列表
        self.open_maker_order_lst = []  # 开仓挂单
        self.close_maker_order_lst = []  # 平仓挂单

        # 打印日志
        self.log = self.GF.Logger.log

    def reset_position_flag(self):
        """
            策略逻辑内的一个订单'已经完结', 重置各种'持仓标识'
        """
        self.position_flag = 0  # '持仓标识'变为空仓
        self.cancel_stop_profit_orders()
        self.cancel_stop_loss_orders()

    def is_order_profit_or_loss(self):
        '''根据已完成的一笔订单的最后一笔，查询订单是止盈还是止损，并返回订单状态
           同时会清空网格，并休眠，这时候就算有订单也不能下单，做了另一道限制
           打印成交信息，根据成交信息输出是亏损还是盈利多少百分比
        '''
        order_status = {}  # 已完结订单的止盈止损情况
        order_dict = self.strategy_trade_dict_dict
        # 进行订单去重的判断,用key来判断，先获取所有订单且长度等于2的key，再取出不在旧订单长度等于2的新key，之后将所有订单赋值给旧的
        order_list = [order for order in order_dict if len(order_dict[order]) == 2]
        new_order_list = [order for order in order_dict if order not in self.strategy.old_order_list and len(order_dict[order]) == 2]
        self.strategy.old_order_list = order_list[:]
        # 如果产生新的key,且新的订单必须完结
        # self.log(order_dict)
        if new_order_list:
            # 打印订单记录
            new_order = order_dict[order_list[-1]]
            order0 = dict(
                zip(['offset', 'direction', 'price', 'base_qty'],
                    [new_order[0]['offset'], new_order[0]['direction'], new_order[0]['price'], new_order[0]['base_qty']]))
            order1 = dict(
                zip(['offset', 'direction', 'price', 'base_qty'],
                    [new_order[1]['offset'], new_order[1]['direction'], new_order[1]['price'], new_order[1]['base_qty']]))
            self.log(f'成交明细, {order0}, {order1}', 90)

            # 进行止盈还是止损的判断
            if new_order[0]['direction'] == 'buy' and new_order[1]['direction'] == 'sell':  # 开多，平多
                # 开仓价大于平仓价，该订单止损
                order_status['loss'] = True if new_order[0]['price'] >= new_order[1]['price'] else False
                # 开仓价小于平仓价，该订单止盈
                order_status['profit'] = True if new_order[0]['price'] < new_order[1]['price'] else False

                # 计算盈亏的百分比
                m = (new_order[1]['price'] - new_order[0]['price']) / new_order[0]['price'] * 100
                self.log(f'做多{"亏损" if m <= 0 else "盈利"}{self.GF._N(m,2)}%', 90)

            elif new_order[0]['direction'] == 'sell' and new_order[1]['direction'] == 'buy':  # 开空，平空
                # 开仓价大于平仓价，该订单止损
                order_status['profit'] = True if new_order[0]['price'] > new_order[1]['price'] else False
                # 开仓价小于平仓价，该订单止盈
                order_status['loss'] = True if new_order[0]['price'] <= new_order[1]['price'] else False

                # 计算盈亏的百分比
                m = (new_order[0]['price'] - new_order[1]['price']) / new_order[0]['price'] * 100
                self.log(f'做空{"亏损" if m <= 0 else "盈利"}{self.GF._N(m,2)}%', 90)

            # 对历史成交记录的字典进行清空，保证效率
            if len(self.strategy_trade_dict_dict) >= 20:
                self.strategy_trade_dict_dict = {}
            self.end_of_close_position()
            self.strategy.show_profit()  # 显示收益曲线
            self.log('=' * 50, 100)
            self.strategy.running_num += 1

    def end_of_close_position(self):
        """一笔订单结束，判断挂单信息和持仓信息，进行撤单，并对持仓进行平仓
        """
        # 查询挂单，如果有，就进行撤单
        all_orders = self.GF.exchange.GetOrders()
        for order in all_orders:
            self.log(f"有挂单，进行撤单操作", 100)
            self.cancel_order(order_id=order['Id'], exchange=self.GF.exchange)  # 撤单
        futures_base_qty_total = self.get_futures_base_qty_total(exchange=self.GF.exchange)
        if futures_base_qty_total < 0:
            direction = 'buy'
        elif futures_base_qty_total > 0:
            direction = 'sell'
        futures_base_qty_total = abs(futures_base_qty_total)
        if futures_base_qty_total != 0:
            self.log(f'持仓不为0，进行平仓操作', 100)
            self.send_order(offset="close", direction=direction, price=-1, base_qty=futures_base_qty_total, exchange=self.GF.exchange)

    def open_order(self, offset, direction, price, base_qty, exchange=None, **kwargs):
    ########
    ###这里修改止盈止损(暂时都用固定止盈止损)
    ########
        if self.trading_toggle.toggle:
            if direction == "buy" and self.strategy.buy_trading_toggle.toggle:
                # 开多下单:
                open_price = self.strategy.tick.price
                self.GF.Logger.log(f'开仓触发价：{open_price}', 90)
                base_qty = self.get_base_qty(base_qty=self.strategy.base_qty, quote_qty=self.strategy.trade.pm.quote_qty)
                order_id = self.send_order(offset=offset, direction=direction, price=price, base_qty=base_qty, exchange=exchange)
                # 记录交易信息
                self.record_strategy_trade(order_id=order_id, offset=offset, direction=direction, price=price, base_qty=base_qty)
                # 止盈:
                stop_profit_maker_base_qty = base_qty
                stop_profit_maker_price = open_price * (1 + self.strategy.stop_profit_rate)
                self.GF.Logger.log(f'止盈挂单价：{stop_profit_maker_price}', 90)
                self.stop_profit_maker(direction="sell", price=stop_profit_maker_price, base_qty=stop_profit_maker_base_qty, exchange=GF.exchange)

            elif direction == "sell" and self.strategy.sell_trading_toggle.toggle:
                # 开空下单:
                open_price = self.strategy.tick.price
                self.GF.Logger.log(f'开仓触发价：{open_price}', 90)
                base_qty = self.get_base_qty(base_qty=self.strategy.base_qty, quote_qty=self.strategy.trade.pm.quote_qty)
                order_id = self.send_order(offset=offset, direction=direction, price=price, base_qty=base_qty, exchange=exchange)
                # 记录交易信息
                self.record_strategy_trade(order_id=order_id, offset=offset, direction=direction, price=price, base_qty=base_qty)
                # 止盈:
                stop_profit_maker_base_qty = base_qty
                stop_profit_maker_price = open_price * (1 - self.strategy.stop_profit_rate)
                self.GF.Logger.log(f'平仓挂单价：{stop_profit_maker_price}', 90)
                self.stop_profit_maker(direction="buy", price=stop_profit_maker_price, base_qty=stop_profit_maker_base_qty, exchange=GF.exchange)

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

    def check_stop_loss_bar(self, exchange=None):
        """修改父类，去掉撤销止盈挂单
            检查是否满足'收盘止损单'止损条件
                若满足条件: 则以'市价'立马止损
        """
        # 打印排错
        self.GF.Logger.log(f"未成交的收盘止损单:{self.stop_loss_bar_order_lst}", 50)

        close_price = self.strategy.bar.close_price
        futures_base_qty_total = abs(self.get_futures_base_qty_total(exchange=exchange))
        for stop_loss_bar_order_info in self.stop_loss_bar_order_lst:
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
                    self.log(f"收盘止损的实时价{self.strategy.tick.price}", 90)
                    order_id = self.send_order(offset="close", direction=direction, price=-1, base_qty=futures_base_qty_total, exchange=exchange)
                    self.record_strategy_trade(order_id=order_id,
                                               offset="close",
                                               direction=direction,
                                               price=-1,
                                               base_qty=futures_base_qty_total,
                                               stop_type="stop_loss")
                    self.reset_position_flag()
                    self.pm.update(op="increase")  # 更新'每次下单金额'
                    # 禁止开仓 (默认10次)
                    self.strategy.trading_toggle.close()
            elif direction == "buy":
                # 若收盘价高于止损价, 市价买入止损
                if close_price >= stop_loss_bar_price:
                    # 先把止盈单撤销
                    cancel_success = self.cancel_stop_profit_orders(exchange=exchange)
                    if not cancel_success:
                        return
                    # 再市价止损
                    self.log(f"收盘止损的实时价{self.strategy.tick.price}", 90)
                    order_id = self.send_order(offset="close", direction=direction, price=-1, base_qty=futures_base_qty_total, exchange=exchange)
                    self.record_strategy_trade(order_id=order_id,
                                               offset="close",
                                               direction=direction,
                                               price=-1,
                                               base_qty=futures_base_qty_total,
                                               stop_type="stop_loss")
                    self.reset_position_flag()
                    self.pm.update(op="increase")  # 更新'每次下单金额'
                    # 禁止开仓 (默认10次)
                    self.strategy.trading_toggle.close()

    def check_stop_loss_tick(self, exchange=None):
        """修改父类
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
                    self.log(f"瞬间止损的实时价{self.strategy.tick.price}", 90)
                    order_id = self.send_order(offset="close", direction=direction, price=-1, base_qty=futures_base_qty_total, exchange=exchange)
                    self.record_strategy_trade(order_id=order_id,
                                               offset="close",
                                               direction=direction,
                                               price=-1,
                                               base_qty=futures_base_qty_total,
                                               stop_type="stop_loss")
                    self.reset_position_flag()
                    self.pm.update(op="increase")  # 更新'每次下单金额'
                    # 禁止开仓 (默认10次)
                    self.strategy.trading_toggle.close()
            elif direction == "buy":
                # 若'最新价'高于止损价, 市价买入止损 (全部仓位止损)
                if latest_price >= stop_loss_tick_price:
                    # 先把止盈单撤销
                    cancel_success = self.cancel_stop_profit_orders(exchange=exchange)
                    if not cancel_success:
                        return
                    # 再市价止损
                    self.log(f"瞬间止损的实时价{self.strategy.tick.price}", 90)
                    order_id = self.send_order(offset="close", direction=direction, price=-1, base_qty=futures_base_qty_total, exchange=exchange)
                    self.record_strategy_trade(order_id=order_id,
                                               offset="close",
                                               direction=direction,
                                               price=-1,
                                               base_qty=futures_base_qty_total,
                                               stop_type="stop_loss")
                    self.reset_position_flag()
                    self.pm.update(op="increase")  # 更新'每次下单金额'
                    # 禁止开仓 (默认10次)
                    self.strategy.trading_toggle.close()

    def check_order_status(self, order_id):
        """修改父类，增加重试与打印
            获取订单的'成交状态'
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
        "修改父类，增加打印与延时，当策略开始新的一单时, 启动该方法"
        self.log(f"撤销的订单，{order_id}", 90)
        order_id = exchange.CancelOrder(order_id)
        self.GF.Sleep(2000)
        return order_id

    def get_futures_base_qty_total(self, exchange):
        "修改父类，增加打印，修改空头持仓，获取合约账户, '该币种'的仓位的总数量 (多头为正, 空头为负)"
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
                futures_base_qty_total += futures_base_qty
        return futures_base_qty_total

    def stop_profit_maker(self, direction, price, base_qty, exchange=None, **kwargs):
        "修改父类，增加打印，挂单止盈"
        order_id = self.send_order(offset="close", direction=direction, price=price, base_qty=base_qty, exchange=exchange)
        if order_id:
            stop_profit_maker_order_info = {
                "order_id": order_id,
                "offset": "close",
                "direction": direction,
                "price": price,
                "base_qty": base_qty,
                # "maker_price_index":kwargs['maker_price_index']
            }
        else:
            msg = f"[下单失败] order_id:{order_id}"
            raise Exception(msg)
        self.stop_profit_maker_order_lst.append(stop_profit_maker_order_info)
        self.log(f"止盈挂单的信息{self.stop_profit_maker_order_lst}", 90)

    def get_account_info(self, exchange):
        """修改父类，增加重试
        """
        symbol, full_symbol, base_asset, quote_asset = UTILS.get_symbol(exchange)
        # self.GF.Log(f"symbol:{symbol}")
        account_dict = self.GF._C(exchange.GetAccount)
        # self.GF.Log(f"account_dict:{account_dict}")
        exchange_name = self.GF._C(exchange.GetName)
        # self.GF.Log(f"exchange_name:{exchange_name}")
        exchange_name_prefix = exchange_name.split("_")[0]  # 交易所的前缀  （期货的话前面会带有‘Futures’）
        if exchange_name_prefix == "Futures":
            # self.GF.Log(f"进入Futures...")
            #position_dict = exchange.GetPosition()[0] if exchange.GetPosition() else {}
            #contract_type = exchange.GetContractType()
            # contractType即使是合约， 若当前没有仓位的话，还是会返回空[]
            position_dict_lst = GF._C(exchange.GetPosition) if self.GF._C(exchange.GetPosition) else []
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
        marginBalance = self.GF._N(float(marginBalance), 2)
        self.log(f"marginBalance:{marginBalance}", 100)
        return marginBalance
