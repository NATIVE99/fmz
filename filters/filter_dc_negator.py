from helpers import *


class FilterDcNegator(BaseFilter):
    """
    过滤器说明
    1. 上轨:当前K线的DC上轨值比前一根DC通道上轨值大时，那么接下来10分钟【UI控件参数】被否决为非横盘。
    2. 下轨:当前K线的DC下轨值比前一根DC通道下轨值小时，那么接下来10分钟被否决为非横盘。
    3. 以上两个条件是或关系，任意一个触发，就会被否决会非横盘
    4. 算法对每一根K线进行无条件 不择时的判断

    """
    author = "bigluo"

    filter_type = "Negator"

    parameters = ["dc_ban_time"]

    variables = []

    def __init__(self, strategy_inst):
        super().__init__(strategy_inst)
        self.flag = 0  # 默认为 0 表示没有开启否决
        self.timer_toggle = "off"  # 设置 timer 默认是关闭的
        self.c_rest_time = 0


    def get_filter_flag(self, bars):
        """
        输入: bars
        功能: 计算过滤器指标
        输出: self.flag (1:开启否决, 0:不否决)
        """
        self.GF.Logger.log(f"the toggle is fffffff {self.flag}", 50)
        self.get_negator_flag(bars, self.dc_ban_time)
        # self.GF.Logger.log(f"the toggle is fffffff {self.flag}", 50)
        

    def is_dc_negator_bar(self, bars):
        dc_dict = self.ie.get_dc(bars)
        pre_dc_dict = self.ie.get_dc(bars[:-1])
        # self.GF.Logger.log(f"the dc value ++++++ {dc_dict} {pre_dc_dict}", 50)
        
        if dc_dict["upline"] > pre_dc_dict["upline"] or dc_dict["downline"] < pre_dc_dict["downline"]:
            return 1
        else:
            return 0


    def get_negator_flag(self, bars, dc_ban_time):
            # 1. 检查是否存在活跃倒计时器
        if self.c_rest_time == 0:
            self.timer_toggle = "off"
            self.flag = 0
            self.GF.Logger.log(f"没有活跃度倒计时器, c_rest_timer:{self.c_rest_time}",
                               40)

        # 2. 没有活跃计时器，检查是否具备开启条件
        # if self.timer_toggle == "off":
        self.flag = self.is_dc_negator_bar(bars=bars)

        if self.flag:  # 倒计时器开启！
            self.c_rest_time = self.dc_ban_time
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


    def draw(self, bars, draw_all):
        # 1. 画最终的flag
        self.chart.fmz_chart.add(
            self.chart.get_series_index(self.chart.chart_config, "DC-否定器"),
            [self.bar.time, self.flag]
        )

        # self.chart.fmz_chart.add(
        #     self.chart.get_series_index(self.chart.chart_config,
        #                                 "收盘价突破布林倒计时-辅图"),
        #     [self.bar.time, self.c_rest_time])