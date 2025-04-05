
from collections import deque
from typing import TypedDict

class TypedDictDevice(TypedDict):
    raw: str
    device: str | None
    channels: dict[str, deque[int]]

class AroundQueue(TypedDict):
    pointer: int
    totalPointer: float
    data: list[float]
    multiplier: int


DEFAULTDATALENGTH = 50

class ComData:
    def __init__(self, maxlen=DEFAULTDATALENGTH):
        self._channelData: TypedDictDevice = {
            'raw': '', 'device': None, 'channels': {}}
        self._channelList: list[str] = None
        self._device: str = None
        self._partial = ''
        self._maxlen: int = maxlen

    def _readCommand(self, chunk: str):
        chunk.count('hello')
        chunk = ''.join(chunk.split('hello'))
        return chunk

    def _verifyChunks(self, rawChunk: str):
        lastChunk = ''
        chunks: list[str] = rawChunk.split(',\\r\\n')
        newChunks = list()
        for chunk in chunks:
            if (len(chunk)) < 1:
                continue
            if (chunk[0] != '{'):
                continue
            if (chunk[-1] != '}'):
                lastChunk = chunk
                continue
            newChunks.append(chunk)
        return (newChunks, lastChunk)

    def _readChunk(self, raw: str, partial: str):
        chunks: list[str] = list()
        united: str = partial + raw
        if (len(raw) < 10):
            return (chunks, united)
        (chunks, rest) = self._verifyChunks(united)
        return (chunks, rest)

    def _parseData(self, rawData: str):
        [info, sval] = rawData.split(':')
        val = int(sval)
        if self._device == None:
            self._channelData['device'] = info[1:2]
            self._device = info[1:2]
        return (info[2:3], val)

    def _parseChunk(self, chunk: str):
        datas = chunk[1:-1].split(';')
        dataArray: list[tuple[str, str]] = list()
        for data in datas:
            if (len(data) < 2):
                continue
            dataArray.append(self._parseData(data))
        return dataArray

    def _addChannelData(self, channel: str, val):
        valuesList: deque = self._channelData['channels'].get(
            channel, deque([0]*self._maxlen, maxlen=self._maxlen))
        valuesList.append(val)
        self._channelData['channels'].setdefault(channel, valuesList)

    def readData(self, rawBytes: str):
        raw = str(rawBytes)
        if (len(raw) < 3):
            return 0
        raw = self._readCommand(raw)
        self._channelData.update({'raw': raw[2:-1]})
        (chunks, partial) = self._readChunk(raw[2:-1], self._partial)
        self._partial = partial

        for chunk in chunks:
            datas = self._parseChunk(chunk)
            for (ch, val) in datas:
                self._addChannelData(ch, val)
        return len(chunks)

    def flushData(self):
        channels = self._channelData['channels']
        if (self._channelList == None):
            self._channelList = channels.keys()
        for key in self._channelList:
            channels[key] = deque([0]*self._maxlen, maxlen=self._maxlen)

    def getDeviceNumber(self):
        channel = self._channelData['device']
        return channel

    def getChannelsList(self):
        if (self._channelList == None):
            self._channelList = self._channelData['channels'].keys()
        return self._channelList

    def getChannelData(self, ch: str):
        data = self._channelData['channels'].get(
            ch, deque([0]*self._maxlen, maxlen=self._maxlen))
        return data