#!/usr/bin/python3

import selectors
import time

'''Classe Poller: um agendador de eventos que monitora objetos
do tipo arquivo e executa callbacks quando tiverem dados para 
serem lidos. Callbacks devem ser registrados para que 
seus fileobj sejam monitorados. Callbacks que não possuem
fileobj são tratados como timers'''


class Poller:
    def __init__(self):
        self.cbs_to = []
        self.cbs = set()

    def adiciona(self, cb):
        'Registra um callback'
        if cb.isTimer and not cb in self.cbs_to:
            self.cbs_to.append(cb)
        else:
            self.cbs.add(cb)

    def _compareTimeout(self, cb, cb_to):
        if not cb.timeout_enabled: return cb_to
        if not cb_to:
            cb_to = cb
        elif cb_to.timeout > cb.timeout:
            cb_to = cb
        return cb_to

    def _timeout(self):
        cb_to = None
        for cb in self.cbs_to: cb_to = self._compareTimeout(cb, cb_to)
        for cb in self.cbs:
            cb_to = self._compareTimeout(cb, cb_to)
        return cb_to

    def despache(self):
        '''Espera por eventos indefinidamente, tratando-os com seus
    callbacks. Termina se nenhum evento pude ser gerado pelos callbacks.
    Isso pode ocorrer se todos os callbacks estiverem desativados (monitoramento
    do descritor e timeout)'''
        while self.despache_simples():
            pass

    def _get_events(self, timeout):
        sched = selectors.DefaultSelector()
        active = False
        for cb in self.cbs:
            if cb.isEnabled:
                sched.register(cb.fd, selectors.EVENT_READ, cb)
                active = True
        if not active and timeout == None:
            return None
        eventos = sched.select(timeout)
        return eventos

    def despache_simples(self):
        '''Espera por um único evento, tratando-o com seu callback. Retorna True se
       tratou um evento, e False se nenhum evento foi gerado porque os callbacks
       estão desativados.'''
        t1 = time.time()
        cb_to = self._timeout()
        if cb_to != None:
            tout = cb_to.timeout
        else:
            tout = None
        eventos = self._get_events(tout)
        if eventos == None:  # fim: nada a fazer !!
            return False
        fired = set()
        if not eventos:  # timeout !
            if cb_to != None:
                fired.add(cb_to)
                cb_to.handle_timeout()
                cb_to.reload_timeout()
        else:
            for key, mask in eventos:
                cb = key.data  # este é o callback !
                fired.add(cb)
                cb.handle()
                cb.reload_timeout()
        dt = time.time() - t1
        for cb in self.cbs_to:
            if not cb in fired: cb.update(dt)
        for cb in self.cbs:
            if not cb in fired: cb.update(dt)
        return True