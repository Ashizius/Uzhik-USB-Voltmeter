import tkinter as tk
from tkinter import ttk

from appInterface.appTabs.Tab import Tab

class ChannelLine():
    def __init__(self, frame: ttk.Frame, name: str, title: str, row=0):
        self.name = name
        self._row = row
        self.check = tk.BooleanVar()
        self.checkBox = checkBox = ttk.Checkbutton(
            frame, onvalue=True, offvalue=False, variable=self.check)
        self.label = label = ttk.Label(frame, text=title)
        self.entry = entry = ttk.Entry(frame)
        label.grid(column=1, row=row)
        checkBox.grid(column=0, row=row)
        entry.grid(column=2, row=row)

    def getSetup(self):
        try:
            multiplier = float(self.entry.get().replace(',', '.'))
        except:
            multiplier = 1.0
        return (self.name, self.check.get(), multiplier)

    def setSetup(self, multiplier: int, enabled: bool):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, str(multiplier))
        self.check.set(enabled)

class ChannelFrame ():
    def __init__(self, parent: ttk.Frame, name, title, col=0):
        self.frame = frame = ttk.Labelframe(parent, text=title)
        self.name = name
        self._channels: dict[str, ChannelLine] = dict()
        self.frame.grid(column=col, row=0, padx=2, pady=2)
        ttk.Label(frame, text='Включён').grid(column=0, row=0)
        ttk.Label(frame, text='Канал').grid(column=1, row=0)
        ttk.Label(frame, text='Множитель').grid(column=2, row=0)

    def addChannelControl(self, name: str, title: str = None):
        if title == None:
            title = name
            row = len(list(self._channels.keys()))+1
            channel = ChannelLine(self.frame, name, title, row)
            self._channels.update({name: channel})
        return channel

    def getChannels(self):
        return list(self._channels.values())

    def findChannel(self, name: str):
        return self._channels.get(name, None)

class ChannelTab (Tab):
    def __init__(self, tabControl: ttk.Notebook, title: str):
        Tab.__init__(self, tabControl, title)
        self._frames: dict[str, ChannelFrame] = dict()

    def addFrame(self, name: str, title: str = None):
        if title == None:
            title = name
        col = len(list(self._frames.keys()))
        frame = ChannelFrame(self.tab, name, title, col)
        self._frames.update({name: frame})
        return frame

    def destroyFrame(self, name):
        frame = self._frames.pop(name, None)
        if frame != None:
            frame.frame.destroy()

    def clearFrames(self):
        for key in self._frames.keys():
            self.destroyFrame(key)

    def getFramesList(self):
        return list(self._frames.values())

    def findFrame(self, name: str):
        return self._frames.get(name, None)
