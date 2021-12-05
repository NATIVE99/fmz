from helpers import *


class FilterBbw(BaseFilter):
    """
        说明： 过滤 bbw 
            1. bbw 值的相对大小可以反映横盘，所以通过 求的 bbw 的值来
    """
    author = "bigluo"
    filter_type = "Negator"
    parameters = ["bbw_value"]
    # 状态变量
    variables = []

    def __init__(self, strategy_inst):
        super().__init__(strategy_inst=strategy_inst)
        self.flag = 1

    def get_filter_flag(self, bars):
        """
        输入: bars
        功能: 计算过滤器指标
        输出: self.flag (1:否定器开启否定, 0：否定器未开启否定)
        """
        self.flag = self.get_bbw_signal(candles=bars)

    def draw(self, bars, draw_all=True):
        # flag = 0 if self.flag else 1.2
        self.chart.fmz_chart.add(
            self.chart.get_series_index(self.chart.chart_config, "BBW值否决"),
            [self.bar.time, self.flag * 1.2])
        self.chart.fmz_chart.add(
            self.chart.get_series_index(self.chart.chart_config, "BBW视图"),
            [self.bar.time, self.get_bbw(bars)])

    # boll
    def get_bbw(self, candles):
        if candles and len(candles) > 20:
            boll = GF.TA.BOLL(candles, 20, 2)
            upline = boll[0][-1]
            middleline = boll[1][-1]
            downline = boll[2][-1]
            bbw = (upline - downline) / middleline
            return bbw

    def get_bbw_signal(self, candles):
        bbw_value = self.get_bbw(candles=candles)
        if bbw_value < GT.bbw_value:
            bbw_flag = 1
        else:
            bbw_flag = 0
        return bbw_flag

