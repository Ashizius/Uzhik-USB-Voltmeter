import tkinter as tk


from appInterface.appTabs.ChannelTab import ChannelTab
from appInterface.appTabs.TabControl import TabControl
from appInterface.appWindows.Window import Window
from presenter.AppConfiguration import TSettingsList


class SetupWindow(Window):
    def __init__(self, root: tk.Toplevel, *, placer: tk.Toplevel = None):
        Window.__init__(self, root, title='настройки', placer=placer)
        self.tabControl = tabControl = TabControl(self._window)
        tabControl.addTab('com', 'Настройка COM портов')
        self.channelSetup: ChannelTab = tabControl.addTab(
            'channelSetup', 'Настройка каналов', ChannelTab)
        self._comFrame = comFrame = tk.LabelFrame(tabControl.getTab(
            'com').tab, text="Настройка COM портов ", relief=tk.RIDGE)
        comFrame.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
        self._portsListbox = portsListbox = tk.Listbox(
            comFrame, selectmode='multiple')
        tk.Label(comFrame, text='Интервал').grid(row=0, column=0)
        tk.Label(comFrame, text='Количество \n точек').grid(row=0, column=1)

        self._intervalInput = tk.Entry(comFrame)
        self._dataSizeInput = tk.Entry(comFrame)
        portsListbox.grid(row=2, column=0, columnspan=2, sticky='ew')
        self._intervalInput.grid(row=1, column=0)
        self._dataSizeInput.grid(row=1, column=1)

        self._onApplyCallback: function[TSettingsList] = lambda x: print({
                                                                         'portsList': x})
        self._monitorApplyCallback: function[str,
                                             str, float, bool] = lambda *x: print
        self._monitorLoadCallback: function[None] = lambda *x: (
            '0', '0', 0, True)
        self._onRefreshCallback: function = lambda: print(
            'refresh is not assigned')

        self.portsApplyButton = portsApply = tk.Button(
            comFrame, text="Применить", state=tk.ACTIVE, command=self._portsApply)
        self.portsRefreshButton = portsRefresh = tk.Button(
            comFrame, text="Обновить", state=tk.ACTIVE, command=self._portsRefresh)
        portsApply.grid(row=3, column=1, sticky='ew')
        portsRefresh.grid(row=3, column=0, sticky='ew')

        self.monitorApplyButton = monitorApply = tk.Button(
            self.channelSetup.tab, text="Применить", state=tk.ACTIVE, command=self._monitorApply, width=10, anchor='w')
        self.monitorLoadButton = monitorLoad = tk.Button(
            self.channelSetup.tab, text="Загрузить", state=tk.ACTIVE, command=self._monitorLoad, width=10, anchor='w')
        monitorApply.grid(row=2, column=0, sticky='w')
        monitorLoad.grid(row=1, column=0, sticky='w')

    def fillPorts(self, ports: list[str]):
        self._portsListbox.delete(0, tk.END)
        for port in ports:
            self._portsListbox.insert(tk.END, port)

    def selectPorts(self, ports: list[str]):
        portsList: list = self._portsListbox.get(0, 'end')
        for port in ports:
            if port in portsList:
                index = portsList.index(port)
                self._portsListbox.selection_set(index)

    def setDataSize(self, val):
        self._dataSizeInput.delete(0, tk.END)
        self._dataSizeInput.insert(0, str(val))

    def setInterval(self, val):
        self._intervalInput.delete(0, tk.END)
        self._intervalInput.insert(0, str(val))

    def setOnApplyCallback(self, callback):
        self._onApplyCallback = callback

    def setOnRefreshCallback(self, callback):
        self._onRefreshCallback = callback

    def setMonitorApplyCallback(self, callback):
        self._monitorApplyCallback = callback

    def setMonitorLoadCallback(self, callback):
        self._monitorLoadCallback = callback

    def _portsApply(self):
        if self._portsListbox.size() > 0:
            if len(self._portsListbox.curselection()) == 0:
                portsList = list()
            else:
                portsList = self._portsListbox.selection_get()
        else:
            portsList = list()
        if not isinstance(portsList, list):
            portsList = [portsList]
        try:
            dataSize = int(
                round(float(self._dataSizeInput.get().replace(',', '.'))))
            interval = float(self._intervalInput.get().replace(',', '.'))
        except:
            dataSize = 100
            interval = 1
        settings: TSettingsList = {
            'portsList': portsList, 'dataSize': dataSize, 'interval': interval}
        self._onApplyCallback(settings)

    def _portsRefresh(self):
        self._onRefreshCallback()

    def _monitorApply(self):
        done = None
        for frame in self.channelSetup.getFramesList():
            deviceIndex = frame.name
            for channel in frame.getChannels():
                (channelIndex, enabled, multiplier) = channel.getSetup()
                done = self._monitorApplyCallback(
                    deviceIndex, channelIndex, multiplier, enabled)
        if done != None:
            done()

    def _monitorLoad(self):
        self._monitorLoadCallback()

    def channelApply(self, deviceIndex, channelIndex, multiplier, enabled):
        frame = self.channelSetup.findFrame(deviceIndex)
        if frame == None:
            frame = self.channelSetup.addFrame(deviceIndex)
        channel = frame.findChannel(channelIndex)
        if channel == None:
            channel = frame.addChannelControl(channelIndex)
        channel.setSetup(multiplier, enabled)
