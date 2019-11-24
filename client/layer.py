from callback import Callback


class Layer(Callback):

    def __init__(self, lower=None, upper=None):
        self._lower = lower
        self._upper = upper

    def notify(self, data, *info):
        pass

    def send(self, data, *info):
        pass
