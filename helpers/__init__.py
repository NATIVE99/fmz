from helpers.base import *
from helpers.object import *
from helpers.utils import *



""" todo
1. 修改 GT
2. Toggle 调整（待定）
3. 全局定时器 Toggle， TimerLocker
4. 类内的属性尽量使用 getter setter @property 的用法   e.g. Filter 的 flag
5. Python 方法形参类型
6. 模块层次感要更好
7. 注释的格式写好， 推荐使用插件生成
8. 代码空行， 函数 2 行， 类 3 行
9. 私有属性 + 私用函数
10. 计时器放在工具模块里面
11. object 是数据结构
12. 数据
"""

"""
notice:
    1. 止盈单的检查必须在止损单之前, 不管是'收盘止损'或者'瞬间止损'都需要在check时先检查'止盈单是否已经成交'
        (因为回测中我们无法及时判断'止盈单'是否已经成交, 没有回调函数来撤销对应的'止损单', 所以只能主动/及时检验'止盈单是否已经成交')

"""
