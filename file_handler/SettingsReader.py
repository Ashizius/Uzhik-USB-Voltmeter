import json


class SettingsReader():
    def __init__(self):
        self._channelSettingsFile = 'config/channels.json'
        self._portsFile = 'config/ports.json'
        self._plotSettingsFile = 'config/plotSettings.json'

    def _writeJson(self, data, fileName):
        try:
            with open(fileName, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False,
                          indent=2, sort_keys=True)
            return True
        except:
            return False

    def _readJson(self, fileName):
        try:
            with open(fileName, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def writeChannelSettings(self, data):
        return self._writeJson(data, fileName=self._channelSettingsFile)

    def readChannelSettings(self):
        return self._readJson(fileName=self._channelSettingsFile)

    def writePortsList(self, data):
        return self._writeJson(data, fileName=self._portsFile)

    def readPortsList(self):
        return self._readJson(fileName=self._portsFile)

    def writePlotSettings(self, data):
        return self._writeJson(data, fileName=self._plotSettingsFile)

    def readPlotSettings(self):
        return self._readJson(fileName=self._plotSettingsFile)
