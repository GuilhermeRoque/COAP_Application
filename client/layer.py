from client.callback import Callback


class Layer(Callback):

    def __init__(self, lower=None, upper=None, timeout=None):
        self._lower = lower
        self._upper = upper
        self.timeout = timeout

    def notify(self):
        pass

    def send(self):
        pass
