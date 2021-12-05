from helpers import *


class FilterDcAffirmer(BaseFilter):
    """DC一票肯定器说明
        1. 连续 N 根 合格的 bar 触发条件 （ 该条件无法被拟合直线否决， 但是可以被否决器否决 ）
        2. 合格bar定义 ：当前 DC 上轨的值小于等于 前一根 DC 上轨的值 且 bar 下轨的值大于等于前一根下轨的值
        
        说明： 业务有 肯定器 | 否决器。 肯定器和否决器相交那就被否决。肯定器只有肯定的作用。

        DC 指标
        1. 过去 N 日最高价 - 上轨
        2. 过去 N 日最底价 - 下轨
        3. 过去 N 日最高和最低价的均值 - 中轨
    """
    author = "bigluo"

    filter_type = "Affirmer"

    # 可调参数
    parameters = ["conti_num", "contin_num_persent"]

    # 类内变量
    variables = []

    
    def __init__(self, strategy_inst):
        super().__init__(strategy_inst)


    def get_filter_flag(self, bars):
        self.flag = self.get_affirmer_flag(bars, conti_num=self.conti_num, contin_num_persent=self.contin_num_persent)


    # 判断一根 dc 是否满足要求
    def is_require_dc_bar(self, bars):
        dc_dict = self.ie.get_dc(bars)
        pre_dc_dict = self.ie.get_dc(bars[:-1])
        if dc_dict["upline"] <= pre_dc_dict["upline"] and dc_dict["downline"] >= pre_dc_dict["downline"]:
            return True
        else:
            return False


    def is_require_dc_upine(self, bars):
        dc_dict = self.ie.get_dc(bars)
        pre_dc_dict = self.ie.get_dc(bars[:-1])
        
        if dc_dict["upline"] == pre_dc_dict["upline"]:
            return True
        else:
            return False


    def is_require_dc_downline(self, bars):
        dc_dict = self.ie.get_dc(bars)
        pre_dc_dict = self.ie.get_dc(bars[:-1])

        if dc_dict["downline"] == pre_dc_dict["downline"]:
            return True
        else:
            return False


    # 判断一组连续的 dc 值是否相等
    def is_require_dc_bars(self, bars, conti_num) -> bool:        
        bars_bool = True

        for i in list(range(conti_num)):
            index = (i+1) - conti_num
            ls_bars = None
            if index == 0:
                ls_bars = bars
            else:
                ls_bars = bars[:index]
            if not self.is_require_dc_bar(ls_bars):
                bars_bool = False

        return bars_bool


    def is_require_dc_lines(self, bars, conti_num, contin_num_persent) -> bool:
        count = 0

        for i in list(range(conti_num)):
            index = (i+1) - conti_num
            ls_bars = None
            if index == 0:
                ls_bars = bars
            else:
                ls_bars = bars[:index]
            if self.is_require_dc_upine(ls_bars):
                count += 1
            if self.is_require_dc_downline(ls_bars):
                count += 1
            
        if (count / (conti_num * 2)) >= contin_num_persent:
            self.GF.Logger.log(f"{count/(conti_num * 2)}", 20)
            return True
        else:
            return False


    # 获取肯定器的        
    def get_affirmer_flag(self, bars, conti_num, contin_num_persent):
        self.GF.Logger.log(f"{self.is_require_dc_bars(bars, conti_num)} "
                           f"{self.is_require_dc_lines(bars, conti_num, contin_num_persent)}", 20)
        if self.is_require_dc_bars(bars, conti_num) and self.is_require_dc_lines(bars, conti_num, contin_num_persent):
            return 1
        else:
            return 0

    def draw(self, bars, draw_all):
         # 1. 画最终的flag
        self.chart.fmz_chart.add(
            self.chart.get_series_index(self.chart.chart_config, "DC-肯定器"),
            [self.bar.time, self.flag]
        )

    

            
            
            
        

        
