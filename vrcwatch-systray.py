import json
import vrcwatch
from vrcwatch import ReducedMessenger
from pythonosc import udp_client
from datetime import datetime
from time import sleep
from typing import Any, TextIO
from infi.systray import SysTrayIcon
import json

DEFAULT_ADDRESS = "127.0.0.1"
DEFAULT_SEND_PORT = 9000
DEFAULT_SYNC = 5.0
DEFAULT_DINTERVAL = 1.0
DEFAULT_AINTERVAL = 0.1
DEFAULT_WITHANALOG = True
SETTING_FILE_PATH = "./setting.json"

SETTING_KEY_ADDRESS = "address"
SETTING_KEY_PORT = "port"
SETTING_KEY_SYNC = "sync"
SETTING_KEY_DINTERVAL = "degital_interval"
SETTING_KEY_AINTERVAL = "analog_interval"
SETTING_KEY_WITHANALOG = "with_analog"
DEFAULT_SETTING = {SETTING_KEY_ADDRESS: DEFAULT_ADDRESS, SETTING_KEY_PORT: DEFAULT_SEND_PORT, SETTING_KEY_SYNC: DEFAULT_SYNC, SETTING_KEY_DINTERVAL: DEFAULT_DINTERVAL, SETTING_KEY_AINTERVAL: DEFAULT_AINTERVAL, SETTING_KEY_WITHANALOG: DEFAULT_WITHANALOG}

class SettingParams(object):
    __slots__ = (
        "_setting_dict"
    )
    
    def __init__(self) -> None:
        self.LoadJSON()
        
    def GetParam(self, key) -> Any:
        return self._setting_dict.setdefault(key, DEFAULT_SETTING.get(key))

    # 未使用        
    # def GetParamsDict(self) -> dict:
    #     return self._setting_dict
    
    def SetParam(self, key, value) -> None:
        self._setting_dict[key] = value
    
    # 未使用
    # def SetPrams(self, address: str = None, port: int = None, sync: float = None, degital_interval: float = None, analog_interval: float = None, with_analog: bool = None) -> None:
    #     address = self._setting_dict.get(SETTING_KEY_ADDRESS) if address is None else address
    #     port = self._setting_dict.get(SETTING_KEY_PORT) if port is None else address
    #     sync = self._setting_dict.get(SETTING_KEY_SYNC) if sync is None else sync
    #     degital_interval = self._setting_dict.get(SETTING_KEY_DINTERVAL) if degital_interval is None else degital_interval
    #     analog_interval = self._setting_dict.get(SETTING_KEY_AINTERVAL) if analog_interval is None else analog_interval
    #     with_analog = self._setting_dict.get(SETTING_KEY_WITHANALOG) if with_analog is None else with_analog
    #     self._setting_dict: dict = {SETTING_KEY_ADDRESS: address, SETTING_KEY_PORT: port, SETTING_KEY_SYNC: sync, SETTING_KEY_DINTERVAL: degital_interval, SETTING_KEY_AINTERVAL: analog_interval, SETTING_KEY_WITHANALOG: with_analog}

    def SaveJOSN(self) -> None:
        with open(SETTING_FILE_PATH, "w") as setting_file:
            json.dump(self._setting_dict, setting_file, indent=4)
            
    def LoadJSON(self) -> None:
        try:
            with open(SETTING_FILE_PATH, "r") as setting_file:
                self._setting_dict = json.load(setting_file)
        except FileNotFoundError :
            with open(SETTING_FILE_PATH, "w") as setting_file:
                self._setting_dict = DEFAULT_SETTING
                json.dump(self._setting_dict, setting_file, indent=4)
                

class OSCSender(object):
    __slots__ = (
        "_is_running",
        "_setting_params",
        "_client",
        "_address",
        "_port",
        "_sync",
        "_degital_interval",
        "_analog_interval",
        "_interval",
        "_with_analog",
        "_year",
        "_month",
        "_day",
        "_weekday",
        "_hour",
        "_minute",
        "_second",
        "_hour_f",
        "_minute_f",
        "_second_f",
        "_hour_fa",
        "_minute_fa",
        "_second_fa",
        "_daytime",
    )
    
    def __init__(self):
        self._setting_params = SettingParams()
        self._is_running: bool = False
        self._address: str = self._setting_params.GetParam(SETTING_KEY_ADDRESS)
        self._port: int = self._setting_params.GetParam(SETTING_KEY_PORT)
        self._sync: float = self._setting_params.GetParam(SETTING_KEY_SYNC)
        self._with_analog: bool = self._setting_params.GetParam(SETTING_KEY_WITHANALOG)
        self._degital_interval: float = self._setting_params.GetParam(SETTING_KEY_DINTERVAL)
        self._analog_interval: float = self._setting_params.GetParam(SETTING_KEY_AINTERVAL)
        self._interval: float = self._analog_interval if self._with_analog else self._degital_interval
        try:
            self._client: udp_client.SimpleUDPClient = udp_client.SimpleUDPClient(self._address, self._port)
        except OSError:
            print(f"IP Address \"{self._address}\" is not valid.\nDefault Address is used instead.\n")
            self._address = DEFAULT_ADDRESS
            self._client = udp_client.SimpleUDPClient(address=DEFAULT_ADDRESS, port=self._port)
        try:
            self._client.send_message("/PortTest", 0)
        except OverflowError:
            print(f"Port number \"{self._port}\" is not valid.\nDefault port is used instead.\n")
            self._port = DEFAULT_SEND_PORT
            self._client = udp_client.SimpleUDPClient(address=self._address, port=DEFAULT_SEND_PORT)
            
        sync = int(self._sync / self._interval)
        self._year = ReducedMessenger(self._client, vrcwatch.AVATAR_PARAMS_YEAR, sync)
        self._month = ReducedMessenger(self._client, vrcwatch.AVATAR_PARAMS_MONTH, sync)
        self._day = ReducedMessenger(self._client, vrcwatch.AVATAR_PARAMS_DAY, sync)
        self._weekday = ReducedMessenger(self._client, vrcwatch.AVATAR_PARAMS_WEEKDAY, sync)
        self._hour = ReducedMessenger(self._client, vrcwatch.AVATAR_PARAMS_HOUR, sync)
        self._minute = ReducedMessenger(self._client, vrcwatch.AVATAR_PARAMS_MINUTE, sync)
        self._second = ReducedMessenger(self._client, vrcwatch.AVATAR_PARAMS_SECOND, sync)
        self._hour_f = ReducedMessenger(self._client, vrcwatch.AVATAR_PARAMS_HOUR_F, sync)
        self._minute_f = ReducedMessenger(self._client, vrcwatch.AVATAR_PARAMS_MINUTE_F, sync)
        self._second_f = ReducedMessenger(self._client, vrcwatch.AVATAR_PARAMS_SECOND_F, sync)
        self._hour_fa = ReducedMessenger(self._client, vrcwatch.AVATAR_PARAMS_HOUR_FA, sync)
        self._minute_fa = ReducedMessenger(self._client, vrcwatch.AVATAR_PARAMS_MINUTE_FA, sync)
        self._second_fa = ReducedMessenger(self._client, vrcwatch.AVATAR_PARAMS_SECOND_FA, sync)
        self._daytime = ReducedMessenger(self._client, vrcwatch.AVATAR_PARAMS_DAYTIME, sync)
        
    def StartSendOSC(self) -> None:
        self._is_running = True
        while self._is_running:
            now = datetime.now()
            self._year.send(now.year - 2000)
            self._month.send(now.month)
            self._day.send(now.day)
            self._weekday.send(now.weekday())
            self._hour.send(now.hour)
            self._minute.send(now.minute)
            self._second.send(now.second)
            self._hour_f.send(vrcwatch.ceil_minifloat(now.hour / 24))
            self._minute_f.send(vrcwatch.ceil_minifloat(now.minute / 60))
            self._second_f.send(vrcwatch.ceil_minifloat(now.second / 60))

            second_analog = now.second / 60 + now.microsecond / 60000000
            minute_analog = now.minute / 60 + second_analog / 3600
            hour_analog = now.hour / 24 + minute_analog / 1440
            if self._with_analog:
                self._hour_fa.send(vrcwatch.ceil_minifloat(hour_analog))
                self._minute_fa.send(vrcwatch.ceil_minifloat(minute_analog))
                self._second_fa.send(vrcwatch.ceil_minifloat(second_analog))
            self._daytime.send(vrcwatch.ceil_minifloat(hour_analog))

            sleep(self._interval)
            
    def QuitSendOSC(self) -> None:
        self._is_running = False
        
    def ToggleAnalog(self) -> None:
        self._with_analog = not self._with_analog
        self._interval = self._analog_interval if self._with_analog else self._degital_interval
        self._setting_params.SetParam(SETTING_KEY_WITHANALOG, self._with_analog)
        
    def GetSettingParams(self) -> SettingParams:
        return self._setting_params
            
class Systray(object):
    __slots__ = (
        "_sender",
        "_menu_options",
        "_analog_menu_texts",
        "_with_analog",
    )
    
    def __init__(self, sender: OSCSender = OSCSender()):
        self._sender = sender
        self._analog_menu_texts = ["Analog: [ ]", "Analog:  [x]"]
        self._with_analog: bool = True
        self._menu_options = (("Toggle Analog", None, self.on_toggle_analog),
                              ("Save Setting", None, self.on_save),)
        
    def create_systray(self) -> None:
        hover = self.create_hover_text()
        systray = SysTrayIcon("icon.ico", hover_text=hover, menu_options=self._menu_options, on_quit=self.on_quit)
        systray.start()
        self._sender.StartSendOSC()
        
    def create_hover_text(self) -> str:
        analog_menu_text = self._analog_menu_texts[1] if self._with_analog else self._analog_menu_texts[0]
        return f"VRChat-KeyCode-OSC\n {analog_menu_text}"
        
    def on_toggle_analog(self, systray: SysTrayIcon) -> None:
        self._sender.ToggleAnalog()
        self._with_analog = not self._with_analog
        systray.update(hover_text=self.create_hover_text())
        
    def on_save(self, systray) -> None:
        self._sender.GetSettingParams().SaveJOSN()
        
    def on_quit(self, systray) -> None:
        self._sender.QuitSendOSC()
        
        
def main():
    osc_sender = OSCSender()
    systray = Systray(osc_sender)
    systray.create_systray()

if __name__ == "__main__":
    main()