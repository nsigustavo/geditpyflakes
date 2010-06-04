from  gedit import Plugin
from geditpyflakes.plugin import PyflakesPlugin

class Geditpyflakes(Plugin):
    def __init__(self):
        Plugin.__init__(self)
        self._instances = {}

    def activate(self, window):
        self._instances[window] = PyflakesPlugin(window)

    def deactivate(self, window):
        self._instances[window].deactivate()
        del self._instances[window]

    def update_ui(self, window):
        self._instances[window].update_ui()
