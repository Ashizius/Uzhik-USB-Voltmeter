import tkinter as tk
from tkinter import ttk

class Tab ():
    def __init__(self, tabControl: ttk.Notebook, title: str):
        self.tab = ttk.Frame(tabControl, relief=tk.RAISED)
        tabControl.add(self.tab, text=title)
    def destroy(self):
        self.tab.destroy()
