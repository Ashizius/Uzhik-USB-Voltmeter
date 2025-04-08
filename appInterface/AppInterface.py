from math import floor
from typing import Literal
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from appInterface.appWindows.MonitorWindow import MonitorWindow
from appInterface.appWindows.SetupWindow import SetupWindow

from time import perf_counter

class AppInterface:
    def __init__(self, name='rootName'):
        self._time_last_update = perf_counter()
        self._time_last_show = perf_counter()
        self.root = root = tk.Tk()
        root.resizable(height=None, width=None)
        self._mainFrame = mainFrame = tk.LabelFrame(
            root, padx=50, pady=5, relief=tk.SUNKEN, borderwidth=3)
        root.title(name)
        self.setupWindow = SetupWindow(root, placer=mainFrame)
        self.monitorWindow = MonitorWindow(root, placer=mainFrame)
        self._warningLabel = warningLabel = tk.Label(
            root, fg="white", bg='black', width=50)
        self.perfomanceLabel = perfomanceLabel = tk.Label(
            root, width=10, anchor='w')
        self._intervalEntry = intervalEntry = tk.Entry(root, width=10)

        self._warnings: list[tuple[str, str, int]] = list()
        self._recurringCallback = lambda restart: print(
            'called by root', restart)
        self._callerIdentifier = None
        self.monitorWindow.setMeasuringCallback(self.startCalling)
        self.updateTimer = 100
        intervalEntry.delete(0, tk.END)
        intervalEntry.insert(0, str(self.updateTimer))

        self._time_current_update = perf_counter()
        self._time_max_update = 0.0
        self.showPerfomance()
        self.__clearWarningCallerId = None

        self._isPlotterEnabled = False

        intervalEntry.bind("<FocusOut>", self._intervalChange)
        intervalEntry.bind("<Return>", lambda e: root.focus_set())

        self.monitorWindow.set_on_resize(self._onResize)
        self.monitorWindow.init_resize(2000)

        self._onDestroy = lambda: print('quit')

        root.protocol("WM_DELETE_WINDOW", self._onClosing)

        warningLabel.grid(column=0, row=0, sticky='ew')
        perfomanceLabel.grid(column=1, row=0, sticky='w')
        tk.Label(root, text='интервал', anchor='w').grid(
            column=1, row=1, sticky='nw')
        intervalEntry.grid(column=1, row=2, sticky='nw')
        mainFrame.grid(column=0, row=1, rowspan=2, sticky='ew')

        self.monitorWindow.startButton.grid(
            column=1, row=1, columnspan=2, rowspan=2, sticky='ns')
        self.setupWindow.showButton.grid(column=0, row=1, sticky='ew')
        self.monitorWindow.showButton.grid(column=0, row=2, sticky='ew')
        self.monitorWindow.startButton.config(width=20)

    def toggleMeasurements(self, switch=None):
        if switch == None:
            self.monitorWindow.startButton.config(text='................')
            self.monitorWindow.startButton.config(state=tk.DISABLED)
        if switch:
            self.setupWindow.portsApplyButton.config(state=tk.DISABLED)
            self.setupWindow.portsRefreshButton.config(state=tk.DISABLED)
            self.monitorWindow.startButton.config(text='остановить измерения')
            self.monitorWindow.startButton.config(state=tk.ACTIVE)
        else:
            self.setupWindow.portsApplyButton.config(state=tk.NORMAL)
            self.setupWindow.portsRefreshButton.config(state=tk.NORMAL)
            self.monitorWindow.startButton.config(text='начать измерения')
            self.monitorWindow.startButton.config(state=tk.NORMAL)

    def _setWarningLabel(self, text, level: Literal['info'] | Literal['warning'] | Literal['error'] | Literal['clear'] | Literal['flood'] = 'info'):
        if level == 'info':
            self._warningLabel.config(text=text, fg="white")
        elif level == 'warning':
            self._warningLabel.config(text=text, fg="yellow")
        elif level == 'error':
            self._warningLabel.config(text=text, fg="red")
        elif level == 'clear':
            self._warningLabel.config(text=text, fg="black")
        elif level == 'flood':
            self._warningLabel.config(text=text, fg="pink")

    def _deleteWarning(self):
        if len(self._warnings) > 0:
            self._warnings.pop(0)
        if len(self._warnings) > 0:
            self._showWarning()
        else:
            self._setWarningLabel('', 'clear')
            self.__clearWarningCallerId = None

    def _showWarning(self):
        if len(self._warnings) == 0:
            self.root.after(time, self._deleteWarning)
            return
        (text, level, time) = self._warnings[0]
        self._setWarningLabel(text, level)
        self.__clearWarningCallerId = self.root.after(
            time, self._deleteWarning)

    def addWarning(self, text: str = '', level: Literal['info'] | Literal['warning'] | Literal['error'] | Literal['clear'] | Literal['flood'] = 'info', time=2000):
        self._warnings.append((text, level, time))
        if len(self._warnings) == 1:
            self._showWarning()
    def _intervalChange(self, event):
        try:
            interval = int(round(float(self._intervalEntry.get())))
        except:
            interval = self.updateTimer
        self.updateTimer = interval

    def showPerfomance(self):
        self._time_current_update = perf_counter()
        delta = (self._time_current_update - self._time_last_update)
        delta2 = (self._time_current_update - self._time_last_show)
        self._time_max_update = max(self._time_max_update, delta)
        self._time_last_update = self._time_current_update
        if (delta2 >= 1):
            self.perfomanceLabel.config(text=str(floor(delta*1000)))
            self._time_max_update = 0.0
            self._time_last_show = perf_counter()
            self._time_last_update = perf_counter()

    def _onResize(self, size):
        if self.monitorWindow.isStop:
            return
        self.monitorWindow.startButton.config(state=tk.DISABLED)
        self.stopCalling()
        self.startCalling()

    def startCalling(self):
        if (self._callerIdentifier != None):
            self.stopCalling()
            return self
        if self.monitorWindow.isStop:
            self.toggleMeasurements()

            self._recurringCallback(restart=True)
            self.monitorWindow.isStop = False
        self._caller()
        self.toggleMeasurements(not self.monitorWindow.isStop)
        return self

    def stopCalling(self):
        self.toggleMeasurements()
        self.root.after_cancel(self._callerIdentifier)
        self.monitorWindow.plotter.destroy()
        self._recurringCallback(restart=True)
        self._recurringCallback()
        self.monitorWindow.plotter.destroy()
        self._callerIdentifier = None
        self.monitorWindow.isStop = True
        self._recurringCallback(stop=self.monitorWindow.isStop)
        self.toggleMeasurements(not self.monitorWindow.isStop)
        return self

    def _caller(self):
        self.showPerfomance()
        self._recurringCallback(stop=self.monitorWindow.isStop)
        if (not self.monitorWindow.isStop):
            self._callerIdentifier = self.root.after(
                self.updateTimer, self._caller)
        return self

    def setRecurringCallback(self, callback):
        self._recurringCallback = callback
        return self

    def start(self):
        return self.root.mainloop()

    def plotInit(self, xLim: tuple[float, float], yLim: tuple[float, float], xLabel: str, yLabel: str):
        return self.monitorWindow.plotter.initPlot(xLim, yLim, xLabel, yLabel)

    def plotGetUpdater(self, type: Literal['plot'] = 'plot'):
        if type == 'plot':
            return self.monitorWindow.plotter.getUpdater()
        else:
            return self.monitorWindow.plotter.getUpdater()

    def plotPrint(self, point: float = 0.0):
        self.monitorWindow.plotter.plot()

    def destroy(self):
        try:
            if not (self._callerIdentifier == None):
                self.stopCalling()
            if not (self.__clearWarningCallerId == None):
                self.root.after_cancel(self.__clearWarningCallerId)
            self.setupWindow.destroy()
            self.monitorWindow.destroy()
            self.root.quit()
            if not (self._onDestroy == None):
                self._onDestroy()

        except Exception as e:
            print(e)
            tk.messagebox.showerror("Quit", str(e))
            self.root.quit()

    def _onClosing(self):
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

    def setOnQuit(self, cb):
        self._onDestroy = cb
