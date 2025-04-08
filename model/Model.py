from model.ComData import AroundQueue
from model.Device import Com


class Model:
    def __init__(self, devices: Com):
        self.devices = devices
        self._data: dict[str, dict[str, AroundQueue]] = {}
        self._indexedDevice: dict[str, str] = {}
        self._isInit = False
        self._portNames: list[str] | None = None
        self._dataSize = devices.dataSize
        self._ports: list[dict[str, str]] = list()

    def setDataSize(self, dataSize: int):
        self._dataSize = dataSize
        self.devices.setDataSize(dataSize)

    def listAllPorts(self):
        self._isInit = False
        ports = self.devices.listAllPorts()
        self._ports = ports
        names = list()
        print('All Ports:', ports)
        for port in ports:
            names.append(port['name'])
        return (ports, names)

    def initDevices(self, portNames: list[str] | None = None):

        if portNames == None:
            portNames = self._portNames
        portNames = self.devices.refreshDevices(portNames)
        self._isInit = True

        self._portNames = portNames

        self.readData()
        for portName in portNames:
            index = self.devices.getDeviceIndex(portName)
            if (index != None) & isinstance(index, int):
                self._indexedDevice.setdefault(index, portName)

    def getIDByName(self, name: str):
        for port in self._ports:
            n = port.get('name', None)
            if n == name:
                return port.get('vid', '')+':'+port.get('pid', '')
        return None

    def getNameByID(self, aggId: str):
        for port in self._ports:
            id = port.get('vid', '')+':'+port.get('pid', '')
            if id == aggId:
                return port.get('name', None)
        return None

    def _mapDataMultiply(self, m: float):
        def mapper(ds: str):
            nonlocal m
            try:
                df: float = int(ds)*m
            except:
                df: int = 0
            return df
        return mapper

    def _dataMultiply(self, dataList, multiplier):
        dataList = list(map(self._mapDataMultiply(multiplier), dataList))
        return dataList

    def setMultiplier(self, i_device: int, i_channel: int, multiplier: int):
        device = self._data.get(str(i_device), dict())
        channel = device.get(str(i_channel), dict())
        channel.update({'multiplier': multiplier})
        device.update({str(i_channel): channel})
        self._data.update({str(i_device): device})
        return self

    def readData(self):
        if self._isInit == False:
            self.initDevices()
        devices = self.devices
        (anyData, dataAmount) = devices.readData()
        if (anyData < 0):
            return False
        if self._portNames == None:
            return False
        for portName in self._portNames:
            deviceChannelsList = self.devices.getChannelsList(portName)
            if (deviceChannelsList == None) | (len(deviceChannelsList) < 1):
                continue
            deviceIndex: str = devices.getDeviceIndex(portName)
            dataChannels = self._data.get(deviceIndex, dict())
            for deviceChannel in deviceChannelsList:
                channelPoints = dataAmount.get(portName, 0)
                channelData = self.devices.getChannelData(
                    portName, deviceChannel)
                dataChannel = dataChannels.get(str(deviceChannel), dict())
                dataPointer = dataChannel.get('pointer', 0)
                dataMultiplier = dataChannel.get('multiplier', 1)

                if len(channelData) < self._dataSize:
                    dataList = [0] * self._dataSize
                dataList = self._dataMultiply(channelData, dataMultiplier)
                dataChannel.update(
                    {'data': dataList, 'pointer': dataPointer+channelPoints, 'multiplier': dataMultiplier})
                dataChannels.update({deviceChannel: dataChannel})
            self._data.setdefault(deviceIndex, dataChannels)
        return True

    def getData(self, index: int | str, channel: int | str):
        channelsData = self._data.get(str(index), dict())
        channelData = channelsData.get(str(channel), dict())
        dataList = channelData.get('data', [0]*self._dataSize)
        pointer = channelData.get('pointer', 0)
        totalPointer = channelData.get('totalPointer', 0)
        return (dataList, pointer, totalPointer)

    def getChannelsList(self, index: int | str):
        channelsData = self._data.get(str(index), dict())
        return list(channelsData.keys())

    def getDevicesList(self):
        return list(self._data.keys())

    def getFullDevicesList(self):
        dList = self.getDevicesList()
        fullList: dict[str, list[str]] = dict()
        for i in dList:
            fullList.setdefault(i, self.getChannelsList(i))
        return fullList

    def close(self):
        self.devices.closeDevices()
        print('ports closed')
