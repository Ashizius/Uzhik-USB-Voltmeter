

import tkinter as tk

from appInterface.appWindows.Plotter import Plotter
from appInterface.appWindows.Window import Window

class MonitorWindow(Window):
    def __init__(self, root: tk.Toplevel, *, placer: tk.Toplevel = None):
        Window.__init__(self, root, title='Монитор данных', placer=placer)
        self.startButton = tk.Button(
            self._placer, text="Начать измерения", state=tk.ACTIVE, command=self._startMeasuring)
        self._onMeasuringCallback: function = lambda: print(
            'measuring is unassigned')
        self.plotter = Plotter(self._window)
        self.isStop = True

    def _startMeasuring(self):
        self._onMeasuringCallback()

    def setMeasuringCallback(self, callback):
        self._onMeasuringCallback = callback
