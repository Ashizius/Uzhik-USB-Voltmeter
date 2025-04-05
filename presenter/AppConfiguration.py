
from typing import Literal, TypedDict

from model.Model import Model
from presenter.SettingsReader import SettingsReader


class TChannelSettings(TypedDict):
    multiplier: int
    enabled: bool


class TSettingsList(TypedDict):
    portsList: list[str]
    interval: float
    dataSize: int


class TConfigLoaded(TypedDict):
    ports: bool
    plot: bool
    channels: bool


class AppConfiguration():
    def __init__(self, fileReader: SettingsReader):
        self.fileReader = fileReader
        self._selectedPorts: list[str] = list()
        self._selectedChannels: dict[str, set[str]] = dict()
        self._selectedDevices = set()
        self._channelsSettings: dict[str, dict[str, TChannelSettings]] = dict()
        self.getFullDevicesList = lambda: {'': ['']}
        self.fillDefaultPorts()
        self.fillDefaultPlotConfig()
        self.allPortsNames = list()
        self._isLoaded: TConfigLoaded = {
            'ports': False, 'plot': False, 'channels': False}

    def isLoaded(self, cfgName: Literal['ports'] | Literal['plot'] | Literal['channels']):
        return self._isLoaded[cfgName]

    def getDefaults(self):
        fullList = self.getFullDevicesList().items()
        print(fullList)
        for (deviceIndex, channels) in fullList:
            device: dict[str, TChannelSettings] = dict()
            for channelIndex in channels:
                settings: TChannelSettings = {'multiplier': 1, 'enabled': True}
                device.update({channelIndex: settings})
                self.setSelectedDevice(deviceIndex, channelIndex, True)
            self._channelsSettings.update({deviceIndex: device})

    def fillDefaultChannelsSettings(self):
        for i in range(0, len(self._selectedPorts)):
            for j in range(0, 7):
                self.setDeviceSettings(i, j, 0.0048828125, False)

    def fillDefaultPorts(self):
        self._selectedPorts = list()
        self.dataSize = 500
        self.interval = 1.0

    def fillDefaultPlotConfig(self):
        self._xlim = (0, self.dataSize*self.interval)
        self._ylim = (0, 5)

    def loadPlotConfig(self):
        plotSettings = self.fileReader.readPlotSettings()
        if plotSettings == None:
            self.fillDefaultPlotConfig()
            return
        self._isLoaded['plot'] = True
        [xlim, ylim] = plotSettings
        self._xlim = tuple(xlim)
        self._ylim = tuple(ylim)

    def savePlotConfig(self):
        self.fileReader.writePlotSettings([self._xlim, self._ylim])

    def loadPortConfig(self):
        config: TSettingsList = self.fileReader.readPortsList()
        if config == None:
            self.fillDefaultPorts()
            return
        self._isLoaded['ports'] = True
        self._selectedPorts = config['portsList']
        self.dataSize = config['dataSize']
        self.interval = config['interval']

    def savePortConfig(self):
        settings: TSettingsList = {'portsList': self._selectedPorts,
                                   'dataSize': self.dataSize, 'interval': self.interval}
        self.fileReader.writePortsList(settings)

    def loadChannelsSettings(self):
        channelsSettings = self.fileReader.readChannelSettings()
        if channelsSettings == None:
            self.fillDefaultChannelsSettings()
            return
        self._isLoaded['channels'] = True
        self._channelsSettings = channelsSettings

    def saveChannelsSettings(self):
        self.fileReader.writeChannelSettings(self._channelsSettings)

    def setLimits(self, xlim: tuple[int, int] = None, ylim: tuple[int, int] = None):
        if xlim != None:
            self._xlim = xlim
        if ylim != None:
            self._ylim = ylim

    def getLimits(self):
        self._xlim = (0, self.dataSize*self.interval)
        return (self._xlim, self._ylim)

    def setInterval(self, interval: float):
        self.interval = interval

    def setDataSize(self, dataSize: int):
        self.dataSize = dataSize

    def getSelectedPorts(self, cb=None):
        print(self._selectedPorts)
        if cb == None:
            return self._selectedPorts
        else:
            return list(map(cb, self._selectedPorts))

    def setSelectedPorts(self, ports: list[str]):
        self._selectedPorts = ports
        print(self._selectedPorts)

    def setSelectedDevice(self, deviceIndex, channelIndex, enabled):
        selectedChannels = self._selectedChannels.get(deviceIndex, set())
        if enabled:
            selectedChannels.add(channelIndex)
        else:
            selectedChannels.discard(channelIndex)
        self._selectedChannels.update({deviceIndex: selectedChannels})
        for (k, channels) in self._selectedChannels.items():
            if len(channels) > 0:
                self._selectedDevices.add(k)
            else:
                self._selectedDevices.discard(k)

    def updateSelectedDevices(self, *, callback=None):
        for (dI, d) in self._channelsSettings.items():
            for (chI, ch) in d.items():
                en = ch.get('enabled', False)
                m = ch.get('multiplier', 1)
                self.setSelectedDevice(dI, chI, en)
                if en & (callback != None):
                    callback(dI, chI, m)

    def setDeviceSettings(self, deviceIndex, channelIndex, multiplier, enabled):
        self.setSelectedDevice(deviceIndex, channelIndex, enabled)

        device = self._channelsSettings.get(deviceIndex, dict())
        channel = device.get(channelIndex, dict())
        channel.update({'multiplier': multiplier, 'enabled': enabled})
        device.update({channelIndex: channel})
        self._channelsSettings.update({deviceIndex: device})

    def getSelectedDevices(self):
        return self._selectedDevices

    def getSelectedChannels(self, device: str):
        return self._selectedChannels.get(device, set())

    def getChannelsSettings(self):
        return self._channelsSettings

    def load(self):
        self.getDefaults()
