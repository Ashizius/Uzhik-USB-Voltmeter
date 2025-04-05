import tkinter as tk
from tkinter import ttk

from appInterface.appTabs.Tab import Tab

class TabControl():
    def __init__(self, window: tk.Toplevel):
        self._window = window
        self.tabControl = tabControl = ttk.Notebook(window)
        tabControl.pack(expand=1, fill="both")
        self._tabs: dict[str, Tab] = dict()

    def addTab(self, name: str, title: str = None, Constructor=Tab):
        if title == None:
            title = name
        tab = Constructor(self.tabControl, title)
        self._tabs.update({name: tab})
        return tab

    def deleteTab(self, name: str):
        tab = self._tabs.get(name, None)
        if tab == None:
            return
        tab.destroy()

    def getTab(self, name: str):
        tab = self._tabs.get(name, None)
        return tab
