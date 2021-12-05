from helpers import *


class FilterBreakBoll(BaseFilter):
    author = "bigluo"
    filter_type = "Negator"
    parameters = ["alpha_bbw", "ban_time"]
    # 状态变量
    variables = ["c_rest_time", "flag"]
    # 全局变量
    #c_rest_time = 0
    flag = None

    def __init__(self, strategy_inst):
        super().__init__(strategy_inst=strategy_inst)
        self.flag = 1  # 默认为 1， 表示是横盘, 没有进行横盘否决
        self.timer_toggle = "off"  # 设置 timer 默认是关闭的 计时器开关
        self.c_rest_time = 0 #计时器时间
    
    def get_filter_flag(self, bars):
        """
        1. 否定器开启否定 1， 0 表示未开启否定

        """
        # flag = 0 if self.flag else 0
        
        # self.flag = flag

    def get_bbw(self, candles):
        if candles and len(candles) > 20:
            boll = self.GF.TA.BOLL(candles, 20, 2)
            upline = boll[0][-1]
            middleline = boll[1][-1]
            downline = boll[2][-1]
            bbw = (upline - downline) / middleline
            return bbw

    def get_bbw_width(self, candles):
        if candles and len(candles) > 20:
            boll = self.GF.TA.BOLL(candles, 20, 2)
            upline = boll[0][-1]
            middleline = boll[1][-1]
            downline = boll[2][-1]
            bbw_width = upline - downline
            return bbw_width

    def get_boll_lines(self, bars) -> list:
        if bars and len(bars) > 20:
            boll = self.GF.TA.BOLL(bars, 20, 2)
            upline = boll[0][-1]
            middleline = boll[1][-1]
            downline = boll[2][-1]
            boll_lines = {
                "upline": upline,
                "midline": middleline,
                "downline": downline
            }
            return boll_lines

    # 收盘价是否突破
    def is_close_break_boll(self, close, bbw_width, alpha_bbw, boll_lines):
        if boll_lines:
            if close > boll_lines[
                    "upline"] + alpha_bbw * bbw_width or close < boll_lines[
                        "downline"] - alpha_bbw * bbw_width:
                n_flag = 1
            else:
                n_flag = 0
            return n_flag
        else:
            raise Exception("is_clobreak_boll failed ......")

    def on_bars(self, bars):
        # 初始化父类这个方法
        super().on_bars(bars=bars)

        bbw_width = self.get_bbw_width(candles=bars)
        boll_lines = self.get_boll_lines(bars=bars)

        # Task: 写一个装饰器来用于控制倒计时！

        # 1. 检查是否存在活跃倒计时器
        if self.c_rest_time == 0:
            self.timer_toggle = "off"
            self.flag = 0
            self.GF.Logger.log(f"没有活跃度倒计时器, c_rest_timer:{self.c_rest_time}",
                               40)

        # 2. 没有活跃计时器，检查是否具备开启条件
        # if self.timer_toggle == "off":
        self.flag = self.is_close_break_boll(
            close=self.bar.close_price,
            bbw_width=bbw_width,
            alpha_bbw=self.alpha_bbw,
            boll_lines=boll_lines)
        self.GF.Logger.log(f"收盘价突破布林轨, flag:{self.flag}", 40)

        if self.flag:  # 倒计时器开启！
            self.c_rest_time = self.ban_time
            self.timer_toggle = "on"
            self.GF.Logger.log(
                f"开启计时器, c_rest_time:{self.c_rest_time} timer_toggle:{self.timer_toggle}",
                40)

        # 3. 倒计时
        if self.timer_toggle == "on":
            self.c_rest_time -= 1
            self.flag = 1
            self.GF.Logger.log(
                f"倒计时中......, c_rest_time:{self.c_rest_time} timer_toggle:{self.timer_toggle}",
                40)

    def draw(self, bars, draw_all=True):
        # self.GF.Logger.log(
        #     f"this is a testing of draw {self.flag},{self.c_rest_time}")

        self.chart.fmz_chart.add(
            self.chart.get_series_index(self.chart.chart_config,
                                        "收盘价突破布林倒计时-辅图"),
            [self.bar.time, self.c_rest_time])
        self.chart.fmz_chart.add(
            self.chart.get_series_index(self.chart.chart_config,
                                        "收盘价突破布林倒计时-主图"),
            [self.bar.time, self.flag])
