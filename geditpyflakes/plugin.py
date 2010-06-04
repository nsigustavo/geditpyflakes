from pyflakes.scripts import pyflakes
from StringIO import StringIO
import sys
from pynotify import Notification, init


class PyflakesPlugin:
    message = None

    def __init__(self, window):
        self._window = window

    def deactivate(self):
        self._window = None
        self._plugin = None

    def update_ui(self):
        self.notify_erros()

    @property
    def doc(self):
        return self._window.get_active_document()

    def notify_erros(self):
        if self.is_python():
            filename = self.doc.get_uri_for_display()
            message = self.check()
            if message: self.notify(filename, message)

    def check(self):
        bounds = self.doc.get_bounds()
        text = self.doc.get_text(*bounds)
        with redirect_out() as out:
            pyflakes.check(text, 'line')
        return out.getvalue()

    def is_python(self):
        if self.doc is None:return False
        lang = self.doc.get_language()
        return lang and lang.get_name() == 'Python'

    def notify(self, title, message):
        if init("geditpyflakes") and self.message != message:
            self.message = message
            self.notification = Notification(title, message)
            self.notification.set_timeout(1)
            self.notification.show()


class redirect_out(object):

    def __enter__(self):
        self.stdout_old = sys.stdout
        self.stderr_old = sys.stderr
        out = sys.stderr = sys.stdout = StringIO()
        return out

    def __exit__(self,*_):
        sys.stdout = self.stdout_old
        sys.stderr_old = self.stderr_old


