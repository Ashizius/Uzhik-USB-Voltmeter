

from collections import deque
import serial
import serial.tools.list_ports as listPorts

from model.ComData import DEFAULTDATALENGTH, ComData


class Device:
    def __init__(self):
        pass

    def listAllPorts(self):
        return [{'name': 'name', 'device': 'device', 'description': 'description', 'pid': 'pid', 'vid': 'vid', 'hwid': 'hwid'}]


class Com(Device):
    def __init__(self, *, baudrate=9600, timeout=None, dataSize=DEFAULTDATALENGTH):
        self.baudrate = baudrate
        self.timeout = timeout
        self.write_timeout = timeout
        self._comsInfo = self.listAllPorts()  # полный список сустройств
        self._comList: list[serial.Serial] = list()  # текущие устройства
        self.data: dict[str, ComData] = {}
        self.dataSize = dataSize

    def setDataSize(self, dataSize: int):
        self.dataSize = dataSize

    def listAllPorts(self):
        comsInfo = list()
        for comport in (listPorts.comports()):
            comsInfo.append({'name': comport.name, 'device': comport.device, 'description': comport.description, 'pid': str(
                comport.pid), 'vid': str(comport.vid), 'hwid': comport.hwid})

        print('defined ports are:', comsInfo)
        return comsInfo

    def refreshDevices(self, chosen: list[str] = None):
        comsInfo = self._comsInfo
        self._comList.clear()
        portNames: list[str] = list()
        if (comsInfo == None):
            return
        com = None
        # print(comsInfo)
        for comport in (comsInfo):
            comName = comport['name']
            isChosen = True
            if (chosen != None):
                isChosen = (comName in chosen)
            if (isChosen):
                try:
                    com = serial.Serial(
                        port=comport['name'], baudrate=self.baudrate, timeout=self.timeout, write_timeout=self.write_timeout)
                    portNames.append(comport['name'])
                    if (com.is_open):
                        com.close()
                except:
                    com = None
                    comsInfo.remove(comport)
                if (com != None):
                    com.open()
                    self._comList.append(com)
                    self.data.update({comName: ComData(maxlen=self.dataSize)})
        return portNames

    def getDeviceIndex(self, name):
        port = self.data.get(name, None)
        index = None
        if port == None:
            return None
        try:
            index = port.getDeviceNumber()
        except:
            index = None
        return index

    def readData(self):
        allAmount: dict[str, int] = dict()
        someAmount = 0
        for com in (self._comList):
            raw = com.read_all()
            amount = self.data[com.name].readData(raw)

            someAmount += amount
            allAmount.setdefault(com.name, amount)
        return (someAmount, allAmount)

    def getChannelsList(self, name: str):
        port = self.data.get(name, None)
        if port == None:
            return list()
        return port.getChannelsList()

    def getChannelData(self, name: str, ch: str):
        port = self.data.get(name, None)
        if port == None:
            return deque([0]*self.dataSize)
        return port.getChannelData(ch)

    def flushDeviceData(self, name: str):
        port = self.data.get(name, None)
        if port == None:
            return self
        port.flushData()
        return self

    def closeDevices(self):
        for com in (self._comList):
            com.close()
