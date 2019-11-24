"""Classe Callback:

      Define uma classe base para os callbacks
      a serem usados pelo Poller. Cada objeto Callback
      contém um fileobj e um valor para timeout.
      Se fileobj for None, então o callback define
      somente um timer.
      Esta classe DEVE ser especializada para que
      possa executar as ações desejadas para o tratamento
      do evento detectado pelo Poller."""


class Callback:

    def __init__(self, fileobj=None, timeout=0):
        if timeout < 0: raise ValueError('timeout negativo')
        self.fd = fileobj
        self._timeout = timeout
        self.base_timeout = timeout
        self._enabled = True
        self._enabled_to = True
        self._reloaded = False

    def handle(self):
        '''Trata o evento associado a este callback. Tipicamente
        deve-se ler o fileobj e processar os dados lidos. Classes
        derivadas devem sobrescrever este método.'''
        pass

    def handle_timeout(self):
        '''Trata um timeout associado a este callback. Classes
        derivadas devem sobrescrever este método.'''
        pass

    def update(self, dt):
        'Atualiza o tempo restante de timeout'
        if not self._reloaded:
            self._timeout = max(0, self._timeout - dt)
        else:
            self._reloaded = False

    def reload_timeout(self):
        'Recarrega o valor de timeout'
        self._timeout = self.base_timeout
        self._reloaded = True

    def disable_timeout(self):
        'Desativa o timeout'
        self._enabled_to = False

    def enable_timeout(self):
        'Reativa o timeout'
        self._enabled_to = True

    def enable(self):
        'Reativa o monitoramento do descritor neste callback'
        self._enabled = True

    def disable(self):
        'Desativa o monitoramento do descritor neste callback'
        self._enabled = False

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, tout):
        self._timeout = tout
        self._reloaded = True

    @property
    def timeout_enabled(self):
        return self._enabled_to

    @property
    def isTimer(self):
        'true se este callback for um timer'
        return self.fd == None

    @property
    def isEnabled(self):
        'true se monitoramento do descritor estiver ativado neste callback'
        return self._enabled
