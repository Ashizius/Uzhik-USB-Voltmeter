from math import floor
from os import mkdir
import time
from typing import TypedDict

# https://superfastpython.com/multithreaded-file-saving/#Save_Files_One-By-One_slowly


class TChannelData(TypedDict):
    pointer: int
    x: list
    y: list
    label: str


class DataSaver():
    def __init__(self):
        self._data: dict[str, dict[str, TChannelData]] = dict()
        self._maxData: int = 500
        self._fullData: int = 0
        self._isCreated = False
        self._isInit = False
        self._isStarted = False
        self._baseName = ''
        self.setBasename()

    def setSaveInterval(self, interval: int | None):
        if interval == None:
            return
        self._maxData: int = interval

    def setBasename(self):
        self._baseName = '_' + str(time.time())

    def initSave(self, xLim: tuple[float, float], yLim: tuple[float, float], xLabel: str = '', yLabel: str = '', saveInterval: int = None):
        self._xLim = xLim
        self._yLim = yLim
        self._xLabel = xLabel
        self._yLabel = yLabel
        self._isInit = True
        if not self._isInit:
            self.setBasename()
        self.setSaveInterval(saveInterval)
        return self

    def getUpdater(self):
        if self._isStarted == False:
            self._isStarted = True
        return self.save_update

    def save_update(self, deviceIndex: int | str, *, x: list[float] = None, interval=1, defLabel='y'):
        deviceData = self._data.get(str(deviceIndex), dict())
        self._data.update({str(deviceIndex): deviceData})

        def update_channel(channelIndex: int | str, y: list[float], lineLabel=defLabel, pointer: int = 0):
            nonlocal deviceData, interval, defLabel
            channelData: TChannelData = deviceData.get(
                str(channelIndex), dict())
            oldPointer = channelData.get('pointer', 0)
            xData = channelData.get('x', list())
            yData = channelData.get('y', list())
            dataSize = pointer-oldPointer
            if dataSize <= 0:
                return
            if len(y) < (dataSize):
                dataSize = len(y)
                ponter = oldPointer + len(y)
            xData.extend([round(interval*i, 4)
                         for i in range(oldPointer+1, pointer+1)])
            yData.extend(y[-1*dataSize:])
            self._fullData += dataSize
            channelData.update(
                {'pointer': pointer, 'x': xData, 'y': yData, 'label': lineLabel})
            deviceData.update({channelIndex: channelData})
        return update_channel

    def _flushData(self):
        self._fullData = 0
        for device in self._data.values():
            for channel in device.values():
                channel['x'] = list()
                channel['y'] = list()

    def save(self, force: bool = False):
        if (self._fullData >= self._maxData) | (force):
            self._dumpAllToFile()
            self._flushData()

    def _dumpAllToFile(self):
        for dI, device in self._data.items():
            data = list()
            labels = list()
            time = None
            for chI, channel in device.items():
                if time == None:
                    time = channel['x']
                    data.append(time)
                data.append(channel['y'])
                labels.append(channel['label'])
            if not self._isCreated:
                self._startFile(dI, labels)
            self._dumpOneToFile(dI, data)
        self._isCreated = True

    def _getFilePath(self, fileName):
        return './data/' + fileName+self._baseName + '.csv'

    def _getFileHeader(self, channels):
        return 't['+self._xLabel+']\t'+('['+self._yLabel+']\t').join(list(channels))+'['+self._yLabel+']'

    def _dumpOneToFile(self, dI, data):
        self._writeData(dI, self._dataToString(data))

    def _startFile(self, dI, channels):
        self._writeData(dI, self._getFileHeader(channels), mode='w')

    def _dataToString(self, data):
        return '\n'.join(map(self._dataMapper, *data))

    def _dataMapper(self, *datas):
        return '\t'.join(map("{:.4f}".format, datas))

    def _writeData(self, fileName, data, *, mode='a'):
        try:
            with open(self._getFilePath(fileName), mode, encoding='utf-8') as f:
                f.write(data+'\n')
        except FileNotFoundError:
            mkdir('./data')
            with open(self._getFilePath(fileName), mode, encoding='utf-8') as f:
                f.write(data+'\n')

    def destroy(self):
        self._dumpAllToFile()
        self._flushData()
        self._data: dict[str, dict[str, TChannelData]] = dict()
        self._isCreated = False
        self._isInit = False
        self._isStarted = False
        return self
