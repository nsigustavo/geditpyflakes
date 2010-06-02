from pyflakes.scripts import pyflakes
import gedit
from StringIO import StringIO
import sys
import time


class redirect_out(object):

    def __enter__(self):
        self.stdout_old = sys.stdout
        self.stderr_old = sys.stderr
        out = sys.stderr = sys.stdout = StringIO()
        return out

    def __exit__(self,*_):
        sys.stdout = self.stdout_old
        sys.stderr_old = self.stderr_old


class PyflakesPlugin(gedit.Plugin):

    def __init__(self):
        gedit.Plugin.__init__(self)
        self.window = None
        self.id_name = 'pyflakes'

    def activate(self, window):
        handler_id = window.connect("tab-added", self.on_window_tab_added)
        window.set_data(self.__class__.__name__, handler_id)
        for doc in window.get_documents():
            self.connect_document(doc)

    def connect_document(self, doc):
        """Connect to document's 'saving' signal."""
        handler_id = doc.connect("saving", self.on_document_saving)
        doc.set_data(self.__class__.__name__, handler_id)

    def deactivate(self, window):
        name = self.__class__.__name__
        handler_id = window.get_data(name)
        window.disconnect(handler_id)
        window.set_data(name, None)
        for doc in window.get_documents():
            handler_id = doc.get_data(name)
            doc.disconnect(handler_id)
            doc.set_data(name, None)

    def on_document_saving(self, doc, *args):
        lang = doc.get_language()
        if lang:
            if lang.get_name() == 'Python':
                text = doc.get_text(*doc.get_bounds())
                filename = doc.get_uri_for_display()
                with redirect_out() as out:
                    pyflakes.check(text, '    ')
                if out.getvalue():
                    notify(filename, out.getvalue())

    def on_window_tab_added(self, window, tab):
        name = self.__class__.__name__
        doc = tab.get_document()
        handler_id = doc.get_data(name)
        if handler_id is None:
            self.connect_document(doc)


def notify(title, message):
    try:
        import pynotify
        if pynotify.init("geditpyflakes"):
            n = pynotify.Notification(title, message)
            n.show()
            time.sleep(1)
            n.close()
        else:
            print "there was a problem initializing the pynotify module"
    except:
        print "you don't seem to have pynotify installed"
