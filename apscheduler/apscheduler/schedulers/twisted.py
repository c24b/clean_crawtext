from __future__ import absolute_import
from functools import wraps

from apscheduler.schedulers.base import BaseScheduler
from apscheduler.util import maybe_ref

try:
    from twisted.internet import reactor as default_reactor
except ImportError:  # pragma: nocover
    raise ImportError('TwistedScheduler requires Twisted installed')


def run_in_reactor(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self._reactor.callFromThread(func, self, *args, **kwargs)
    return wrapper


class TwistedScheduler(BaseScheduler):
    """A scheduler that runs on a Twisted reactor."""

    _reactor = None
    _delayedcall = None

    def _configure(self, config):
        self._reactor = maybe_ref(config.pop('reactor', default_reactor))
        super(TwistedScheduler, self)._configure(config)

    def start(self):
        super(TwistedScheduler, self).start()
        self._wakeup()

    @run_in_reactor
    def shutdown(self, wait=True):
        super(TwistedScheduler, self).shutdown(wait)
        self._stop_timer()

    def _start_timer(self, wait_seconds):
        self._stop_timer()
        if wait_seconds is not None:
            self._delayedcall = self._reactor.callLater(wait_seconds, self._wakeup)

    def _stop_timer(self):
        if self._delayedcall and self._delayedcall.active():
            self._delayedcall.cancel()
            del self._delayedcall

    @run_in_reactor
    def _wakeup(self):
        self._stop_timer()
        wait_seconds = self._process_jobs()
        self._start_timer(wait_seconds)
