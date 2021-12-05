import fmz
import matplotlib.pyplot as plt
import talib
import numpy as np
import math
from abc import ABC
import pandas as pd
import json

from helpers.object import *
from helpers.utils import *
from functools import reduce
from typing import List


# 基础类-画图模块
class BaseChart():

    chart_config = {
        "title": {
            "text": "非横盘状态监测",
        },
        "subtitle": {
            "text": "---K线+过程指标"
        },
        "draw_all": True,
        # 使用Highcharts的图表 (非普通图表)
        '__isStock': True,
        # 缩放工具
        'tooltip': {"xDateFormat": "%Y-%m-%d %H:%M:%S, %A"},
        "extension": {
            "layout": "single",
            "height": "1100px",
            "col": 12,  # 页面宽度一共划分为12个单元，设置8即该图表占用8个单元宽度
        },
        "yAxis": [
            {  # y0
                "top": "0%",
                "height": "60%",
                "lineWidth": 2,  # y轴线的粗细
                "title": {
                    "text": '价格',  # y轴的名称
                },
                "style": {"color": "#4572A7"},
                "tickPixelInterval": 200,  # 横线之间的间隔距离
                "minorGridLineWidth": 1,
                "minorTickWidth": 0,
                "opposite": False,  # y轴放左边
                "labels": {
                    "align": "right",  # 标签的右边与y轴对齐 (即: label放在y轴左边)
                    "x": -3  # lable的位置相对于'y轴'的偏移量
                },
            },
            {  # y1
                # 两个过滤器的area的y轴
                "top": "0%",
                "height": "60%",
                "tickPixelInterval": 200,  # 横线之间的间隔距离
            },
            {  # y2
                # 大罗指标数据 第一个 5%
                "top": "60%",
                "height": "5%",
            },
            {  # y3 大罗指标数据 第二个 5%
                "top": "65%",
                "height": "5%"

            },
            {  # y4
                # 吕一波指标数据
                "top": "70%",
                "height": "5%",
            },
            {  # y5
                "top": "75%",
                "height": "5%",
            },
            {  # y6
                "top": "80%",
                "height": "5%",
            },
            {  # y7
                # 吕一波盈利统计分析
                "top": "85%",
                "height": "10%",
            },
            {  # y8
                "top": "95%",
                "height": "5%",
            },
            {  # y9
                "top": "95%",
                "height": "5%",
            }
        ],
        "series": [
            {
                "name": "K线蜡烛图",
                "type": "candlestick",  # 蜡烛图
                "yAxis": 0,
                "data": [],
            },
            {
                "name": "平均K线蜡烛图",
                "type": "candlestick",  # 蜡烛图
                "yAxis": 4,
                "data": [],
            },
            {
                "name": "布林上轨",
                "type": "spline",
                "yAxis": 0,
                "data": [],
                "color": "blue",
            },
            {
                "name": "布林中轨",
                "type": "spline",
                "yAxis": 0,
                "data": [],
                "color": "purple",
            },
            {
                "name": "布林下轨",
                "type": "spline",
                "yAxis": 0,
                "data": [],
                "color": "blue",
            },
            {
                "name": "EMA慢线",
                "type": "spline",
                "yAxis": 0,
                "data": [],
                "color": "red",
            },
            {
                "name": "EMA快线",
                "type": "spline",
                "yAxis": 0,
                "data": [],
                "color": "pink",
            },
            {
                "name": "SAR",
                "type": "scatter",  # 散点图
                "yAxis": 0,
                "data": [],
                "color": "orange",
                "marker": {  # symbol默认是正方形
                    # "symbol" : "triangle" # 三角形
                    "symbol": "x"  # 无法识别的话, 默认圆点
                }
            },
            {
                "name": "斜率拟合横盘",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#00ff00",
                "fillOpacity": 0.4,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                "name": "BBW值否决",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#ff0000",
                "fillOpacity": 0.4,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                "name": "base_template_flag",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#00ff00",
                "fillOpacity": 0.4,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                # sar过滤器的flag
                "name": "最近段sar过滤器",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#bb0000",
                "fillOpacity": 0.4,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                # 交叉ema
                "name": "交叉ema",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#62cf75", # 绿色
                "fillOpacity": 0.4,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                # 亏损休眠
                "name": "亏损休眠",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#e95a68", # 红色
                "fillOpacity": 0.4,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                # EMA-方向器-做多
                "name": "EMA-方向器-做多",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#FFFF00",
                "fillOpacity": 0.4,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                # EMA-方向器-做空
                "name": "EMA-方向器-做空",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#FFFF00",
                "fillOpacity": 0.2,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                "name": "非横盘倒计时",
                "type": "area",
                "yAxis": 4,
                "data": [],
                "color": "#ff0000",
                "fillOpacity": 0.8,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                "name": "trading_toggle",
                "type": "area",
                "yAxis": 5,
                "data": [],
                "color": "#00ff00",
                "fillOpacity": 0.4,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                "name": "最小布林带宽度*alpha",
                "type": "column",
                "yAxis": 6,
                "data": [],
                "color": "green",
            },
            {
                "name": "SAR首尾差值",
                "type": "column",
                "yAxis": 6,
                "data": [],
                "color": "blue",
            },
            {
                "name": "总资产价值",
                "type": "spline",
                "yAxis": 7,
                "data": [],
                "color": "green",
            },
            {
                "name": "总资产价值涨跌",
                "type": "column",
                "yAxis": 8,
                "data": [],
                "color": "red",
            },
            {
                "name": "总资产价值涨幅",
                "type": "column",
                "yAxis": 9,
                "data": [],
                "color": "blue",
            },
            {
                "name": "判断为横盘-打勾",
                "type": "scatter",
                "yAxis": 0,
                "data": [],
                "marker": {
                    # ✅ 绿色打勾
                    "symbol": "url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAKT2lDQ1BQaG90b3Nob3AgSUNDIHByb2ZpbGUAAHjanVNnVFPpFj333vRCS4iAlEtvUhUIIFJCi4AUkSYqIQkQSoghodkVUcERRUUEG8igiAOOjoCMFVEsDIoK2AfkIaKOg6OIisr74Xuja9a89+bN/rXXPues852zzwfACAyWSDNRNYAMqUIeEeCDx8TG4eQuQIEKJHAAEAizZCFz/SMBAPh+PDwrIsAHvgABeNMLCADATZvAMByH/w/qQplcAYCEAcB0kThLCIAUAEB6jkKmAEBGAYCdmCZTAKAEAGDLY2LjAFAtAGAnf+bTAICd+Jl7AQBblCEVAaCRACATZYhEAGg7AKzPVopFAFgwABRmS8Q5ANgtADBJV2ZIALC3AMDOEAuyAAgMADBRiIUpAAR7AGDIIyN4AISZABRG8lc88SuuEOcqAAB4mbI8uSQ5RYFbCC1xB1dXLh4ozkkXKxQ2YQJhmkAuwnmZGTKBNA/g88wAAKCRFRHgg/P9eM4Ors7ONo62Dl8t6r8G/yJiYuP+5c+rcEAAAOF0ftH+LC+zGoA7BoBt/qIl7gRoXgugdfeLZrIPQLUAoOnaV/Nw+H48PEWhkLnZ2eXk5NhKxEJbYcpXff5nwl/AV/1s+X48/Pf14L7iJIEyXYFHBPjgwsz0TKUcz5IJhGLc5o9H/LcL//wd0yLESWK5WCoU41EScY5EmozzMqUiiUKSKcUl0v9k4t8s+wM+3zUAsGo+AXuRLahdYwP2SycQWHTA4vcAAPK7b8HUKAgDgGiD4c93/+8//UegJQCAZkmScQAAXkQkLlTKsz/HCAAARKCBKrBBG/TBGCzABhzBBdzBC/xgNoRCJMTCQhBCCmSAHHJgKayCQiiGzbAdKmAv1EAdNMBRaIaTcA4uwlW4Dj1wD/phCJ7BKLyBCQRByAgTYSHaiAFiilgjjggXmYX4IcFIBBKLJCDJiBRRIkuRNUgxUopUIFVIHfI9cgI5h1xGupE7yAAygvyGvEcxlIGyUT3UDLVDuag3GoRGogvQZHQxmo8WoJvQcrQaPYw2oefQq2gP2o8+Q8cwwOgYBzPEbDAuxsNCsTgsCZNjy7EirAyrxhqwVqwDu4n1Y8+xdwQSgUXACTYEd0IgYR5BSFhMWE7YSKggHCQ0EdoJNwkDhFHCJyKTqEu0JroR+cQYYjIxh1hILCPWEo8TLxB7iEPENyQSiUMyJ7mQAkmxpFTSEtJG0m5Si +ksqZs0SBojk8naZGuyBzmULCAryIXkneTD5DPkG+Qh8lsKnWJAcaT4U+IoUspqShnlEOU05QZlmDJBVaOaUt2ooVQRNY9aQq2htlKvUYeoEzR1mjnNgxZJS6WtopXTGmgXaPdpr+h0uhHdlR5Ol9BX0svpR+iX6AP0dwwNhhWDx4hnKBmbGAcYZxl3GK+YTKYZ04sZx1QwNzHrmOeZD5lvVVgqtip8FZHKCpVKlSaVGyovVKmqpqreqgtV81XLVi +pXlN9rkZVM1PjqQnUlqtVqp1Q61MbU2epO6iHqmeob1Q/pH5Z/YkGWcNMw09DpFGgsV/jvMYgC2MZs3gsIWsNq4Z1gTXEJrHN2Xx2KruY/R27iz2qqaE5QzNKM1ezUvOUZj8H45hx+Jx0TgnnKKeX836K3hTvKeIpG6Y0TLkxZVxrqpaXllirSKtRq0frvTau7aedpr1Fu1n7gQ5Bx0onXCdHZ4/OBZ3nU9lT3acKpxZNPTr1ri6qa6UbobtEd79up+6Ynr5egJ5Mb6feeb3n+hx9L/1U/W36p/VHDFgGswwkBtsMzhg8xTVxbzwdL8fb8VFDXcNAQ6VhlWGX4YSRudE8o9VGjUYPjGnGXOMk423GbcajJgYmISZLTepN7ppSTbmmKaY7TDtMx83MzaLN1pk1mz0x1zLnm+eb15vft2BaeFostqi2uGVJsuRaplnutrxuhVo5WaVYVVpds0atna0l1rutu6cRp7lOk06rntZnw7Dxtsm2qbcZsOXYBtuutm22fWFnYhdnt8Wuw+6TvZN9un2N/T0HDYfZDqsdWh1+c7RyFDpWOt6azpzuP33F9JbpL2dYzxDP2DPjthPLKcRpnVOb00dnF2e5c4PziIuJS4LLLpc+Lpsbxt3IveRKdPVxXeF60vWdm7Obwu2o26/uNu5p7ofcn8w0nymeWTNz0MPIQ+BR5dE/C5+VMGvfrH5PQ0+BZ7XnIy9jL5FXrdewt6V3qvdh7xc+9j5yn+M+4zw33jLeWV/MN8C3yLfLT8Nvnl+F30N/I/9k/3r/0QCngCUBZwOJgUGBWwL7+Hp8Ib+OPzrbZfay2e1BjKC5QRVBj4KtguXBrSFoyOyQrSH355jOkc5pDoVQfujW0Adh5mGLw34MJ4WHhVeGP45wiFga0TGXNXfR3ENz30T6RJZE3ptnMU85ry1KNSo+qi5qPNo3ujS6P8YuZlnM1VidWElsSxw5LiquNm5svt/87fOH4p3iC+N7F5gvyF1weaHOwvSFpxapLhIsOpZATIhOOJTwQRAqqBaMJfITdyWOCnnCHcJnIi/RNtGI2ENcKh5O8kgqTXqS7JG8NXkkxTOlLOW5hCepkLxMDUzdmzqeFpp2IG0yPTq9MYOSkZBxQqohTZO2Z+pn5mZ2y6xlhbL+xW6Lty8elQfJa7OQrAVZLQq2QqboVFoo1yoHsmdlV2a/zYnKOZarnivN7cyzytuQN5zvn//tEsIS4ZK2pYZLVy0dWOa9rGo5sjxxedsK4xUFK4ZWBqw8uIq2Km3VT6vtV5eufr0mek1rgV7ByoLBtQFr6wtVCuWFfevc1+ 1dT1gvWd+ 1YfqGnRs+FYmKrhTbF5cVf9go3HjlG4dvyr+Z3JS0qavEuWTPZtJm6ebeLZ5bDpaql+aXDm4N2dq0Dd9WtO319kXbL5fNKNu7g7ZDuaO/PLi8ZafJzs07P1SkVPRU+lQ27tLdtWHX+G7R7ht7vPY07NXbW7z3/T7JvttVAVVN1WbVZftJ+7P3P66Jqun4lvttXa1ObXHtxwPSA/0HIw6217nU1R3SPVRSj9Yr60cOxx+ 1/p3vdy0NNg1VjZzG4iNwRHnk6fcJ3/ceDTradox7rOEH0x92HWcdL2pCmvKaRptTmvtbYlu6T8w+0dbq3nr8R9sfD5w0PFl5SvNUyWna6YLTk2fyz4ydlZ19fi753GDborZ752PO32oPb+ 16EHTh0kX/i +c7vDvOXPK4dPKy2+UTV7hXmq86X23qdOo8/pPTT8e7nLuarrlca7nuer21e2b36RueN87d9L158Rb/1tWeOT3dvfN6b/fF9/XfFt1+cif9zsu72Xcn7q28T7xf9EDtQdlD3YfVP1v+3Njv3H9qwHeg89HcR/cGhYPP/pH1jw9DBY+Zj8uGDYbrnjg+OTniP3L96fynQ89kzyaeF/6i/suuFxYvfvjV69fO0ZjRoZfyl5O/bXyl/erA6xmv28bCxh6+yXgzMV70VvvtwXfcdx3vo98PT+R8IH8o/2j5sfVT0Kf7kxmTk/8EA5jz/GMzLdsAAAAgY0hSTQAAeiUAAICDAAD5/wAAgOkAAHUwAADqYAAAOpgAABdvkl/FRgAAAVVJREFUeNpi/P37NwOxYM2pHtm7lw8uYmBgYGAiVtPC3RWh+88vuneT474Dv4DkcUZibJy8PG72le/nkn+zMzAaMhnNyY1clMpCjKbz/86lMLAzMMA0MTAwMOC1Ea6JgYFB9pPwncbMg6owOaY1p3pk15zqkcWnie8j63ddY18nZHmWI2eW3vzN/Jf168c3UfGuHathAXHl+7lkBnYGBtafDP8NVd3jQ8xKHiNrZMyeqPPtE/9vTgYGBgb1H4oHlHXt43ZfWfDwNzsDIwMDA4POX831RXGrg9BdxLhob63VgTurjsAUsv5k+A9jC3/g/NCdfVoQm/+ZIu3qjhnyW3XABJANMNL19cYVcPBQrZpq9eyFwCdJmIT6D8UD5cmbHXFphKccI9Mgc84vTH9goYhPE4rGELOSx0bSjsUMDAwMunJ2FQST0+/fv1Hw5BWJbehi2DBgAHTKsWmiz+rJAAAAAElFTkSuQmCC)",  # ✅打勾
                }
            },
            {
                "name": "不能判断为横盘-打叉",
                "type": "scatter",
                "yAxis": 0,
                "data": [],
                "marker": {
                    # ❎ 红色叉叉
                    "symbol": 'url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAABJklEQVQ4jc2SPU7DQBCF37NJkO3Clg+AIosb+BRAAQEFJTLHQ8jGMVRAmwvkBihKQRWJiMJBMsE7NLHxXwMNvG41877dfTPAv5L4fk98v/eTulYtpo4ebRz9Xo4O97vM7/ZemDp6VIWUAHieIiQDcLL5cJMqpIAL5ZyQDJ6nihprt4xG+ma9vAY4BvBg9dcXWNkqdfSIwBBgZLkHAeM47wS0IIJH0bCl4BSCW0uZAWezz2p/C1BCXpc3IC93/5wauTlpmusZVLVYaEKtXxyVwITxone1tgBFYIScEUwAiUAcN4PtBHybMSQwNXNjbLmDAJAQHdOpZVA3S2K+qQnn822ZSWM6fHrO6i/Y7QGFd1UzADCOc8sdXAESUphhZSt06Ter/Pf6AoTylJNA9HjXAAAAAElFTkSuQmCC)',
                }
            },
            {
                'name': "最终横盘显示",
                'type': "area",
                'data': [],
                'color': '#00FF00',
                'fillOpacity': 0.1,
                'step': True,
                'lineWidth': 0,
                'yAxis': 1
            },
            {
                "name": "开多",
                "type": "scatter",
                "yAxis": 0,
                "data": [],
                "marker": {
                    # uparrow
                    "symbol": 'url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABmJLR0QA/wD/AP+gvaeTAAABLUlEQVRIie3Wv0vDQBQH8O8lh6YQkQo6uOng4l+gFLlFROyg0Fv0n1MHF3EQHBRRior/gZODi5AE6dKW5ghenpPShjS8ECgI+W53eY/Py08CzCCiTDEpJaOFdKfn9V42L98Sbp/DBrR2I9+eEqUPS6Z5/aGUx+1lnQlp7UZxeEagk7HOWzOQR2vdrqmM5AIloUKEtHaDODgXwHFB2Z0ZysMiaCrCBFhQ7o0nQISj4IIJAMCe59srUkqykc/21ioEOkzgd7T9cNFu5B2Zermig9a6BZp/hQKvAOYmJ0y3LTkJAEjh9Fdunt5LIdkE7ZYBMD++Z4aywXmE2S9jldRIjdTIP0TSzJpGy1/ZvYqIwOPkmp65PxO53/+8mIHsNPzvXSJ4whFJiviePeAs8gOgHXdBn94bjAAAAABJRU5ErkJggg==)',
                }
            },
            {
                "name": "平空",
                "type": "scatter",
                "yAxis": 0,
                "data": [],
                "marker": {
                    # 红色横线
                    "symbol": 'url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABmJLR0QA/wD/AP+gvaeTAAAAR0lEQVRIiWNgGAWjYBSMAqoCRgYGBobn3tbx/xkY2alv+P+fkluPLmR8HGrJyfKd+Ru1LYCBP5x/uejiE2qbOwpGwSgY8QAA1hcTfiEYLwgAAAAASUVORK5CYII=)'
                    # # uparrow
                    # "symbol": 'url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABmJLR0QA/wD/AP+gvaeTAAABLUlEQVRIie3Wv0vDQBQH8O8lh6YQkQo6uOng4l+gFLlFROyg0Fv0n1MHF3EQHBRRior/gZODi5AE6dKW5ghenpPShjS8ECgI+W53eY/Py08CzCCiTDEpJaOFdKfn9V42L98Sbp/DBrR2I9+eEqUPS6Z5/aGUx+1lnQlp7UZxeEagk7HOWzOQR2vdrqmM5AIloUKEtHaDODgXwHFB2Z0ZysMiaCrCBFhQ7o0nQISj4IIJAMCe59srUkqykc/21ioEOkzgd7T9cNFu5B2Zermig9a6BZp/hQKvAOYmJ0y3LTkJAEjh9Fdunt5LIdkE7ZYBMD++Z4aywXmE2S9jldRIjdTIP0TSzJpGy1/ZvYqIwOPkmp65PxO53/+8mIHsNPzvXSJ4whFJiviePeAs8gOgHXdBn94bjAAAAABJRU5ErkJggg==)',
                }
            },
            {
                "name": "开空",
                "type": "scatter",
                "yAxis": 0,
                "data": [],
                "marker": {
                    # downarrow
                    "symbol": 'url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABmJLR0QA/wD/AP+gvaeTAAABPklEQVRIie3Wv0rDUBQG8O/cpLaDJnZXEF2U+gcpLoLVgji4ieDgA7jrE+QBRMR3cIoOTgoOBRGH6iBSKyhKh7oWGxUkpTlOipaknisqDjlbON93fzdLCPAHQ9JgX8FJWZ3eHBOSQNCghHl4Mbb+LOmaUsTqqu8CmKe3u/nBEYBpSVdJEQD5T0/EU9mzlcRPI61ZqttJUV8H+fbESIzEyD9BIr/CI6er/VAq/R7k4ARAx8cMK54EGz4AGKrhnY9v3YiR4eJar1Jcgd6bckCcKWU3r1oXoYeUJjaqDOxoAACwP3R7fx22CL8pgQfvqssE2hYdzzjwHu1Fd8lthq2NqF7ZLXNutmevlrYHAIy2BZ7shUreeYmKRCIiSAB8ibSFhIAICYU0AEDjbwUAZgqOWbMecs1U9/FlxvF1ur8+r2eydL/lD7S/AAAAAElFTkSuQmCC)',
                }
            },
            {
                "name": "平多",
                "type": "scatter",
                "yAxis": 0,
                "data": [],
                "marker": {
                    # 红色横线
                    "symbol": 'url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABmJLR0QA/wD/AP+gvaeTAAAAR0lEQVRIiWNgGAWjYBSMAqoCRgYGBobn3tbx/xkY2alv+P+fkluPLmR8HGrJyfKd+Ru1LYCBP5x/uejiE2qbOwpGwSgY8QAA1hcTfiEYLwgAAAAASUVORK5CYII=)'
                    # # downarrow
                    # "symbol": 'url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABmJLR0QA/wD/AP+gvaeTAAABPklEQVRIie3Wv0rDUBQG8O/cpLaDJnZXEF2U+gcpLoLVgji4ieDgA7jrE+QBRMR3cIoOTgoOBRGH6iBSKyhKh7oWGxUkpTlOipaknisqDjlbON93fzdLCPAHQ9JgX8FJWZ3eHBOSQNCghHl4Mbb+LOmaUsTqqu8CmKe3u/nBEYBpSVdJEQD5T0/EU9mzlcRPI61ZqttJUV8H+fbESIzEyD9BIr/CI6er/VAq/R7k4ARAx8cMK54EGz4AGKrhnY9v3YiR4eJar1Jcgd6bckCcKWU3r1oXoYeUJjaqDOxoAACwP3R7fx22CL8pgQfvqssE2hYdzzjwHu1Fd8lthq2NqF7ZLXNutmevlrYHAIy2BZ7shUreeYmKRCIiSAB8ibSFhIAICYU0AEDjbwUAZgqOWbMecs1U9/FlxvF1ur8+r2eydL/lD7S/AAAAAElFTkSuQmCC)',
                }
            },
            {
                "name": "收盘止损价",
                "type": "scatter",
                "marker": {
                    # 黄色横线
                    "symbol": 'url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABmJLR0QA/wD/AP+gvaeTAAAASUlEQVRIiWNgGAWjYBSMAqoCRgYGBoZPRwTi//3/z05tw5kYGX/y2XxYyPj/mAznp3+fv1HbAhjgY+LlootPqG3uKBgFo2DEAwDWVhXuQ5ViLgAAAABJRU5ErkJggg==)'
                },
                "yAxis": 0,
                "data": [],
            },
            {
                "name": "盘中瞬时止损价",
                "type": "scatter",
                "marker": {
                    # 红色横线
                    "symbol": 'url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABmJLR0QA/wD/AP+gvaeTAAAAR0lEQVRIiWNgGAWjYBSMAqoCRgYGBobn3tbx/xkY2alv+P+fkluPLmR8HGrJyfKd+Ru1LYCBP5x/uejiE2qbOwpGwSgY8QAA1hcTfiEYLwgAAAAASUVORK5CYII=)'
                },
                "yAxis": 0,
                "data": [],
            },
            {
                "name": "网格上轨",
                "type": "scatter",
                "marker": {
                    # 黑色横线
                    "symbol": 'url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAAJUlEQVRIiWNgGAWjYBSMAoKAEYn9nxZmM1HZ0FEwCkbBKCAHAAD4CQEEQU/AbwAAAABJRU5ErkJggg==)'
                },
                "yAxis": 0,
                "data": [],
            },
            {
                "name": "网格下轨",
                "type": "scatter",
                "marker": {
                    # 黑色横线
                    "symbol": 'url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAAJUlEQVRIiWNgGAWjYBSMAoKAEYn9nxZmM1HZ0FEwCkbBKCAHAAD4CQEEQU/AbwAAAABJRU5ErkJggg==)'
                },
                "yAxis": 0,
                "data": [],
            },
            {
                "name": "开仓屏蔽次数",
                "type": "area",
                "yAxis": 3,
                "data": [],
                "color": "green",
                "fillOpacity": 0.2,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                "name": "BBW视图",
                "type": "spline",
                "yAxis": 2,
                "data": [],
                "color": "black",
            },
            {
                "name": "收盘价突破布林倒计时-辅图",
                "type": "area",
                "yAxis": 3,
                "data": [],
                "color": "#ff0000",
                "fillOpacity": 0.8,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                "name": "收盘价突破布林倒计时-主图",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#ff0000",
                "fillOpacity": 0.4,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                # DC 肯定器
                "name": "DC-肯定器",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#4aa4eb",
                "fillOpacity": 0.4,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                # DC 否定器
                "name": "DC-否定器",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#bb0000",
                "fillOpacity": 0.3,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                # 马浩专用
                "name": "Filter-Tempt",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#bb0000",
                "fillOpacity": 0.3,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                 # 指定概率随机否定器
                "name": "概率-否定器",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#bb0000",
                "fillOpacity": 0.3,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                # 七巧板 肯定器
                "name": "七巧板-肯定器",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#4aa4eb",
                "fillOpacity": 0.4,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                # 七巧板 方向过滤器
                "name": "七巧板-方向过滤器-开多",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#4aa4eb",
                "fillOpacity": 0.4,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                # 七巧板 肯定器
                "name": "七巧板-方向过滤器-开空",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#bb0000",
                "fillOpacity": 0.4,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                #耦合多指标-肯定器
                "name": "耦合多指标-肯定器",
                "type": "area",
                "yAxis": 1,
                "data": [],
                "color": "#4aa4eb",
                "fillOpacity": 0.4,  # 设置透明度
                "step": True,  # 绘制的是'正方形'
                "lineWidth": 0,
            },
            {
                "name": "EMA-收盘价",
                "type": "spline",
                "yAxis": 0,
                "data": [],
                "color": "red",
                "fillOpacity": 0.5,  # 设置透明度
            },
            {
                "name": "EMA-最高价",
                "type": "spline",
                "yAxis": 0,
                "data": [],
                "color": "#4aa4eb",
                "fillOpacity": 0.5,  # 设置透明度
            },
            {
                "name": "EMA-最低价",
                "type": "spline",
                "yAxis": 0,
                "data": [],
                "color": "#bb0000",
                "fillOpacity": 0.5,  # 设置透明度
            },
        ],
    }

    def __init__(self, cta_engine):
        # 初始化
        self.cta_engine = cta_engine  # cta_engine (fmz中会有fmz的cta_engine)
        self.GF = self.cta_engine.GF
        self.GP = self.cta_engine.GP
        # 画出所有中间过程的数据!!
        self.draw_all = self.chart_config.get("draw_all", True)
        self.fmz_chart = self.GF.Chart([self.chart_config])
        self.fmz_chart.reset()

    def get_series_index(self, chart_config, name):
        # 如果没有的话， 动态的插入
        series_lst = chart_config.get("series")
        for i, d in enumerate(series_lst):
            if name == d.get("name"):
                return i
        msg = f"[chart_config中没有该series_name] name:{name}"
        raise Exception(msg)

    def draw_operation(self, price, name="开多", draw_offset=1):
        "针对策略类的开平仓操作画图 (所以该函数是需要依赖'策略实例'的'trade模块')"
        if price == -1:
            # 市价下单才画图 (挂单不画图)
            if name == "开多" or name == "开空":
                time = self.strategy.bar.time
            elif name == "平多" or name == "平空":
                time = self.strategy.tick.time
            latest_price = self.strategy.tick.price
            draw_price = latest_price * draw_offset
            self.strategy.chart.fmz_chart.add(
                self.get_series_index(self.strategy.chart.chart_config, name),
                [time, draw_price]
            )


# 基础类-策略类
class BaseStrategy():
    author = "kerwin"
    parameters = [
        "base_qty", "quote_qty",
        "trading_toggle", "buy_trading_toggle", "sell_trading_toggle"
    ]
    variables = []

    def __init__(self, cta_engine):
        # 初始化
        self.tick = FmzTickData()
        self.bar = FmzBarData()
        self.bars = []  # List(FmzBarData(), FmzBarData(), ...)
        self.ie = IndicatorsExtension()  # 指标扩展对象
        self.filters = {}
        self.cta_engine = cta_engine  # cta_engine (fmz中会有fmz的cta_engine)
        self.chart_vars = {}
        self.GF = self.cta_engine.GF
        self.GP = self.cta_engine.GP

        # 添加策略必备的'子组件'
        self.add_trade(BaseTrade)
        self.add_pm(BasePositionManager)
        self.add_analysis(BaseAnalysis)

    def add_trade(self, trade_cls):
        self.trade = trade_cls(strategy_inst=self)

    def add_pm(self, pm_cls):
        "添加仓位管理模块"
        pm_inst = pm_cls(strategy_inst=self)
        self.trade.pm = pm_inst

    def add_opener(self, opener_cls):
        "添加开仓器模块"
        opener_inst = opener_cls(strategy_inst=self)
        self.trade.opener = opener_inst

    def add_analysis(self, analysis_cls):
        self.analysis = analysis_cls(strategy_inst=self)
        total_capital_value = self.analysis.get_total_capital_value(
            exchange=self.GF.exchange)  # 获取总资产的初始价值
        self.analysis.total_capital_value = total_capital_value  # 赋予给analysis模块

    def update_parameters_settings(self, parameters_settings: dict):
        """
        Update strategy parameter wtih value in setting dict.
        """
        # 这个parameters_settings就是传入需要修改的'parameters'
        for name in self.parameters:
            if name in parameters_settings:
                msg = f"name:{name}; value:{parameters_settings[name]}"
                self.GF.Logger.log(msg, 10)
                setattr(self, name, parameters_settings[name])

    def add_filters(self, filter_cls_lst):
        for filter_cls in filter_cls_lst:
            filter_cls_name = filter_cls.__name__
            filter_inst = filter_cls(strategy_inst=self)
            self.filters.update({filter_cls_name: filter_inst})

    def add_chart(self, chart_inst):
        self.chart = chart_inst
        self.chart.strategy = self

    def initialize(self):
        pass

    def trans_f_to_s(self, filters):
        """肯定器和否定器的解释
        为了规范理解，如下约定
        约定：
            1. 肯定器是: 1 表示肯定，0 表示否定
            2. 否定器: 1 代表否定， 0 表示否定
            3. 方向器: 1 表示只能做多， -1 表示只能做空， 0 表示可以多空
        """
        pos_neg_signal = 0
        director_signal = 0

        affirmer_flags = [] # 肯定器列表
        negetor_flags = [] # 否定器列表
        director_flags = [] # 方向器列表（1 代表只能多， 0 可以空）

        def muti(x, y):
            return x * y

        def sum(x, y):
            return x + y

        # 1.过滤分类，过滤器的 flag 值集合
        for f_name, filter in filters.items():
            if filter.filter_type == "Affirmer":
                affirmer_flags.append(filter.flag)
            elif filter.filter_type == "Negator":
                if f_name == "FilterSidewaySar": # dirty code 遗留问题
                    sar_flag = 0 if filter.flag == 1 else 1
                    negetor_flags.append(sar_flag)
                else:
                    negetor_flags.append(filter.flag)
            elif filter.filter_type == "Director":
                if f_name == "FilterEma": # dirty code 遗留问题
                    director_flags.append(0)
                else:
                    director_flags.append(filter.flag)

        self.GF.Logger.log(f"肯定器:{affirmer_flags} 否定器: {negetor_flags} 方向器:{director_flags}.....", 50)

        # 2. 对肯定器和否定器的集合做布尔计算
        if affirmer_flags and len(negetor_flags) == 0:
            if reduce(sum, affirmer_flags):
                pos_neg_signal = 1
            else:
                pos_neg_signal = 0
        elif affirmer_flags and negetor_flags:
            if reduce(sum, affirmer_flags) and reduce(sum, affirmer_flags) == 0:
                pos_neg_signal = 1
            else:
                pos_neg_signal = 0
        elif len(affirmer_flags) == 0 and negetor_flags:
            if not reduce(sum, negetor_flags):
                pos_neg_signal = 1
            else:
                pos_neg_signal = 0
        elif len(affirmer_flags) == 0 and len(negetor_flags) == 0: #认为是测试的情况 可以开仓
            pos_neg_signal = 1

        # 3. 对方向过滤器做计算
        if director_flags:
            if  len(set(director_flags)) == 1: # 方向过滤器
                director_signal = director_flags[0] # 开仓方向的信号
            else:
                raise Exception("the director error ......")


        return pos_neg_signal, director_signal

    def through_filters(self, bars):
        "在执行策略之前, 统一处理过滤器的信号"
        for filter_name, filter in self.filters.items():
            filter.on_bars(bars)

        open_pos_signal, director_signal = self.trans_f_to_s(self.filters)
        self.GF.Logger.log(f"获取开仓信号： {open_pos_signal}", 20)
        if not open_pos_signal:
            self.trading_toggle.close(1)

        if director_signal == 1:
            self.sell_trading_toggle.close(1)
        elif director_signal == -1:
            self.buy_trading_toggle.close(1)
        elif director_signal == 0:
            pass

    def on_tick(self, tick):
        # 更新tick数据
        self.tick.time = tick.Time
        self.tick.price = tick.Close
        # 获得 tick 信号
        self.get_tick_indicators()
        self.get_tick_signals()
        # 处理 tick 信号
        self.process_tick_signals()

    def on_bars(self, bars): #【谁发送数据给他的呢？engine】
        """
        function: bar数据获取的源头, 会把数据不断传递给 on_bar
            (衔接fmz和vnpy的函数)
        """
        # self.bars_queue.append_bar(bars[-1])
        # bars = self.bars_queue.get_bars()
        # GF.Log(f"bars的长度:{len(bars)}; bars:{bars}")
        self.bars = bars
        bar = self.bars[-1]
        # 1. 每次收盘后, 会首先更新"开仓锁"
        self.trading_toggle.update()
        self.buy_trading_toggle.update()
        self.sell_trading_toggle.update()
        # 2. 过滤器筛选
        self.through_filters(bars) #【发送数据给过滤器】
        # 3. 传递bar数据
        self.on_bar(bar)
        # 4. 获取今日总资产价值的涨跌情况
        self.analysis.get_delta_capital_value(exchange=self.GF.exchange)

    def on_bar(self, bar):
        # 更新bar数据
        self.bar.time = bar.Time
        self.bar.open_price = bar.Open
        self.bar.high_price = bar.High
        self.bar.low_price = bar.Low
        self.bar.close_price = bar.Close
        self.bar.volume = bar.Volume
        # 获得 bar 信号
        self.get_bar_indicators()
        self.get_bar_signals()
        # 处理 bar 信号
        self.process_bar_signals() #交易在里面进行

    def get_tick_indicators(self):
        """
        获取 tick 的指标
        """
        self.tick.indicators = {}

    def get_tick_signals(self) -> bool:
        """
        获取 tick 的信号
        """
        self.tick.signals = []

    def process_tick_signals(self):
        """
        处理 tick 的信号
        """
        # '瞬时止损单'检查:
        self.trade.check_stop_loss_tick(exchange=GF.exchange)

    def get_bar_indicators(self):
        """
        获取 bar 的指标
        """
        self.bar.indicators = {}

    def get_bar_signals(self):
        """
        获取 bar 的信号
        """
        self.bar.signals = []

    def process_bar_signals(self):
        """
        处理 bar 的信号
        """
        # 1. '挂单止盈单'检查:
        self.trade.check_stop_profit_maker(exchange=GF.exchange)

        # 2. '收盘止损单'检查:
        self.trade.check_stop_loss_bar(exchange=GF.exchange)

    def draw(self, bars, draw_all=True):
        # i. k线图
        self.chart.fmz_chart.add(
            self.chart.get_series_index(self.chart.chart_config, "K线蜡烛图"),
            [self.bar.time, self.bar.open_price, self.bar.high_price, self.bar.low_price, self.bar.close_price]
        )

        # ii. 布林轨
        boll_price_dict = self.ie.get_boll_price_dict(bars=self.bars)
        # 上轨
        self.chart.fmz_chart.add(self.chart.get_series_index(
            self.chart.chart_config, "布林上轨"), [self.bar.time, boll_price_dict[2]])
        # 中轨
        self.chart.fmz_chart.add(self.chart.get_series_index(
            self.chart.chart_config, "布林中轨"), [self.bar.time, boll_price_dict[0]])
        # 下轨
        self.chart.fmz_chart.add(self.chart.get_series_index(
            self.chart.chart_config, "布林下轨"), [self.bar.time, boll_price_dict[-2]])

        # iii. SAR
        high_arr = self.bars.High
        low_arr = self.bars.Low
        sar_arr = talib.SAR(high_arr, low_arr)
        sar = sar_arr[-1]  # 获取最新的sar值 (把最后一个元素作为sar的值)
        self.chart.fmz_chart.add(self.chart.get_series_index(
            self.chart.chart_config, "SAR"), [self.bar.time, sar])

        # iv. 开仓锁
        toggle = 1 if self.trading_toggle.toggle else 0
        self.chart.fmz_chart.add(self.chart.get_series_index(
            self.chart.chart_config, "trading_toggle"), [self.bar.time, toggle])

        # v. 总资产价值
        self.chart.fmz_chart.add(self.chart.get_series_index(self.chart.chart_config, "总资产价值"), [
                                 self.bar.time, self.analysis.total_capital_value])
        self.chart.fmz_chart.add(self.chart.get_series_index(self.chart.chart_config, "总资产价值涨跌"), [
                                 self.bar.time, self.analysis.delta_capital_value])

    def print_variables(self, score=50):
        "打印全局状态变量"
        main_status_dict = {}
        for v_name in self.variables:
            v_value = self.__getattribute__(v_name)
            main_status_dict.update({v_name : v_value})
        self.GF.Logger.log(f"[策略-全局状态变量]: {main_status_dict}", score)

    def print_parameters(self, score=50):
        "打印可调参数"
        main_status_dict = {}
        for v_name in self.parameters:
            v_value = self.__getattribute__(v_name)
            main_status_dict.update({v_name : v_value})
        self.GF.Logger.log(f"[策略-可调参数]: {main_status_dict}", score)

    def print_toggle(self, score=50):
        "打印toggle的remaining_times"
        toggle_dict = {
            "trading_toggle.remaining_times" : self.trading_toggle.remaining_times,
            "buy_trading_toggle.remaining_times" : self.buy_trading_toggle.remaining_times,
            "sell_trading_toggle.remaining_times" : self.sell_trading_toggle.remaining_times,
        }
        self.GF.Logger.log(f"[toggle参数]: {toggle_dict}", score)


# 基础类-过滤器类
class BaseFilter():
    author = "kerwin"
    parameters = []
    variables = []
    filter_type = "Negator"

    def __init__(self, strategy_inst):
        # 初始化
        self.strategy = strategy_inst
        self.GF = self.strategy.GF
        self.tick = FmzTickData()
        self.bar = FmzBarData()
        self.bars = []  # List(FmzBarData(), FmzBarData(), ...)
        self.ie = IndicatorsExtension()  # 指标扩展对象
        self.flag = 1 # 允许/禁止开仓(做多/做空都行) (1:允许; 0:禁止)
        # # 下面这两个flag的优先级要高于flag (如果被禁止做多, 则上面)
        # self.buy_flag = 1 # 允许/禁止做多 (1:允许; 0:禁止)
        # self.sell_flag = 1 # 允许/禁止做多 (1:允许; 0:禁止)
        # 需要画中间过程的变量值 (存在该字典中, 若draw_all为True, 则会在分钟结束后画出这些变量值)
        self.chart_vars = {}

    def update_parameters_settings(self, parameters_settings: dict):
        """
        Update strategy parameter wtih value in setting dict.
        """
        # 这个parameters_settings就是传入需要修改的'parameters'
        for name in self.parameters:
            if name in parameters_settings:
                setattr(self, name, parameters_settings[name])

    def add_chart(self, chart_inst):
        self.chart = chart_inst

    def on_bars(self, bars): #【谁把数据发给他的呢？engine 是最合适的。】
        self.bars = bars
        bar = self.bars[-1]
        # 传递bar数据
        self.on_bar(bar) #【 send bar 数据！】
        # 得到最终的flag
        self.get_filter_flag(bars) #【 send bars 数据！】

    def on_bar(self, bar):
        # 更新bar数据
        self.bar.time = bar.Time
        self.bar.open_price = bar.Open
        self.bar.high_price = bar.High
        self.bar.low_price = bar.Low
        self.bar.close_price = bar.Close
        self.bar.volume = bar.Volume

    def get_filter_flag(self, bars):
        """
        输入: bars
        功能: 计算过滤器指标
        输出: self.flag (0:过滤, 1:不过滤)
        """
        if bars:
            self.flag = 1
        else:
            self.flag = 0

    def draw(self, bars, draw_all=True):
        self.chart.fmz_chart.add(
            self.chart.get_series_index(self.chart.chart_config, "base_template_flag"),
            [self.bar.time, self.flag]
        )

    def print_variables(self, score=50):
        "打印全局状态变量"
        main_status_dict = {}
        for v_name in self.variables:
            v_value = self.__getattribute__(v_name)
            main_status_dict.update({v_name : v_value})
        self.GF.Logger.log(f"[过滤器-全局状态变量]: {main_status_dict}", score)

    def print_parameters(self, score=50):
        "打印可调参数"
        main_status_dict = {}
        for v_name in self.parameters:
            v_value = self.__getattribute__(v_name)
            main_status_dict.update({v_name : v_value})
        self.GF.Logger.log(f"[过滤器-可调参数]: {main_status_dict}", score)

    def print_remaining_times(self, score=50):
        "打印timer的剩余倒计时次数"
        self.GF.Logger.log(f"[过滤器-倒计时次数]: {self.timer.remaining_times}", score)


# 基础类-交易模块
class BaseTrade():
    author = "kerwin"
    parameters = [
        "base_qty", "quote_qty", "trading_toggle"
    ]
    variables = []

    def __init__(self, strategy_inst):
        self.strategy = strategy_inst
        self.GF = self.strategy.GF
        self.fmz_order_id_lst = [] # 包含所有fmz订单的id
        self.fmz_order_dict_lst = [] # 包含所有fmz订单的dict
        self.strategy_trade_id = 0 # 策略逻辑内的trade_id (成交的id)
        self.strategy_trade_profit_dict = {} # 策略逻辑内的所有订单的盈亏利润 [注意]: 需要每分钟计算profit, 并存入字典 //eg: {1:+100, 2:-50}
        self.strategy_trade_dict_lst = [] # 包含策略逻辑内的所有strategy_trade_dict
        self.strategy_trade_dict_dict = {} # 包含策略逻辑内的所有strategy_trade_dict

        # 4个持仓标识
        self.position_flag = 0
        self.stop_profit_maker_order_lst = [] # 止盈委托单的'未成交'的订单列表
        self.stop_loss_bar_order_lst = []
        self.stop_loss_tick_order_lst = []

        # 挂单的订单列表
        self.open_maker_order_lst = [] # 开仓挂单
        self.close_maker_order_lst = [] # 平仓挂单

    def update_parameters_settings(self, parameters_settings: dict):
        """
        Update strategy parameter wtih value in setting dict.
        """
        # 这个parameters_settings就是传入需要修改的'parameters'
        for name in self.parameters:
            if name in parameters_settings:
                setattr(self, name, parameters_settings[name])

    def get_strategy_order_profit(self, strategy_trade_id):
        """
            获取策略逻辑内的'完整一单'的利润
            输入: strategy_trade_id
            输出: '完整一单'的利润
        """
        this_strategy_trade_dict_lst = self.strategy_trade_dict_dict[strategy_trade_id]
        GF.Log(f"this_strategy_trade_dict_lst:{this_strategy_trade_dict_lst}")
        cash_flow = 0
        for this_strategy_trade_dict in this_strategy_trade_dict_lst:
            order_id = this_strategy_trade_dict.get("order_id")
            fmz_order_dict = self.GF.exchange.GetOrder(order_id)
            price = fmz_order_dict["AvgPrice"] # 成交均价
            amount = fmz_order_dict["Amount"] # 下单数量
            quote_qty = price * amount # 计价币数量 (即: 总金额)
            type = fmz_order_dict["Type"] # 0: 买; 1: 卖
            if type == 0:
                cash_flow -= quote_qty
            elif type == 1:
                cash_flow += quote_qty
        profit = cash_flow
        GF.Log(f"profit:{profit}")
        return profit

    def record_strategy_trade(self, order_id, offset, direction, price, base_qty, **kwargs):
        """
            [注意]: 该函数由子类重写, 不要继承父类  (不同策略, record的逻辑不同)
            待实现功能:
                - 更新'strategy_trade_id' (策略逻辑内的id)
                - 更新'position_flag' (每个策略, 修改的方式不一样..) (使用taker和maker导致的结果也不一样)
                - 记录每一个'trade_dict' (后期统计需要用到)
            进入该函数的前提:
                两个方案:
                    1. 必须要全部成交才会进入
                    2. 无条件: 只要执行了send_order就会进入??

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

            # 2. 修改'position_flag'
            if offset == "open":
                if direction == "buy":
                    self.position_flag += 1
                elif direction == "sell":
                    self.position_flag -= 1
            elif offset == "close":
                stop_type = kwargs.get("stop_type")
                if direction == "buy":
                    self.position_flag += 1
                elif direction == "sell":
                    self.position_flag -= 1

            # 3. 标记为新的一单 (策略逻辑内的自定义的'一单')
            if offset == "open":
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
                base_qty = -base_qty # 卖出的话标记为'负值'
            strategy_trade_dict = {
                "time" : self.strategy.bar.time,
                "strategy_trade_id" : self.strategy_trade_id, # 策略逻辑内的订单id
                "order_id" : order_id, # 服务器返回的订单id
                "offset" : offset,
                "direction" : direction,
                "price" : price,
                "base_qty" : base_qty,
            }
            # 计算每单利润 [待优化: 目前写得过于凌乱...]
            self.strategy_trade_dict_lst.append(strategy_trade_dict)
            if self.strategy_trade_dict_dict.get(self.strategy_trade_id):
                self.strategy_trade_dict_dict[self.strategy_trade_id].append(strategy_trade_dict)
            else:
                self.strategy_trade_dict_dict[self.strategy_trade_id] = [strategy_trade_dict]

            # if offset == "close":
            #     # 判断是止盈还是止损 (仓位管理模块中, 止损需要加倍仓位)
            #     profit = self.get_strategy_order_profit(strategy_trade_id=self.strategy_trade_id)
            #     if profit >= 0 :
            #         # 重置'每次下单金额'
            #         self.pm.update(op="reset")
            #     elif profit < 0 :
            #         # 更新'每次下单金额'
            #         self.pm.update(op="increase")
        pass

    def stop_loss(self, direction, stop_loss_type, stop_loss_base_qty, stop_loss_bar_price, stop_loss_tick_price):
        # 1. 两类止损都加
        if stop_loss_type == "both":
                # i. 收盘止损
            self.stop_loss_bar(direction=direction, price=stop_loss_bar_price, base_qty=stop_loss_bar_price, exchange=GF.exchange)
                # ii. 瞬间止损
            self.stop_loss_tick(direction=direction, price=stop_loss_tick_price, base_qty=stop_loss_bar_price, exchange=GF.exchange)
        # 2. 只'收盘止损'
        elif stop_loss_type == "bar":
            self.stop_loss_bar(direction=direction, price=stop_loss_bar_price, base_qty=stop_loss_bar_price, exchange=GF.exchange)
        # 3. 只'瞬间止损'
        elif stop_loss_type == "tick":
            self.stop_loss_tick(direction=direction, price=stop_loss_tick_price, base_qty=stop_loss_bar_price, exchange=GF.exchange)

    def stop_profit(self):
        pass

    def get_account_info(self, exchange):
        symbol, full_symbol, base_asset, quote_asset = UTILS.get_symbol(exchange)
        # self.GF.Log(f"symbol:{symbol}")
        account_dict = exchange.GetAccount()
        # self.GF.Log(f"account_dict:{account_dict}")
        exchange_name = exchange.GetName()
        # self.GF.Log(f"exchange_name:{exchange_name}")
        exchange_name_prefix = exchange_name.split("_")[0] # 交易所的前缀  （期货的话前面会带有‘Futures’）
        if exchange_name_prefix == "Futures":
            # self.GF.Log(f"进入Futures...")
            #position_dict = exchange.GetPosition()[0] if exchange.GetPosition() else {}
            #contract_type = exchange.GetContractType()
            # contractType即使是合约， 若当前没有仓位的话，还是会返回空[]
            position_dict_lst = exchange.GetPosition() if exchange.GetPosition() else []
            # self.GF.Log(f"position_dict_lst:{position_dict_lst}")
            contract_type = exchange.GetContractType()
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
            "full_symbol": full_symbol, "symbol": symbol, "quote_asset": quote_asset,
            "quote_qty": quote_qty, "quote_qty_frozen": quote_qty_frozen,  # 合约账户的现金余额
            # '标的资产'的数据 (只有'现货账户'才有, '合约账户'这个数据为空, 忽略)
            "base_qty": base_qty, "base_qty_frozen": base_qty_frozen,
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
                    "direction": position_direction, "margin": margin, "margin_level": margin_level,
                    "futures_base_qty": amount, "futures_base_qty_frozen": frozen_amount, "floating_profit": floating_profit,
                }
                position_lst.append(_d)

        account_info.update({"position_lst": position_lst})
        return account_info

    def print_account_msg(self, exchange):
        account_info = self.get_account_info(exchange=exchange)
        full_symbol = account_info["full_symbol"]
        symbol = account_info["symbol"]
        contract_type = account_info["contract_type"]
        quote_asset = account_info["quote_asset"]
        quote_qty = account_info["quote_qty"]
        quote_qty_frozen = account_info["quote_qty_frozen"]
        base_qty = account_info["base_qty"]
        base_qty_frozen = account_info["base_qty_frozen"]
        position_lst = account_info["position_lst"]
        msg = f"{full_symbol}.{contract_type}-----> "
        msg += f"[{quote_asset}现金]: 总数量:{quote_qty}; 冻结数量：{quote_qty_frozen} "
        # msg += f"[{symbol}现货余额]: 总数量:{base_qty}; 冻结数量：{base_qty_frozen} " # 合约账户不需要打印这个数据 (一直都是空的) (现货账户才需要打印)
        for position_dict in position_lst:
            direction = position_dict["direction"]
            futures_base_qty = position_dict["futures_base_qty"]
            futures_base_qty_frozen = position_dict["futures_base_qty_frozen"]
            msg += f".............[{symbol}合约{direction}仓位]: 总数量:{futures_base_qty}; 冻结数量：{futures_base_qty_frozen}"
        # 打印
        self.GF.Logger.log(msg, 30)

    def get_futures_base_qty_total(self, exchange):
        "获取合约账户, '该币种'的仓位的总数量 (多头为正, 空头为负)"
        "futures_base_qty: 指合约账户的'标的资产'的仓位数量"
        account_info = self.get_account_info(exchange=exchange)
        position_lst = account_info["position_lst"]
        futures_base_qty_total = 0
        for position_dict in position_lst:
            futures_base_qty = position_dict["futures_base_qty"]
            direction = position_dict["direction"]
            if direction == "多头":
                futures_base_qty_total += futures_base_qty
            elif direction == "空头":
                futures_base_qty_total -= futures_base_qty
        return futures_base_qty_total

    def get_account_msg(self, exchange):
        "待删.....已经弃用了"
        symbol, full_symbol, base_asset, quote_asset = UTILS.get_symbol(
            exchange)
        account_dict = exchange.GetAccount()
        exchange_name = exchange.GetName()
        exchange_name_prefix = exchange_name.split(
            "_")[0]  # 交易所的前缀  （期货的话前面会带有‘Futures’）
        if exchange_name_prefix == "Futures":
            #position_dict = exchange.GetPosition()[0] if exchange.GetPosition() else {}
            #contract_type = exchange.GetContractType()
            # contractType即使是合约， 若当前没有仓位的话，还是会返回空[]
            position_dict_lst = exchange.GetPosition() if exchange.GetPosition() else []
            contract_type = exchange.GetContractType()
        else:
            position_dict_lst = []
            contract_type = ""

        msg = f"{full_symbol}.{contract_type}-----> "
        # 1. 余额：
        balance = account_dict.get("Balance")
        frozen_balance = account_dict.get("FrozenBalance")
        # 2. 币数：(这里特指现货， 所以合约的持仓量不会显示在这里）
        stocks = account_dict.get("Stocks")
        frozen_stocks = account_dict.get("FrozenStocks")
        msg += f"[{quote_asset}现金]: 可用数量:{balance}; 冻结数量：{frozen_balance} ............."
        msg += f"[{symbol}现货余额]: 可用数量:{stocks}; 冻结数量：{frozen_stocks} "

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
                marginLevel = position_dict.get("MarginLevel", 0)
                msg += f".............[{symbol}合约{position_direction}仓位]: 可用数量:{amount}; 冻结数量：{frozen_amount} ({marginLevel}倍)"

        return msg

    def get_available_amount(self, account_type, exchange):
        """
            (不管是现货还是合约都通用)
            - 现货: 获取币的可用数量
            - 合约: 获取币的可用仓位
            notes:
                - 返回的结果是有正负值的! (正值表示多头仓位, 负值表示空头仓位)
                    (如果有些场景只需要知道仓位大小, 不需要知道方向, 直接取abs()即可)
        """
        # i. 如果是现货:
        if account_type == "spot":
            account = exchange.GetAccount()
            available_amount = account.Stocks
        # ii. 如果是合约:
        elif account_type == "futures":
            position_dict_lst = exchange.GetPosition()
            net_amount = 0  # 双向持仓的数量要相加 (得到净持仓数量)
            for position_dict in position_dict_lst:
                amount = position_dict.get("Amount", 0)
                flag = position_dict.get("Type", 0)
                if flag == 0:  # 0表示amount正值
                    pass
                elif flag == 1:  # 1表示amount负值
                    amount = amount * -1
                net_amount += amount
            available_amount = net_amount
        return available_amount

    def get_base_asset_precision(self, lc_symbol):
        "从redis中获取数量精度"
        try:
            base_asset_precision = float(UTILS.r2.hget(lc_symbol, "base_asset_precision")) # 数量精度 (eg: 0.01)
        except Exception as e:
            err_msg = f"[获取数量精度]: {e}"
            raise Exception(err_msg)
        return base_asset_precision

    def get_min_notional(self, lc_symbol):
        "从redis中获取最小名义市值"
        try:
            min_notional = float(UTILS.r2.hget(lc_symbol, "min_notional"))
        except Exception as e:
            err_msg = f"[获取最小名义市值]: {e}"
            raise Exception(err_msg)
        return min_notional

    def filter_lot_size(self, base_qty):
        """
        args:
            - base_qty: 下单的数量
        notes:
            - 发明者中的symbol都是和exchange一对一绑定的! (知道exchange就相当于知道symbol了)
        """
        lc_symbol = UTILS.get_lc_symbol(exchange=self.GF.exchange)
        base_asset_precision = self.get_base_asset_precision(lc_symbol)
        filtered_base_qty = math.floor(round(base_qty / base_asset_precision, 10)) * base_asset_precision
        filtered_base_qty = round(filtered_base_qty, 10) # 上面的计算中可能出现'python浮点精度问题', 所以这里必须再做一次round
        return filtered_base_qty

    def filter_min_notional(self, quote_qty):
        lc_symbol = UTILS.get_lc_symbol(exchange=self.GF.exchange)
        min_notional = self.get_min_notional(lc_symbol)
        if quote_qty <= min_notional:
            msg = f"[最小市值不足{min_notional}] quote_qty:{quote_qty}"
            raise Exception(msg)
        else:
            return quote_qty

    def get_base_qty(self, base_qty=0, quote_qty=0):
        """
        args:
            price:
                -1: 表示市价下单
                正数: 表示限价下单
            base_qty:
                这里传入的参数统一指代'币'的base_qty
            quote_qty:
                交易金额 (主要用USDT来计价)
        """
        # GF.Log(f"base_qty输入:{base_qty}")
        time = self.strategy.tick.time
        latest_price = self.strategy.tick.price

        # 同时计算出 base_qty和quote_qty (两者都需要经历过滤器)
        # base_qty: 只需要经历'filter_lot_size'
        # quote_qty: 只需要经历'filter_min_notional'
        # i. 若使用'交易金额'下单:
        if quote_qty:  # 如果传入'交易金额'的参数, 则按照'交易金额'计算出当前应该买入的数量
            base_qty = quote_qty / latest_price
        # ii. 若使用'数量'下单:
        elif base_qty:
            pass
        else:
            msg = f"[输入错误] base_qty:{base_qty}; quote_qty:{quote_qty}"
            raise Exception(msg)

        # 检查下单信息 (不管是用'交易金额'下单, 还是用'数量'下单, 都需要做此检查)
        # =============
        # 1. 检查下单的最小精度
        base_qty = self.filter_lot_size(base_qty=base_qty)
        # 2. 检查最小交易金额
        quote_qty = base_qty * latest_price
        quote_qty = self.filter_min_notional(quote_qty=quote_qty)
        # GF.Log(f"base_qty输出:{base_qty}")

        return base_qty

    def check_order_status(self, order_id):
        """
            获取订单的'成交状态'
        """
        fmz_order_dict = self.GF.exchange.GetOrder(order_id)
        Amount = fmz_order_dict["Amount"]
        DealAmount = fmz_order_dict["DealAmount"]
        if DealAmount == Amount:
            order_status = "all_traded"  # 全部成交
        elif DealAmount == 0:
            order_status = "not_traded"  # 无成交
        else:
            order_status = "part_traded"  # 部分成交
        return order_status

    def send_order(self, offset="open", direction="buy", price=-1, base_qty=0, exchange=None):
        """
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
        base_qty = self.get_base_qty(base_qty=base_qty, quote_qty=self.strategy.tick.price*base_qty)

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
                self.strategy.chart.draw_operation(price=price, name="平空", draw_offset=1.001) # 平仓暂时不画图, 后期待优化

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
                self.strategy.chart.draw_operation(price=price, name="平多", draw_offset=0.999) # 平仓暂时不画图, 后期待优化

        return order_id

    def print_variables(self, score=50):
        "打印全局状态变量"
        main_status_dict = {}
        for v_name in self.variables:
            v_value = self.__getattribute__(v_name)
            main_status_dict.update({v_name : v_value})
        self.GF.Logger.log(f"[trade模块-全局状态变量]: {main_status_dict}", score)

    def print_parameters(self, score=50):
        "打印可调参数"
        main_status_dict = {}
        for v_name in self.parameters:
            v_value = self.__getattribute__(v_name)
            main_status_dict.update({v_name : v_value})
        self.GF.Logger.log(f"[trade模块-可调参数]: {main_status_dict}", score)

    def cancel_order(self, order_id, exchange=None):
        "当策略开始新的一单时, 启动该方法"
        order_id = exchange.CancelOrder(order_id)
        return order_id

    def cancel_stop_profit_orders(self, exchange=None):
        """
        撤销所有止盈单

        tips:
            - 撤销止盈单之前, 需要前check一下'止盈单是否已经成交'

        return:
            True # 撤销成功
            False # 撤销失败 (止盈单在撤销之前已经成交)

        """
        self.check_stop_profit_maker(exchange=exchange)
        stop_profit_maker_order_lst = self.stop_profit_maker_order_lst.copy()
        if not stop_profit_maker_order_lst:
            return False
        else:
            for stop_profit_maker_order_info in stop_profit_maker_order_lst:
                order_id = stop_profit_maker_order_info.get("order_id")
                self.cancel_order(order_id=order_id, exchange=exchange)
            self.stop_profit_maker_order_lst = []
            return True

    def cancel_stop_loss_orders(self, exchange=None):
        "撤销所有止损单"
        self.stop_loss_bar_order_lst = []
        self.stop_loss_tick_order_lst = []

    def stop_profit_maker(self, direction, price, base_qty, exchange=None, **kwargs):
        "挂单止盈"
        order_id = self.send_order(offset="close", direction=direction, price=price, base_qty=base_qty, exchange=exchange)
        if order_id:
            stop_profit_maker_order_info = {
                "order_id":order_id, "offset":"close", "direction":direction, "price":price, "base_qty":base_qty,
                # "maker_price_index":kwargs['maker_price_index']
            }
        else:
            msg = f"[下单失败] order_id:{order_id}"
            raise Exception(msg)
        self.stop_profit_maker_order_lst.append(stop_profit_maker_order_info)

    def stop_loss_bar(self, direction, price, base_qty, exchange=None):
        "计划单-市价-收盘止损"
        GF.Logger.log(f"收盘止损价格:{price}", 40)
        stop_loss_bar_price = price
        stop_loss_bar_order_info = {"direction":direction, "price":stop_loss_bar_price, "base_qty":base_qty}
        self.stop_loss_bar_order_lst.append(stop_loss_bar_order_info)

    def stop_loss_tick(self, direction, price, base_qty, exchange=None):
        "计划单-市价-瞬间止损"
        GF.Logger.log(f"瞬间止损价格:{price}", 40)
        stop_loss_tick_price = price
        stop_loss_tick_order_info = {"direction":direction, "price":stop_loss_tick_price, "base_qty":base_qty}
        self.stop_loss_tick_order_lst.append(stop_loss_tick_order_info)

    def check_stop_profit_maker(self, exchange=None):
        """
            检查'止盈单'是否已经成交
                若'止盈单已经成交': 则把'stop_profit_maker_order_info'pop出来
                若'止盈单未完全成交': 则把pop出来的'stop_profit_maker_order_info'重新添加回去
        """
        # 打印排错
        GF.Logger.log(f"未成交的止盈单:{self.stop_profit_maker_order_lst}", 50)

        # 将'已成交'的止盈单从 'stop_profit_maker_order_lst'中pop出来
        stop_profit_maker_order_num = len(self.stop_profit_maker_order_lst) # 当下'未check'的止盈单的数量
        _stop_profit_times = 0 # '本回合'止盈次数
        for _ in range(stop_profit_maker_order_num):
            stop_profit_maker_order_info = self.stop_profit_maker_order_lst.pop(0)
            # GF.Logger.log(f"未成交的止盈单:stop_profit_maker_order_info:{stop_profit_maker_order_info}", 50)
            order_id = stop_profit_maker_order_info.get("order_id")
            offset = stop_profit_maker_order_info.get("offset")
            direction = stop_profit_maker_order_info.get("direction")
            price = stop_profit_maker_order_info.get("price")
            base_qty = stop_profit_maker_order_info.get("base_qty")
            fmz_order_dict = exchange.GetOrder(order_id)
            Amount = fmz_order_dict["Amount"]
            DealAmount = fmz_order_dict["DealAmount"]
            GF.Logger.log(f"fmz_order_dict:{fmz_order_dict}", 40)
            # 如果该'止盈单'已经完全成交 (修改'仓位标识')
            if DealAmount == Amount:
                _stop_profit_times += 1 # 止盈次数增加1
                # 若'未check的止盈单数量' 和 '本回合止盈次数'相同, 则表明: 所有止盈单都已经成交!
                if stop_profit_maker_order_num == _stop_profit_times:
                    # 策略逻辑内的'一个订单'已经完结, 重置各种持仓指标
                    self.reset_position_flag()
                    # 重置'每次下单金额'
                    self.pm.update(op="reset")
                self.record_strategy_trade(order_id=order_id, offset=offset, direction=direction, price=price, base_qty=base_qty, stop_type="stop_profit")

            # 如果该'止盈单'没有完全成交 (重新append回去)
            elif DealAmount != Amount:
                self.stop_profit_maker_order_lst.append(stop_profit_maker_order_info)

    def check_stop_loss_bar(self, exchange=None):
        """
            检查是否满足'收盘止损单'止损条件
                若满足条件: 则以'市价'立马止损
        """
        # 打印排错
        GF.Logger.log(f"未成交的收盘止损单:{self.stop_loss_bar_order_lst}", 50)

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
                    order_id = self.send_order(offset="close", direction=direction, price=-1, base_qty=futures_base_qty_total, exchange=exchange)
                    self.record_strategy_trade(order_id=order_id, offset="close", direction=direction, price=-1, base_qty=futures_base_qty_total, stop_type="stop_loss")
                    self.reset_position_flag()
                    self.pm.update(op="increase") # 更新'每次下单金额'
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
                    order_id = self.send_order(offset="close", direction=direction, price=-1, base_qty=futures_base_qty_total, exchange=exchange)
                    self.record_strategy_trade(order_id=order_id, offset="close", direction=direction, price=-1, base_qty=futures_base_qty_total, stop_type="stop_loss")
                    self.reset_position_flag()
                    self.pm.update(op="increase") # 更新'每次下单金额'
                    # 禁止开仓 (默认10次)
                    self.strategy.trading_toggle.close()

    def check_stop_loss_tick(self, exchange=None):
        """
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
                    order_id = self.send_order(offset="close", direction=direction, price=-1, base_qty=futures_base_qty_total, exchange=exchange)
                    self.record_strategy_trade(order_id=order_id, offset="close", direction=direction, price=-1, base_qty=futures_base_qty_total, stop_type="stop_loss")
                    self.reset_position_flag()
                    self.pm.update(op="increase") # 更新'每次下单金额'
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
                    order_id = self.send_order(offset="close", direction=direction, price=-1, base_qty=futures_base_qty_total, exchange=exchange)
                    self.record_strategy_trade(order_id=order_id, offset="close", direction=direction, price=-1, base_qty=futures_base_qty_total, stop_type="stop_loss")
                    self.reset_position_flag()
                    self.pm.update(op="increase") # 更新'每次下单金额'
                    # 禁止开仓 (默认10次)
                    self.strategy.trading_toggle.close()



# 通用类-统计分析模块
class BaseAnalysis():
    author = "kerwin"
    parameters = [
        "maker_fee_rate", "taker_fee_rate"
    ]
    variables = []

    def __init__(self, strategy_inst):
        self.strategy = strategy_inst
        self.GF = self.strategy.GF
        self.period_info_lst = []  # 收集所有日常资产数据

    def update_parameters_settings(self, parameters_settings: dict):
        """
        Update strategy parameter wtih value in setting dict.
        """
        # 这个parameters_settings就是传入需要修改的'parameters'
        for name in self.parameters:
            if name in parameters_settings:
                setattr(self, name, parameters_settings[name])

    def get_total_capital_value(self, exchange=None):
        "获取总资产价值 (用usdt计算)"
        account_info = self.strategy.trade.get_account_info(exchange=exchange)
        self.GF.Logger.log(f"account_info:{account_info}", 30)
        # 现货usdt余额 (一般这里的'quote_qty'是指usdt的余额数量)
        usdt_qty = account_info.get("quote_qty")
        position_lst = account_info.get("position_lst")

        # fmz的margin比较坑, 不是'保证金余额', 而是'单个仓位的所需保证金'.....
        total_margin = 0  # 总保证金数
        for position_dict in position_lst:
            # 不管多头还是空头, 都算作总资产的一部分
            margin = abs(position_dict["margin"])
            floating_profit = position_dict["floating_profit"]
            total_margin += margin
            total_margin += floating_profit  # 要把浮盈浮亏算上!!
        total_capital_value = usdt_qty + total_margin  # 总资产价值

        return total_capital_value

    def get_delta_capital_value(self, exchange=None):
        total_capital_value = self.get_total_capital_value(exchange=exchange)
        self.delta_capital_value = total_capital_value - \
            self.total_capital_value  # 今日总资产增量
        self.delta_capital_value_rate = self.delta_capital_value / \
            self.total_capital_value  # 今日总资产增长幅度
        self.total_capital_value = total_capital_value

        daily_info = {
            "total_capital_value": total_capital_value,
            "delta_capital_value": self.delta_capital_value, "delta_capital_value_rate": self.delta_capital_value_rate,
        }
        self.record_period_info(daily_info)

    def record_period_info(self, daily_info):
        "记录每个周期的盈亏数据"
        # self.GF.Logger.log(f"self.strategy.bar:{self.strategy.bar}", 50)
        time = self.strategy.bar.time
        daily_info.update({"time": time})
        self.period_info_lst.append(daily_info)

    def _get_period_df(self):
        "获取每个周期记录的资产涨跌表"
        period_info_lst = self.period_info_lst
        df = pd.DataFrame(period_info_lst)
        df["time"] = UTILS.utc0_to_utc8(df["time"])
        return df

    def _get_daily_df(self, period_df):
        "根据period_df, 汇总成'每日资产涨跌表'"
        daily_df = period_df
        # daily_df["time"] = pd.to_datetime(daily_df["time"])
        # daily_df["date"] = daily_df["time"].str.extract(r"([\s\S]{10})") # eg: 2021-03-14
        daily_df["date"] = daily_df["time"].dt.strftime("%Y-%m-%d")

        # 获得每日总资产&资产变化值
        daily_df = daily_df.pivot_table(index="date", aggfunc={"delta_capital_value":"sum", "total_capital_value":"last"})
        daily_df = daily_df.reset_index()
        return daily_df

    def get_fmz_order_dict_lst(self):
        """
        循环遍历每个fmz_order_id, 获得交易所的真实数据
        """
        fmz_order_dict_lst = []
        fmz_order_id_lst = self.strategy.trade.fmz_order_id_lst
        self.GF.Logger.log(f"fmz_order_id_lst:{fmz_order_id_lst}", 10)
        for fmz_order_id in fmz_order_id_lst:
            fmz_order_dict = self.GF.exchange.GetOrder(fmz_order_id)
            fmz_order_dict_lst.append(fmz_order_dict)
        self.strategy.trade.fmz_order_dict_lst = fmz_order_dict_lst
        self.GF.Logger.log(f"fmz_order_dict_lst:{fmz_order_dict_lst}", 10)
        return fmz_order_dict_lst

    def get_fmz_order_df(self):
        "获得fmz所有订单的df(包含未成交/部分成交的撤单订单)"  # 貌似只有'已成交的'...?
        fmz_order_dict_lst = self.get_fmz_order_dict_lst()
        df = pd.DataFrame(fmz_order_dict_lst)
        self.strategy.trade.fmz_order_df = df
        self.fmz_order_df = df
        return df

    def get_strategy_trade_df(self):
        "获得策略逻辑内的所有'已经成交的'订单的df"

        def _get_profit_flag(strategy_trade_dict_lst):
            "遍历所有开平仓记录, 对所有平仓数据打标:'止盈'/'止损'"
            new_strategy_trade_dict_lst = []
            for strategy_trade_dict in strategy_trade_dict_lst:
                offset = strategy_trade_dict.get("offset")
                direction = strategy_trade_dict.get("direction")
                price = strategy_trade_dict.get("price")
                if offset == "open":
                    open_direction = direction
                    open_price = price
                    profit_flag = 0
                elif offset == "close":
                    close_direction = direction
                    close_price = price
                    if open_direction == "buy":
                        if close_price > open_price:
                            profit_flag = 1 # 止盈单
                        elif close_price < open_price:
                            profit_flag = -1 # 止损单
                        elif close_price == open_price:
                            profit_flag = 0 # 没盈亏
                    elif open_direction == "sell":
                        if close_price < open_price:
                            profit_flag = 1 # 止盈单
                        elif close_price > open_price:
                            profit_flag = -1 # 止损单
                        elif close_price == open_price:
                            profit_flag = 0 # 没盈亏
                strategy_trade_dict.update({"profit_flag":profit_flag})
                new_strategy_trade_dict_lst.append(strategy_trade_dict)
            return new_strategy_trade_dict_lst

        strategy_trade_dict_lst = self.strategy.trade.strategy_trade_dict_lst
        strategy_trade_dict_lst = _get_profit_flag(strategy_trade_dict_lst)
        if strategy_trade_dict_lst:
            df = pd.DataFrame(strategy_trade_dict_lst)
            df["time"] = UTILS.utc0_to_utc8(df["time"])
        else:
            err_msg = f"[策略逻辑内没有订单, 不需要经历统计模块] strategy_trade_dict_lst:{strategy_trade_dict_lst}"
            raise Exception(err_msg)
        self.strategy.trade.strategy_trade_df = df
        self.strategy_trade_df = df
        return df

    def _get_final_trade_df(self):
        "联结'已成交df'和所有'fmz订单df'" # 其实感觉用处不是很大, 直接strategy_trade_df就差不多够用了(待删...)
        strategy_trade_df = self.get_strategy_trade_df()
        fmz_order_df = self.get_fmz_order_df()
        fmz_order_df = fmz_order_df.rename(columns={"Id": "order_id"})
        # 合并
        trade_df = pd.merge(strategy_trade_df, fmz_order_df, on="order_id", how="left")
        # trade_df = strategy_trade_df # 临时测试....


        # usdt总金额
        trade_df["quote_qty"] = trade_df["base_qty"] * trade_df["price"]
        # 现金流 (便于下面计算每笔盈亏)
        trade_df["现金流"] = -trade_df["quote_qty"]

        # Taker
        query_df = trade_df.query("Price==0")
        trade_df.loc[query_df.index, "手续费率"] = self.taker_fee_rate
        # Maker
        query_df = trade_df.query("Price!=0")
        trade_df.loc[query_df.index, "手续费率"] = self.maker_fee_rate
        trade_df["手续费用"] = -1 * abs(trade_df["quote_qty"]) * trade_df["手续费率"]

        self.strategy.trade.final_trade_df = trade_df
        self.final_trade_df = trade_df
        return trade_df

    def _remove_unfinished_order(self, df):
        # 如果最后一笔订单是'未完成订单', 则统计分析时, 把这笔交易删除
        last_strategy_trade_id = df["strategy_trade_id"].iloc[-1]
        last_df = df.query(f"strategy_trade_id=={last_strategy_trade_id}")
        open_qty = last_df.query("offset=='open'")["base_qty"].sum()
        close_qty = last_df.query("offset=='close'")["base_qty"].sum()
        close_percentage = abs(close_qty / open_qty) # 平仓占比
        GF.Log(f"close_percentage:{close_percentage}", "#ff0000")
        if close_percentage > 0.98:
            return df
        elif close_percentage <= 0.98:
            df = df.drop(last_df.index, axis=0)
            return df

    def _get_profit_df(self, final_trade_df):
        "获得最终的逐笔成交的'利润表'"
        df = self._remove_unfinished_order(df=final_trade_df)

        # 获得每笔交易的profit
        profit_df = df.pivot_table(
            index="strategy_trade_id",
            aggfunc={"strategy_trade_id":"first", "time":"first", "profit_flag":"sum", "现金流":"sum", "手续费用":"sum"}
        )
        profit_df["profit"] = profit_df["现金流"] + profit_df["手续费用"]
        profit_df["盈亏"] = 0
        query_df = profit_df.query("profit >= 0")
        profit_df.loc[query_df.index, "盈亏"] = 1

        self.strategy.trade.profit_df = profit_df
        self.profit_df = profit_df
        return profit_df

    def _cal_win_rate(self):
        "计算胜率"
        profit_df = self.profit_df
        # 胜率
        win_count = profit_df["盈亏"].sum()  # 胜的单数
        total_count = profit_df["盈亏"].count()
        fail_count = total_count - win_count  # 负的单数
        win_rate = win_count / total_count
        self.strategy.GF.Log(f"胜的单数:{win_count}; 败的单数:{fail_count};", "#0000ff")
        self.strategy.GF.Log(f"[统计胜率]: {win_rate:.3%} ", "#ff0000")

    def _cal_win_fail_ratio(self):
        "计算盈亏比"
        profit_df = self.profit_df
        win_count = profit_df["盈亏"].sum() # 胜的单数
        total_count = profit_df["盈亏"].count()
        fail_count = total_count - win_count  # 负的单数
        # 盈亏比
        # 公式: abs(所有收益总和 / 所有亏损总和) * (负的单数 / 胜的单数)
        win_total_profit = profit_df.query("盈亏==1")["profit"].sum()  # 所有收益总和
        fail_total_profit = profit_df.query("盈亏==0")["profit"].sum()  # 所有亏损总和
        # win_fail_ratio = abs(win_total_profit / fail_total_profit) * (fail_count / win_count)
        self.strategy.GF.Log(
            f"胜单总收益:{win_total_profit:.3f}; 胜单次数:{win_count}; 败单总亏损:{fail_total_profit:.3f}; 败单次数:{fail_count}", "#0000ff")
        avg_win_profit = win_total_profit / win_count
        avg_fail_profit = fail_total_profit / fail_count
        self.strategy.GF.Log(
            f"平均每个胜单收入:{avg_win_profit:.3f}; 平均每个败单亏损:{avg_fail_profit:.3f};", "#0000ff")
        win_fail_ratio = avg_win_profit / abs(avg_fail_profit)  # 盈亏比
        self.strategy.GF.Log(f"[统计盈亏比]: {win_fail_ratio:.3%} ", "#ff0000")

    def get_expectation_df(self, profit_df):
        "计算策略的期望值"

        df = profit_df.set_index("profit_flag")
        # 把所有profit_flag进行分类 (-1和-2都属于'全亏')
        df = df.rename(index={1:"全赢", 2:"全赢", -1:"全亏", -2:"全亏", 0:"一盈一亏"})
        df = df.pivot_table(
            index="profit_flag",
            aggfunc={"strategy_trade_id":"count", "profit":"sum"}
        )
        df = df.reset_index()
        df = df.rename(columns={"profit_flag":"事件", "profit":"利润", "strategy_trade_id":"次数"})

        df["利润率"] = df["利润"] / self.strategy.trade.pm.quote_qty
        df["平均利润率"] = df["利润率"] / df["次数"]


        df["发生概率"] = df["次数"] / df["次数"].sum()
        df["期望值"] = df["发生概率"] * df["平均利润率"]

        df = UTILS.sort_df(df, ["事件", "次数", "发生概率", "利润", "利润率", "平均利润率", "期望值"])

        return df

    def statistics(self):
        "统计盈亏数据"

        def _get_prefix():
            doc = self.doc
            start_date_time = re.findall("start: (.*?)\n", doc)[-1] # '2021-05-03 03:00:00'
            end_date_time = re.findall("end: (.*?)\n", doc)[-1]
            start_date = "".join(start_date_time.split(" ")[0].split("-")) # '20210503'
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

        # 得到 final_trade_df
        final_trade_df = self._get_final_trade_df()
        final_trade_df.to_csv(f"{prefix}_所有交易记录表.csv", index=False, encoding="gb18030")

        # 得到 profit_df
        profit_df = self._get_profit_df(final_trade_df=self.final_trade_df)
        profit_df.to_csv(f"{prefix}_逐笔交易利润表.csv", index=False, encoding="gb18030")

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



# 通用类-仓位管理模块
class BasePositionManager():
    author = "kerwin"
    parameters = [
        "multiplier", "max_increase_times",
        "base_qty", "quote_qty",
    ]
    variables = []

    def __init__(self, strategy_inst):
        self.strategy = strategy_inst
        self.GF = self.strategy.GF
        self.increase_times = 0
        self.quote_qty = 0

    def update_parameters_settings(self, parameters_settings: dict):
        """
        Update strategy parameter wtih value in setting dict.
        """
        # 这个parameters_settings就是传入需要修改的'parameters'
        for name in self.parameters:
            if name in parameters_settings:
                setattr(self, name, parameters_settings[name])

    def update(self, op="increase"):
        """
            更新'每次下单金额' (更改下单仓位):
                止盈: '每次下单金额'恢复到初始值
                止损: '每次下单金额'开始翻倍增加 (马丁加仓)
        """

        # self.GF.Logger.log(f"op:{op}", 70)
        if op == "increase":
            # 代表策略'止损'了
            self.increase()
            self.GF.Logger.log(f"[止损] (连续次数:{self.increase_times})", 100)
        elif op == "reset":
            # 代表策略'止盈'了
            self.reset()
            self.GF.Logger.log(f"[止盈]", 100)
        self.GF.Logger.log(f"[更新'每次下单金额'] self.strategy.quote_qty:{self.strategy.trade.pm.quote_qty}", 100)

    def reset(self):
        "将每次下单金额恢复成'初始下单金额'"
        org_quote_qty = self.strategy.cta_engine.engine_config.get("parameters_settings", {}).get("quote_qty")
        self.strategy.trade.pm.quote_qty = org_quote_qty
        self.increase_times = 0

    def increase(self):
        "增加仓位(增加每次下单金额)"
        if self.increase_times <= self.max_increase_times:
            self.strategy.trade.pm.quote_qty *= self.multiplier # 仓位根据乘数翻倍
            self.increase_times += 1





#
