
'''backtest
user: bigluo
version: v1.0.6 [增加子csv合并]
start: 2020-05-01 00:00:00
end: 2020-05-03 00:00:00
args_name: 布林
ID:303281
period: 1m
basePeriod: 1m
exchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]
'''

from helpers import *

# 策略
from strategies.strategy_boll import StrategyBoll
#from strategies.mahao.strategy_sar import StrategySar
from strategies.strategy_template import StrategyTemplate
from strategies.strategy_avg_candle import StrategyAvgCandle
from strategies.strategy_grid_bak import StrategyGrid
# from strategies.mahao.strategy_grid import StrategyGrid
from strategies.mahao.strategy_grid_V2 import StrategyGridV2  # 原地生格策略
from strategies.mahao.strategy_break_grid import StrategyBreakGrid  # 格子突破
from strategies.mahao.strategy_break_boll import StrategyBreakBoll  # 布林突破
from strategies.mahao.strategy_follow_deler import StrategyFollowDeler  # 跟庄
from strategies.mahao.strategy_golden_cross import StrategyGoldenCross  # 金叉策略
from strategies.mahao.strategy_wave import StrategyWave  # 广义波浪策略
from strategies.mahao.strategy_in_place_reverse import StrategyInPlaceReverse  # 原地反向策略
from strategies.wangbo.strategy_ContinueRising import StrategyContinueRising

# 余犇策略
from strategies.yuben.strategy_klineTangram import StrategyKlineTangram  #k线七巧板策略
from strategies.yuben.strategy_golden_crosswithfilters import StrategyGoldenCrosswithfilters  #庞氏金叉策略带macd、rsi过滤器
from strategies.yuben.strategy_ema_callback_trend import StrategyEmaCallbackTrend  #EMA回调策略版本三

#王渤策略
# from strategies.wangbo.strategy_RangeBreak import StrategyRangeBreak
from strategies.wangbo.strategy_ContinueRising import StrategyContinueRising

# 马文哲策略
from strategies.mwz.strategy_fei_ali import StrategyFeiALi  # 菲阿里策略
from strategies.mwz.strategy_continuously_variable_speed_macd import StrategyContinuouslyVariableSpeedMacd  # MACD无级变速策略

# 过滤器
from filters.filter_template import FilterTemplate
from filters.filter_sideway_fitted import FilterSidewayFitted
from filters.filter_sideway_sar import FilterSidewaySar
from filters.filter_bbw import FilterBbw
# from filters.filter_break_boll import FilterBreakBoll  #（回测太慢，马文哲修改成了另一个版本）
from filters.filter_ema import FilterEma
from filters.filter_double_ema import FilterDoubleEma
# from filters.filter_ema_cross import FilterEmaCross
from filters.filter_dc_affirmer import FilterDcAffirmer
from filters.filter_dc_negator import FilterDcNegator
from filters.filter_random_negator import FilterRandomNgtor
# from filters.filter_candle_type import FilterCandleType
from filters.mahao.filter_con_loss_negator import FilterConLossNegator  # 连续亏损否定器
from filters.mwz.filter_macd_turbence import FilterMacdTurbence  # macd过滤震荡
from filters.mwz.filter_break_boll_v2 import FilterBreakBoll  # 布林突破过滤器
from filters.wangbo.filter_ContinueRising_affirmer import FilterContinueAffirmer # 阳线或阴线数量肯定器

engine_config = {
    "doc": __doc__,  # yapf:disable
    # 1. Log级别:
    "log_level": 60,  # yapf:disable

    # 2. 画图的配置文件:
    "chart_cls": BaseChart,  # yapf:disable,一般只用Base类
    "draw_all": False,  # yapf:disable,是否需要画出全部过程指标

    # 3. 策略类:
    # "strategy_cls" : BaseStrategy, # 策略模板 (空策略) (同下)
    # "strategy_cls" : StrategyTemplate, # 策略模板 (空策略)
    # "strategy_cls" : StrategyBoll, # 布林策略
    #"strategy_cls" : StrategySar, # sar策略
    # "strategy_cls" : StrategyAvgCandle, # 平均k线策略
    # "strategy_cls" : StrategyGrid, # 原地生格策略
    # "strategy_cls": StrategyGridV2,  # 原地生格策略V2
    # "strategy_cls" : StrategyGoldenCross, # 金叉策略
    # "strategy_cls": StrategyBreakGrid,  # 格子必破策略
    # "strategy_cls": StrategyFollowDeler,  # 跟庄策略
    # "strategy_cls": StrategyBreakBoll,  # 布林突破策略
    # "strategy_cls": StrategyGoldenCross,  # 金叉策略
    "strategy_cls": StrategyWave,  # 波浪策略
    # "strategy_cls": StrategyInPlaceReverse,  # 原地反转策略

    # 余犇策略
    # "strategy_cls": StrategyKlineTangram,  # K线七巧板策略
    # "strategy_cls": StrategyGoldenCrosswithfilters,  # 庞氏金叉macd rsi策略
    # "strategy_cls": StrategyEmaCallbackTrend,  # EMA回调策略版本三

    # 王渤策略
    # "strategy_cls": StrategyRangeBreak,  # 突破策略
    # "strategy_cls": StrategyContinueRising,  # 突破策略

    # 马文哲策略
    # "strategy_cls": StrategyFeiALi,  # 突破策略
    # "strategy_cls": StrategyContinuouslyVariableSpeedMacd,  # MACD无级变速策略

    # 4. 叠加的过滤器类:
    "filter_cls_lst": [
        # BaseFilter,
        # FilterSidewayFitted, # 拟合曲线过滤器
        # FilterBbw, # bbw过滤器
        # FilterSidewaySar, # 最近段sar过滤器
        # FilterBreakBoll, # 突破布林轨过滤器
        # FilterEma, # ema过滤器
        # FilterDcAffirmer, # DC肯定器
        # FilterDcNegator, # DC否定器
        FilterDoubleEma, # 双ema方向过滤器
        # FilterRandomNgtor, # 指定概率随机否定器
        # FilterCandleType, # 单k线阴阳方向过滤器
        # FilterEmaCross, # ema交叉过滤器
        # FilterConLossNegator,  # 连续亏损否定器
        # FilterMacdTurbence,  # MACD振幅过滤器，肯定器
        # FilterContinueAffirmer,# 阳线和阴线数量肯定器
    ],

    # 5. 可调参数-配置文件:
    "parameters_settings": {
        # 一. [过滤器相关]
        # =========================
        # 1. [filter_sideway_fitted]  拟合直线肯定器
        "hj_unit_timexs": 0.7,
        "candle_length_type_a": 8,
        "boll_upline_K_rate_max_interval_value_length_type_a": 0.00015,
        "boll_downline_K_rate_min_interval_value_length_type_a": -0.00015,
        "candle_length_type_b": 20,
        "boll_upline_K_rate_max_interval_value_length_type_b": 0.00030,
        "boll_downline_K_rate_min_interval_value_length_type_b": -0.00030,
        "candle_length_type_c": 40,
        "boll_upline_K_rate_max_interval_value_length_type_c": 1111,
        "boll_downline_K_rate_min_interval_value_length_type_c": -1111,
        "is_filter_k_abs": True,
        "k_abs_upline": 0.00030,
        "k_abs_downline": 0.00030,
        # "is_boll_middle_testing" : True,
        # "boll_middle_candle_length" : 3,
        # "boll_middle_k_rate_abs__value" : 0.00015,
        "bbw_value": 0.0043,

        # 2. [filter_break_boll] 突破布林轨导致的否决
        "ban_time": 5,  # 不开仓时间
        "alpha_bbw": 1 / 10,

        # 3. [filter_sideway_sar]
        "time_period": 20,  # 截取过去bar的数量
        "min_dot_num": 7,  # sar最少连续数
        "not_hp_period": 20,  # '剩余非横盘数量'出现后, 持续多少个bar的时间内都是'非横盘状态'
        "alpha": 1.35,  # 最短布林带系数

        # 4. [filter_ema]
        "ema_time_period": 30,  # ema的周期选择
        "max_break_num": 9,  # '最大间断次数'
        "estimate_trend_times": 10,  # '预估趋势次数' (方向过滤)

        # 5. [filter_dc] dc 肯定器
        "conti_num": 5,  # 连续合格 dc
        "contin_num_persent": 0.7,  # 4 根里面的百分比

        # 6. [filter_dc_negator] dc 否定器
        "dc_ban_time": 10,

        # 7. [filter_random_negator]  指定概率随机否定器
        "rd_pblity": 0.5,

        # 8. [filter_double_ema]  双ema方向过滤器
        "fast_period": 10,
        "slow_period": 100,

        # 9. [filter_ema_cross]  ema交叉临界肯定器
        "filter_ema_cross_fast_period": 100,
        "filter_ema_cross_slow_period": 350,
        "ema_cross_holding_time": 30,  # 肯定器维持时间

        # 10. [filter_loss_sleep]  亏损休眠否定器
        "loss_sleep_holding_time": 10,  # 否定器维持时间

        # 11. [filter_con_loss_negator]  连续亏损否定器
        # 否定器要在订单完结后运行一次，在策略里添加through_filter，并且只运行订单相关的过滤器，否定时间要+1
        "con_loss_sleep_holding_time": 10,  # 否定器维持时间
        "con_loss_num": 1,  # 连续亏损几次，默认2次

        # 12. [filter_macd_urbence]  MACD震荡过滤
        "macd_fastperiod": 30,  # macd 参数
        "macd_slowperiod": 60,  # macd 参数
        "macd_signalperiod": 14,  # macd参数
        "total_macd_hist_num": 10,  # 所有的macd柱子数量，文档中表示为m
        "judge_macd_hist_num": 5,  # 判断所有的macd柱子里，有多少根柱子满足数量，文档中为n
        "without_turbence_kline_num": 0,  # 满足条件后，接下来多少根K线不进行过滤判断
        "final_result_type": 0,  # final的最终值按照哪种方法计算 0 就是默认值 macd_final，1 就是根据公式计算
        "macd_final": 5,  # macd的final值，
        "total_kline_for_final": 20,  # 计算final时，方式2里的20根K线
        "total_kline_for_final_divisor": 10,  # 计算final时，方式2里的20根K线的除数10

        # 13.[filter_ContinueRising_affirmer]  阳线和阴线数量肯定器
        "k_yin_num": 8,  # k_num中多少根K线为阴线
        "k_yang_num": 8,  # k_num中多少根K线为阳线
        "k_num": 10,  # 连续几根k线

        # 二. [策略相关]
        # =========================

        # 调试的时候的参数
        "increase_position_num": 0,  # 软件重启后初始的加仓次数
        "choose_running_num": 100,  # 一天开仓次数
        "init_reboot": 1,  # 重启后，是否撤单并平仓0代表无生效，1代表生效

        # 1. [StrategySar] sar策略
        # "direction_of_operation" : "negative",
        # "direction_of_operation": "positive",
        # "strategy_sar_stop_loss_bar_ratio": 1,  # 收盘止损比例 (1为100%)
        # "strategy_sar_stop_loss_tick_ratio": 0.01,  # 瞬间止损比例 (1为100%)

        # 2. [StrategyBoll] 布林策略
        # "stop_profit_times" : 2, # (1:中轨止盈全部, 2: 两次止盈)

        # 3. [StrategyGrid] 原地生格策略
        # "grid_ratio": 0.01,  # 一个格子的跨度比例
        # "grid_key": 1,  # 选择哪一个格子生成器0：原地生格 ， 1：变化的格子上下10格，每完成一笔订单更新一次，2：布林格子
        # "center_price": 3000,  # 0: 不手动设置中央价格，grid_key=0生效
        # "grid_ratio_multiple": 10,  # grid_key=1生效，格子的间距倍数,上轨/下轨-1 =  初始间距+初始间距%*倍数*格子索引
        # "turn_on_tick_filter": True,  # tick的过滤器，限制一根K线必须上穿上轨才能做多，下穿下轨做空，True为打开，False为关闭

        # 4. [StrategyCandle] 单k阴阳策略
        # "strategy_candle_stop_loss_bar_ratio": 1,  # 收盘止损比例 (1为100%)
        # "strategy_candle_stop_loss_tick_ratio": 0.01,  # 瞬间止损比例 (1为100%)
        # "strategy_candle_stop_profit_tick_ratio": 0.01,  # 瞬间止盈比例 (1为100%)

        # 5. [StrategyGoldenCross] 金叉策略
        # "gnl_kline_num": 10,  # 多少根K线的轨内率默认10
        # "cross_kline_num": 7,  # 上穿伏笔K线数
        # "filter_ema_period1": 100,  # EMA周期，方向过滤器
        # "filter_ema_period2": 350,  # EMA周期，方向过滤器
        # "cross_ema_period1": 7,  # 进行金叉判断的ema周期
        # "cross_ema_period2": 30,  # 进行金叉判断的ema周期
        # "max_z_gnl": 0.8,  # 开仓最大允许的轨内率
        # "wink_stop_point": 0.02,  # 瞬间止损点
        # "stop_profit_rate": 0.02,  # ema满足后的止盈比例
        # "stop_loss_rate": 0.005,  # ema满足后的止损比例
        # "stop_profit_kline_num": 10,  # 开仓后多少根K线之后才能平仓
        # "rsi_time_period": 14,  #rsi周期，计算rsi的参数，默认值不需要管
        # "macd_numkline": 5,  #macd过滤器需要的连续K线数
        # "low_rsi": 36,  #rsi下阈值，小于该值只能做多：38
        # "high_rsi": 60,  #rsi上阈值，大于该值只能做空，在中间的值无法开仓：62

        # 6. [StrategyBreakGrid] 格子必破策略
        # "grid_ratio": 0.005,  # 网格间距
        # "max_stop_loss_num": 5,  # 单格最大允许止损次数
        # "grid_loss_rest_time": 1,  # 格子止损休眠时间30分钟
        # "grid_profit_rest_time": 1,  # 格子止盈休眠时间30分钟
        # "sar_grid_catena": 13,  # SAR生格连续数
        # "atr_grid_catena": 13,  # ATR生格连续数
        # "horizon_movement_hour_a": 14,  # 超大横盘时间小时数A
        # "horizon_movement_hour_b": 14,  # 超大横盘时间小时数B
        # "horizon_movement_different_price": 0.04,  # 最高价和最低价价差小于4%
        # "horizon_movement_ema_cross_num": 4,  # 大于等于4次横盘判定的EMA最小交叉次数
        # "cross_ema_period1": 100,  # 默认100的EMA周期，条件3和条件4的ema周期
        # "cross_ema_period2": 300,  # 默认300的EMA周期，条件3和条件4的ema周期
        # "stop_profit_ratio": 1,  # 止盈系数默认1
        # "stop_loss_ratio": 1 / 2,  # 止损系数 默认1/2
        # "wink_stop_point": 0.02,  # 瞬间止损点默认2%
        # "key": 0,  # 选择哪种网格，0：原地  1：SAR生格  2：ATR生格  3：反转边界生格  4：超级大横盘生格
        # "choose_open_type": 1,  # 0代表瞬间价，1代表收盘价
        # "atr_key": 1,  # 0代表atr连续下跌，1代表atr连续上涨

        # 7. [StrategyFollowDeler] 跟庄策略
        # "gnl_k_line_num": 20,  # 多少根K线的轨内率
        # "min_s_gnl": 0.8,  # 横盘铺垫收盘轨内率最小值0.8
        # "abbw_samped_period": 30,  # ABBW的抽样周期30
        # "abbw_eliminate": 5,  # abbw剔除最大值最小值周期默认5
        # "a_sideway_bbw_samped_period": 40,  # a_sideway_bbw周期，默认40
        # "a_sideway_bbw_eliminate": 7,  # a_sideway_bbw剔除最大值最小值周期默认7
        # "break_leverage": 2.5,  # 突破倍数=2.5
        # "wink_stop_point": 0.02,  # 瞬间止损点默认2%

        # 8. [StrategyBreakBoll] 小级别布林突破CTA
        # "abbw_samped_period": 30,  # abbw的采样周期默认30
        # "abbw_eliminate": 5,  # abbw去掉最高价最低价的值默认5
        # "profit_ratio": 1,  # 止盈系数 1
        # "dmmg_limit": 0.3,  # 波动幅度限制，默认0.3
        # "break_distance": 1,  # 突破距离 1/6
        # "wink_stop_point": 0.02,  # 瞬间止损价2%
        # "rest_time_num": 20,  # 止盈休眠时间
        # "choose_stop_loss_bar_button":1 , # 选择是以哪种方式止损，2代表实时的布林中轨，其他代表开仓的布林中轨

        # 9. [StrategyWave] 广义波浪策略
        "all_kline_num_for_wr_indicator": 10,  # 威廉分型指标的K线总数,默认5
        "side_kline_num_for_wr_indicator": 2,  # 威廉分型指标的单侧最小K线数，默认2
        "length_of_needle": 0.2,  # 针的长度系数，默认0.2
        "profit_ratio": 2,  # 止盈系数 默认2
        "loss_ratio": 1,  # 止损系数 默认1
        "wr_down_price_index": 2,  # 第N个中期低点的价格的索引，用于平多止损，从倒数的低点开始记为1
        "wr_up_price_index": 2,  # 第N个中期高点的价格的索引，用于平多止损，从倒数的高点开始记为1
        "wink_stop_point": 2/100,  # 瞬间止损价2%
        "stop_profit_rate":2/100,  # 止盈幅度限制 2%
        "stop_loss_rate":2/100,   # 止损幅度限制2%
        "stop_profit_kline_num":100, # 止盈K线数量

        # 10. [StrategyInPlaceReverse] 原地反向策略
        # "stop_profit_rate": 4/100,  # 止盈系数
        # "stop_loss_rate": 2/100,  # 止损系数
        # "loss_rest_time": 360,  # 止损休眠分钟（不是K线数）
        # "profit_rest_time": 360,  # 止盈休眠分钟（不是K线数）

        # 11. [StrategyKlineTangram] K线七巧板策略
        # "long_kline_combination":"1011101110-101-100-1-111",  # 做多的K线排序方式 1代表阳，-1代表阴，0代表2者都行
        # "short_kline_combination":"1011101110-101-100-1-111", # # 做多的K线排序方式 1代表阳，-1代表阴，0代表2者都行
        # "stop_profit_rate": 4/100,  # 止盈系数
        # "stop_loss_rate": 2/100,  # 止损系数
        # "stop_tick_rate": 4/100, #瞬间止损系数

        # 12. [StrategEmaCallbackTrend] EMA回调趋势策略
        # "trend_ema1": 5,  # 趋势的ema1
        # "trend_ema2": 10,  # 趋势的ema2
        # "trend_ema3": 20,  # 趋势的ema3
        # "ema1_gradient": 10,  # 趋势的ema1的斜率
        # "ema2_gradient": 10,  # 趋势的ema2的斜率
        # "ema3_gradient": 10,  # 趋势的ema3的斜率
        # "ema1_bias": 0.001,  # 趋势的ema1的乖离率
        # "ema2_bias": 0.001,  # 趋势的ema2的乖离率
        # "ema3_bias": 0.001,  # 趋势的ema3的乖离率
        # #"turbulence_ema1":55,  # 震荡的ema1，默认参数55，收盘价在2根均线之间
        # #"turbulence_ema2":120,  # 震荡的ema2，默认参数120，收盘价在2根均线之间
        # "turbulence_ema1_period": 55,  # 震荡的ema1，默认参数55，收盘价在2根均线之间
        # "turbulence_ema2_period": 120,  # 震荡的ema2，默认参数120，收盘价在2根均线之间
        # "open_ema_period": 82,  # 开仓的ema，默认参数82，
        # "close_ema_period": 120,  # 平仓的ema，默认参数120，
        # "DMMG_rate": 3 / 100,  # K线的波动幅度，是abs(开盘-收盘)/收盘  3
        # "dropping_kline_num": 2,  # 满足条件的小阴，小阳线数量   8
        # "turbulence_kline_num": 2,  # 连续震荡的K线数量         5
        # "needle_length_rate": 1 / 100,  # 上影线或下引线里最小的长度比例
        # "version_flag": 1,  #止损模式，1为ema   2为boll

        # 13.[strateg_RangeBreak]突破策略
        # "upper_trial_N1": 0.65,  # 上轨可调参数N1 一般N1和N2在0.5-0.8区间浮动
        # "down_trial_N2": 0.55,  # 下轨可调参数N2
        # "choose_stop_loss_bar_button": 1,  # 选择止损模式 ０.代表固定止赢止损 ,１.不设置止损，原地反向平仓
        # "strategy_RangeBreak_stop_loss_bar_ratio": 1 / 100,  # 收盘止损系数 (1为100%)　固定值应止损
        # "strategy_RangeBreak_loss_tick_ratio": 2 / 100,  # 瞬间止损系数 (1为100%)　可以设置固定值赢止损　也可不设置根据情况而定 目前设置为固定止赢止损

        # 14.[StrategyContinuouslyVariableSpeedMacd] MACD无级变速
        # "short_macd_fastperiod":12,  # macd 参数
        # "short_macd_slowperiod":26,  # macd 参数
        # "short_macd_signalperiod":9,  # macd参数
        # "buy_hist_length": 4,  # 做多连续柱子阈值
        # "sell_hist_length": 4,  # 做空连续柱子阈值
        # "buy_profit_rate": 6 / 6,  # 多单止盈系数
        # "sell_profit_rate": 6 / 6,  # 空单止盈系数
        # "buy_loss_rate": 6 / 6,  # 多单止损系数
        # "sell_loss_rate": 6 / 6,  # 空单止损系数
        # "buy_loss_point_rate": 0.01,  # 多单固定止损系数
        # "sell_loss_point_rate": 0.01,  # 空单固定止损系数


        # 15. [StrategyContinueRising] 稀有型连涨策略
        # "n_yin_num": 2,  # 回调k线根数默认值为2才开单
        # "model_of_open": 1,  # 开仓模式 1代表立马开单 2代表 回调开单(出现连续N根阴线收，市价进场做多)
        # "model_of_stop": 2,  # 平仓模式，1代表模式1(3根sar反向) 2 代表模式二 三根sar反向+跌破ema20同时满足才止赢
        # "grid_ratio": 0.005, # 网格间距

        # 三. [仓位管理相关]
        # =========================
        "multiplier": 1,  # 加仓倍数
        "max_increase_times": 20,  # 最大加仓次数
        "base_qty": 1,  # 下单数量 (若quote_qty为0时, 才会使用base_qty下单)
        "quote_qty": 1000,  # 下单金额 (以'quote_qty'优先) (初始下单金额)

        # 四. [交易相关]
        # =========================
        "taker_fee_rate": 0.0000,  # 吃单手续费率
        "maker_fee_rate": 0.0000,  # 挂单手续费率
        "trading_toggle": TradingToggle(0),  # 交易开关
        "buy_trading_toggle": TradingToggle(10),  # 做多开关 long(做多)
        "sell_trading_toggle": TradingToggle(10),  # 做空开关 short（做空）
        "stop_loss_type": "both",  # both:两类止损都加; bar:只收盘止损; tick:只瞬间止损
        "trade_type": "taker",  # 目前只支持taker
    }
}


class FmzCtaEngine():
    def __init__(self, engine_config):
        self.engine_config = engine_config
        self._init_gf()
        self._init_gp()
        self._init_gt(engine_config.get("parameters_settings"))  # 该函数后期待删
        self.add_strategy(engine_config.get("strategy_cls"))  # 初始化策略
        self.add_filters(engine_config.get("filter_cls_lst"))  # 添加过滤器到策略
        self.add_chart(engine_config.get("chart_cls"))
        self.update_parameters_settings(engine_config.get("parameters_settings"))

        self.count = 0
        self.stop_count = engine_config.get("stop_count", 60 * 24 * 365)  # 默认一年
        self.strategy.analysis.doc = engine_config.get("doc")

    def add_strategy(self, strategy_cls):
        if isinstance(strategy_cls, type):
            self.strategy = strategy_cls(cta_engine=self)
        else:
            err_msg = f"[导入策略异常]: strategy_cls:{strategy_cls}; {type(strategy_cls)}"
            raise Exception(err_msg)

    def add_filters(self, filter_cls_lst):
        self.strategy.add_filters(filter_cls_lst)

    def add_chart(self, chart_cls):
        "把'fmz_chart对象'同时传入'策略'和'过滤器'中"
        chart_inst = chart_cls(cta_engine=self)
        self.chart = chart_inst
        self.chart.draw_all = self.engine_config["draw_all"]
        self.strategy.add_chart(chart_inst)
        for filter_name, filter_inst in self.strategy.filters.items():
            filter_inst.add_chart(chart_inst)

    def update_parameters_settings(self, parameters_settings):
        "把调参设置同时传入'策略'和'过滤器'、交易、分析模块中"
        self.strategy.update_parameters_settings(parameters_settings)
        for filter_name, filter_inst in self.strategy.filters.items():
            filter_inst.update_parameters_settings(parameters_settings)
        self.strategy.trade.update_parameters_settings(parameters_settings)
        self.strategy.trade.pm.update_parameters_settings(parameters_settings)
        self.strategy.analysis.update_parameters_settings(parameters_settings)

    # 设置全局'fmz对象/方法'

    def _init_gf(self):
        # 设置全局变量
        GF.exchange = exchange
        GF.exchanges = exchanges

        # 全局函数
        GF.version = Version
        GF.Sleep = Sleep
        GF.IsVirtual = IsVirtual
        GF.Mail = Mail
        GF.SetErrorFilter = SetErrorFilter
        GF.GetPid = GetPid
        GF.GetLastError = GetLastError
        GF.GetCommand = GetCommand
        GF.GetMeta = GetMeta
        GF.Dial = Dial
        # GF.HttpQuery = HttpQuery # 实盘中无效
        # GF.Hash = Hash 无效
        # GF.HMAC = HMAC 无效
        GF.UnixNano = UnixNano
        GF.Unix = Unix
        GF.GetOS = GetOS
        GF.MD5 = MD5
        # GF.DBExec = DBExec 无效

        # 内置函数
        GF._G = _G
        GF._D = _D
        GF._N = _N
        GF._C = _C
        GF._Cross = _Cross

        # 日志
        GF.Log = Log
        GF.LogProfit = LogProfit
        GF.LogProfitReset = LogProfitReset
        GF.LogStatus = LogStatus
        GF.EnableLog = EnableLog
        GF.Chart = Chart
        GF.LogReset = LogReset
        GF.LogVacuum = LogVacuum
        GF.Logger = FmzLogger(fmz_log=Log, log_level=self.engine_config["log_level"])  # debug级别

        # 指标
        GF.TA = TA

        GF.doc = __doc__

        # 赋予给strategy对象
        self.GF = GF

    # 设置全局'fmz前端回测环境'
    def _init_gp(self):
        # 1. 判断执行环境
        if GF.IsVirtual():
            GP.ENV = "VIRTUAL"  # 回测环境
        else:
            GP.ENV = "REAL"  # 实盘环境
            if platform.system() == "Darwin":
                # 在mac端本地实盘的时候, 需要设置代理!!
                GF.exchange.SetProxy("socks5://127.0.0.1:7890")
                pass
        # 2. 判断合约类型
        exchange_name = GF.exchange.GetName()
        GF.Logger.log(exchange_name, 10)
        if exchange_name.split("_")[0] == "Futures":
            GF.exchange.SetContractType("swap")
            GF.exchange.SetMarginLevel(20)
            GP.AccountType = "futures"  # 合约
        else:
            GP.AccountType = "spot"  # 现货
        # 3. 获取k线周期
        PERIOD = GF.exchange.GetPeriod()
        GP.PERIOD = PERIOD  # 周期
        # 4. 定义仓位的初始状态
        GP.STATUS = "idle"  # 仓位状态
        # 5. 设置交易精度
        # (价格, 数量) 主要是看数量精度 (因为send_order与价格精度无关)
        exchange.SetPrecision(8, 8)
        # 6. 设置GetRecords()的最大数量
        exchange.SetMaxBarLen(1000)

        # 赋予给strategy对象 （？fmzctaengine 对象）
        self.GP = GP

    # 设置全局'可调参数' (可调参数不需要放在全局, 只需要放策略对象内部即可, 后期待删)
    def _init_gt(self, parameters_settings):
        for name in parameters_settings:
            setattr(GT, name, parameters_settings[name])

    def get_tick(self, tick):
        self.strategy.on_tick(tick)

    def get_bars(self, bars):
        self.strategy.on_bars(bars)

    def draw(self, bars):
        self.strategy.draw(bars, draw_all=self.chart.draw_all)
        for filter_name, filter in self.strategy.filters.items():
            filter.draw(bars, draw_all=self.chart.draw_all)

    def print_variables(self, score=50):
        self.strategy.print_variables(score=score)
        self.strategy.trade.print_variables(score=score)
        for filter_name, filter in self.strategy.filters.items():
            filter.print_variables(score=score)

    def print_parameters(self, score=50):
        self.strategy.print_parameters(score=score)
        self.strategy.trade.print_parameters(score=score)
        for filter_name, filter in self.strategy.filters.items():
            filter.print_parameters(score=score)

    def counting(self):
        "每分钟计时 (达到一定分钟数后, 就会抛出异常, 停止程序)"
        self.count += 1
        if self.count >= self.stop_count:
            err_msg = f"[实盘时间超过约定时间, 退出实盘] count:{self.count}, stop_count:{self.stop_count}"
            raise Exception(err_msg)

    def handle_cmd(self):
        """
        GetCommand()方法大概是5秒执行一次, 所以会有稍许滞后.
        该交互数据是以队列的形式传递, 每次只能取到1个数据, 所以同时上传多个数据, 也会在不同节点分批得到..
        """
        cmd = GF.GetCommand()
        if cmd:
            var, value = cmd.split(":")
            msg = f"var:{var}, value:{value}"
            GF.Log(msg, "#ff0000")

            if var == "open_quote_qty":
                quote_qty = int(value)
                # 这里对开仓金额做了一层保险
                if 5 < quote_qty < 1000:
                    self.strategy.quote_qty = quote_qty

            elif var == "close_times":
                close_times = int(value)
                if close_times > 0:
                    self.strategy.trading_toggle.close(close_times=close_times)
                elif close_times == 0:
                    msg = f"self.strategy.trading_toggle.remaining_times:{self.strategy.trading_toggle.remaining_times}"
                    GF.Log(msg, "#0000ff")
                    self.strategy.trading_toggle.open()
                    msg = f"self.strategy.trading_toggle.remaining_times:{self.strategy.trading_toggle.remaining_times}"
                    GF.Log(msg, "#0000ff")

            elif var == "buy_close_times":
                buy_close_times = int(value)
                if buy_close_times > 0:
                    self.strategy.buy_trading_toggle.close(close_times=buy_close_times)
                elif buy_close_times == 0:
                    self.strategy.buy_trading_toggle.open()

            elif var == "sell_close_times":
                sell_close_times = int(value)
                if sell_close_times > 0:
                    self.strategy.sell_trading_toggle.close(close_times=sell_close_times)
                elif sell_close_times == 0:
                    self.strategy.sell_trading_toggle.open()

            elif var == "stop_count":
                stop_count = int(value)
                if stop_count >= 5:  # 保险层
                    self.count = 0  # 重置
                    self.stop_count = stop_count

        # self.GF.Log(
        #     f"quote_qty:{self.strategy.quote_qty}; toggle:{self.strategy.trading_toggle.toggle};
        #     remaining_times:{self.strategy.trading_toggle.remaining_times}",
        #     "#0000ff"
        # )


# 入口函数
def main():
    try:
        # 初始化
        Log("程序开始...")
        engine = FmzCtaEngine(engine_config)
        Log(__doc__)
        engine.strategy.initialize()
        last_time = 0

        # 循环更新 K线
        while True:
            this_bars = GF._C(GF.exchange.GetRecords, GP.PERIOD)  # 当前所有的bars
            this_bar = this_bars[-1]  # 当前最新的bar
            this_time = this_bar.Time  # 盘中最新时间

            # 获取前端交互数据
            engine.handle_cmd()

            # 获取数据: tick
            engine.get_tick(tick=this_bar)
            # GF.Logger.log(f"this_bar:{this_bar}", 30)

            # 收盘:
            if last_time != this_time:  # 最近时间是否等于当前bar的时间
                historical_bars = fmz.MyList(this_bars[:-1])
                last_bar = historical_bars[-1]
                GF.Logger.log(f"[{GF._D(last_time/1000)}]: 收盘↓↓↓", 51)
                # 获取数据: bars
                engine.get_bars(bars=historical_bars)
                # 画图
                engine.draw(bars=historical_bars)
                # 打印主要的状态变量 (过程值)
                engine.print_variables(score=30)
                engine.print_parameters(score=40)
                # 计数
                engine.counting()
                # 开盘:
                last_time = this_time
                GF.Logger.log("==============================================================", 51)
                GF.Logger.log(f"[{GF._D(this_time/1000)}]:开盘↑↑↑", 51)
                engine.strategy.trade.print_account_msg(exchange=GF.exchange)

            # 睡眠
            if GP.ENV == "VIRTUAL":
                GF.Sleep(1000 * 1)  # 回测睡眠1s
            elif GP.ENV == "REAL":
                GF.Sleep(1000 * 5)  # 实盘睡眠5s (降低访问频次)

    except Exception as e:
        # 扫尾函数
        e = traceback.format_exc(limit=10)
        msg = f"[FMZ报错中断]: {e}"
        Log(msg, "#ff0000")

        onerror(engine=engine)


def onerror(engine):
    try:

        GF.Logger.log("执行扫尾工作...", 90)

        # if GP.ENV == "VIRTUAL":
        #     # 回测中才会去做统计分析
        engine.strategy.analysis.statistics()

        GF.Logger.log("扫尾函数正常结束...", 90)

    except Exception as e:
        e = traceback.format_exc(limit=5)
        msg = f"#### 扫尾函数'非正常'结束: {e}"
        Log(msg, "#ff0000")

    finally:
        LogReset(30000)  # 清除实盘的日志
