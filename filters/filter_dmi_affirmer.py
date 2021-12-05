from helpers import *


# 具象实现类-过滤器模板 (空过滤器)
class FilterDMIAffirmer(BaseFilter):
    '''
    DIM肯定过滤器
    ADX活动区间在0－100内，如果ADX趋向100，表明多空某一方的力量趋于零。如果ADX值大，表明多空双方实力相差悬殊；如ADX值小，表明多空双方实力接近。如果ADX趋向零，表明多空双方的实力近似相等。
    一般讲,ADX值在20至60间，表明多空双方实力大体相等，轮换主体位置的可能性大。投资者此时易把握自己的位置，看准时机，空头转多头，或相反。
    type=1
    ADX > X, 开单。反之不开单 【X是UI控件参数，参数命名为ADX过滤阈值。】
    type=0
    ADX < X, 开单。反之不开单 【X是UI控件参数，参数命名为ADX过滤阈值。】
    可调参数:
    dmi_type：肯定器类型 默认1
    adx_valve:过滤阀值 默认10
    adx_period：adx周期 默认 14
    '''
    author = "Byron"
    filter_type = "Affirmer"

    # 可调参数
    parameters = ["dmi_type","adx_valve","adx_period"
    ]
    # 状态变量
    variables = ["flag"
    ]

    def __init__(self, strategy_inst):
        # 继承父类
        super().__init__(strategy_inst=strategy_inst)



    def get_adx(self, bars):
        return talib.ADX(self.bars.High, self.bars.Low, self.bars.Close, self.adx_period)[-1]
    def get_dmi_flag(self,bars):
        if self.dmi_type == 1:
            if self.get_adx(bars) > self.adx_valve:
                return 1
            else:
                return 0
        elif self.dmi_type == 0:
            if self.get_adx(bars) < self.adx_valve:
                return 1
            else:
                return 0

    def get_filter_flag(self, bars):
        self.flag = self.get_dmi_flag(bars)
    def draw(self, bars, draw_all=True):
        self.chart.fmz_chart.add(
            self.chart.get_series_index(self.chart.chart_config, "DC-肯定器"),
            [self.bar.time, self.flag]
        )




