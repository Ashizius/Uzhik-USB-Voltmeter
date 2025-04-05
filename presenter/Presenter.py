import time
from model.Device import Com
from presenter.AppConfiguration import AppConfiguration
from appInterface.AppInterface import AppInterface, TSettingsList
from model.Model import Model
from presenter.SettingsReader import SettingsReader


class Presenter():
    def __init__(self, name='test'):
        self._last_update = time.perf_counter()

        self.fileReader = SettingsReader()
        self.config = config = AppConfiguration(self.fileReader)
        self.config.loadPortConfig()
        self.config.loadPlotConfig()
        self.config.loadChannelsSettings()
        com = Com(dataSize=config.dataSize)
        model = Model(com)
        config.getFullDevicesList = model.getFullDevicesList
        interface = AppInterface(name)
        self.dataSize = config.dataSize
        self.interval = config.interval

        # self.plotter:Plotter|None = None
        self.interface = interface
        self.model = model

        (ports, names) = self.model.listAllPorts()
        self.config.allPortsNames = names

        interface.setupWindow.setOnApplyCallback(self._applyPorts)
        interface.setupWindow.setOnRefreshCallback(self._refreshPorts)
        self.interface.setupWindow.setMonitorLoadCallback(
            self._monitorLoadCallback)
        self.interface.setupWindow.setMonitorApplyCallback(
            self._monitorApplyCallback)

        interface.setOnQuit(self.destroy)
        interface.setRecurringCallback(self._reader)

    def start(self):
        self.interface.root.after(1000, self._trySelfStart)
        self._current_update = time.perf_counter()
        print('!init time:', (self._current_update-self._last_update)*1000)
        self.interface.setupWindow.hide()
        self.interface.monitorWindow.hide()
        return self.interface.start()

    def _trySelfStart(self):
        self.interface.addWarning('загружаем настройки', 'info', 1000)
        if not self.config.isLoaded('ports'):
            self.interface.addWarning(
                'не найден файл со списком портов', 'warning', 3000)
            return
        isChecked = self.setupPorts()
        if not isChecked:
            self.interface.setupWindow.show()
            self.interface.addWarning('не найдены устройства', 'error', 5000)
            return
        self.enablePorts()
        self.setupPortsInterface()
        if not self.config.isLoaded('channels'):
            self.interface.setupWindow.show()
            self.interface.addWarning(
                'не найден файл с конфигурацией каналов', 'warning', 3000)
            return
        self.setupChannels()
        self.config.updateSelectedDevices(callback=self.model.setMultiplier)

        self.setupPlotter()
        self.interface.addWarning('всё успешно загружено', 'info', 1000)
        self.interface.startCalling()
        self.interface.addWarning('открыт монитор', 'flood', 1000)
        self.interface.addWarning('в работе порты', 'flood', 1000)
        self.interface.addWarning(
            ','.join(self.config.getSelectedPorts()), 'flood', 5000)
        self.interface.monitorWindow.show()

    def setupPorts(self):
        (ports, self.config.allPortsNames) = self.model.listAllPorts()
        self.interface.setupWindow.fillPorts(self.config.allPortsNames)
        portList = list()
        selectedPorts = list()
        for portId in self.config.getSelectedPorts():
            portName = self.model.getNameByID(portId)
            if portName in self.config.allPortsNames:
                portList.append(portName)
                selectedPorts.append(portId)
        print('!!!selected ports', selectedPorts)
        self.config.setSelectedPorts(selectedPorts)
        if len(selectedPorts) == 0:
            return False
        return True

    def enablePorts(self):
        self.model.setDataSize(self.config.dataSize)
        self.model.initDevices(
            self.config.getSelectedPorts(self.model.getNameByID))
        self.config.savePortConfig()

    def setupPortsInterface(self):
        self.interface.setupWindow.selectPorts(
            self.config.getSelectedPorts(self.model.getNameByID))
        self.interface.setupWindow.setInterval(self.config.interval)
        self.interface.setupWindow.setDataSize(self.config.dataSize)

    def setupPlotter(self):
        (xlim, ylim) = self.config.getLimits()
        self.interface.plotInit(xlim, ylim, xLabel='s', yLabel='V')

    def setupChannels(self):
        self.config.loadChannelsSettings()
        fullDict = self.config.getChannelsSettings().items()
        for (dIndex, chDict) in fullDict:
            for (chIndex, chSettings) in chDict.items():
                self.interface.setupWindow.channelApply(dIndex, chIndex, chSettings.get(
                    'multiplier', 1), chSettings.get('enabled', True))

    def enableChannels(self):
        self.config.saveChannelsSettings()

    def _refreshPorts(self):
        self.setupPorts()
        self.setupPortsInterface()

    def _applyPorts(self, settings: TSettingsList):
        portList = settings.get('portsList', list())
        dataSize = settings.get('dataSize', 100)
        interval = settings.get('interval', 1.0)
        newConfigPorts = list()
        for portName in portList:
            newConfigPorts.append(self.model.getIDByName(portName))
        self.config.setSelectedPorts(newConfigPorts)
        self.config.setDataSize(dataSize)
        self.config.setInterval(interval)

        self.enablePorts()
        self.setupChannels()

    def _reader(self, stop=False, restart=False):
        if restart:
            print('restart')
            self.setupPlotter()

        if stop:
            print('stop')
            return
        isData = self.model.readData()
        if not isData:
            return
        for deviceIndex in self.config.getSelectedDevices():
            updater = self.interface.plotGetUpdater()
            draw = updater(deviceIndex, interval=self.config.interval)
            for channelIndex in self.config.getSelectedChannels(deviceIndex):

                (data, pointer, totalPointer) = self.model.getData(
                    deviceIndex, channelIndex)
                draw(channelIndex, data, lineLabel=str(channelIndex))
        self.interface.plotPrint()

    def _monitorLoadCallback(self):
        self.config.loadChannelsSettings()

    def _monitorApplyCallback(self, deviceIndex, channelIndex, multiplier, enabled):
        self.config.setDeviceSettings(
            deviceIndex, channelIndex, multiplier, enabled)
        if enabled:
            print(deviceIndex, channelIndex, multiplier)
            self.model.setMultiplier(deviceIndex, channelIndex, multiplier)
        return self.enableChannels

    def destroy(self):
        self.model.close()
        print('ports closed')
