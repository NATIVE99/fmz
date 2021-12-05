import queue
import fmz

class GlobalValue(dict):
    pass

# fmz global vars
GF = GlobalValue()

# fmz function parmas
GP = GlobalValue()

# fmz debug parmas
GT = GlobalValue()


# 数据结构类-tick
class FmzTickData(dict):
    def __init__(self):
        # tick的源数据
        self.time = None
        self.price = None
        # 处理后的数据
        self.indicators = {}
        self.signals = []

# 数据结构类-bar
class FmzBarData(dict):
    def __init__(self):
        # bar的源数据
        self.time = None
        self.open_price = None
        self.high_price = None
        self.low_price = None
        self.close_price = None
        self.volume = None # 成交量
        # 处理后的数据
        self.indicators = {}
        self.signals = []

# 数据结构类-bars 队列
class FmzBarsQueue(queue.Queue):

    def append_bar(self, bar):
        """
        当队列达到最大长度后, 每次put前会pop一个最旧的数据,
        以确保随时可以向队列中put最新的数据
        """
        if self.qsize() == self.maxsize:
            x = self.get()
        self.put(bar)

    def extend_bars(self, bars):
        for bar in bars:
            self.append_bar(bar)

    def get_bars(self):
        bars_lst = fmz.MyList(self.queue)
        return bars_lst

class TradingToggle():
    """
    开仓权限的开关:
        - toggle为True时, 才允许开仓
        - 每完结一个bar, 就应该执行一次update
    """

    def __init__(self, close_times=10):
        self.toggle = True
        self.close_times = close_times
        self.remaining_times = 0

    def close(self, close_times=None):
        """
        function: 关闭开仓权限
        args:
            close_times: 传入关闭的次数 (如果没有传参, 则默认使用初始化时候的参数)
        """
        self.toggle = False
        if self.remaining_times == 0:
            if close_times:
                self.remaining_times = close_times
            else:
                self.remaining_times = self.close_times
        # 如果原先的次数没有用完, 则不会更新remaining_times
        elif self.remaining_times > 0:
            pass

        if self.remaining_times == 0:
            self.open()

    # def close_long(self, close_time=None):
    #     """
    #         关闭做多权限
    #         传递关闭的次数，其实也是关闭的周期
    #     """
    #     pass


    def update(self):
        if self.remaining_times > 1:
            self.remaining_times -= 1
        elif self.remaining_times == 1:
            self.remaining_times -= 1
            self.toggle = True
        elif self.remaining_times == 0:
            self.open()
        print(self.remaining_times, self.toggle)


    def open(self):
        "打开开仓权限"
        self.remaining_times = 0
        self.toggle = True

class CountdownTimer():
    """倒计时器
    使用场景: 常在过滤器中用于flag状态的延时
    """

    def __init__(self):
        self.remaining_times = 0

    def turn_on(self, times=1):
        """
        function: 开启倒计时
        args:
            times: 倒计时的次数
        """
        if times > 0:
            if self.remaining_times == 0:
                self.remaining_times = times
            # 如果原先的次数没有用完, 则不会更新remaining_times
            elif self.remaining_times > 0:
                pass
        elif times == 0: # 传入次数为0: 则关闭倒计时
            self.turn_off()

    def turn_off(self):
        """
        function: 关闭倒计时
        """
        self.remaining_times = 0

    def update(self):
        if self.remaining_times >= 1:
            self.remaining_times -= 1
        elif self.remaining_times == 0:
            self.turn_off()
        # print(self.remaining_times)

    @property
    def is_running(self):
        if self.remaining_times == 0:
            return False
        elif self.remaining_times != 0:
            return True










#
