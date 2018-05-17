import serial
import bluetooth
import time
import win32api, win32con
from ctypes import windll, byref, Structure, WinError, POINTER, WINFUNCTYPE, cast
from ctypes.wintypes import BOOL, HMONITOR, HDC, RECT, LPARAM, DWORD, BYTE, WCHAR, HANDLE
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyautogui

_MONITORENUMPROC = WINFUNCTYPE(BOOL, HMONITOR, HDC, POINTER(RECT), LPARAM)


class _PHYSICAL_MONITOR(Structure):
    _fields_ = [('handle', HANDLE),
                ('description', WCHAR * 128)]


def _iter_physical_monitors(close_handles=True):
    def callback(hmonitor, hdc, lprect, lparam):
        monitors.append(HMONITOR(hmonitor))
        return True

    monitors = []
    if not windll.user32.EnumDisplayMonitors(None, None, _MONITORENUMPROC(callback), None):
        raise WinError('EnumDisplayMonitors failed')

    for monitor in monitors:
        # Get physical monitor count
        count = DWORD()
        if not windll.dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(monitor, byref(count)):
            raise WinError()
        # Get physical monitor handles
        physical_array = (_PHYSICAL_MONITOR * count.value)()
        if not windll.dxva2.GetPhysicalMonitorsFromHMONITOR(monitor, count.value, physical_array):
            raise WinError()
        for physical in physical_array:
            yield physical.handle
            if close_handles:
                if not windll.dxva2.DestroyPhysicalMonitor(physical.handle):
                    raise WinError()


def set_vcp_feature(monitor, code, value):
    #Sends a DDC command to the specified monitor.

    if not windll.dxva2.SetVCPFeature(HANDLE(monitor), BYTE(code), DWORD(value)):
        raise WinError()

brightness = 0
contrast = 25
screenWidth = 1920 #your screen width and 
screenheight = 1080 #height for cursor to function correctly
mouseX = 0
mouseY = 0

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volumeLevel = volume.GetMasterVolumeLevel()
ser = None
try:
    ser = serial.Serial(port="COM5", baudrate=9600, timeout=1)
except:
    print("no connection")
while 1:
    startingPoint = time.time()
    while ser != None and ser.isOpen():
        command = ser.readline().split(" ")
        print(command)
        mouseX, mouseY = win32api.GetCursorPos()

        if command[0] == "b":
            if command[1] == "+":
                brightness += 4
            elif command[1] == "-":
                brightness -= 4
            if brightness > 100:
                brightness = 100
            elif brightness < 0:
                brightness = 0
            for handle in _iter_physical_monitors():
                set_vcp_feature(handle, 0x10, brightness)
            startingPoint = time.time()

        elif command[0] == "c":
            if command[1] == "+":
                contrast +=4
            elif command[1] == "-":
                contrast -=4
            if contrast > 100:
                contrast = 100
            elif contrast < 25:
                contrast = 25
            for handle in _iter_physical_monitors():
                set_vcp_feature(handle, 0x12, contrast)
            startingPoint = time.time()

        elif command[0] == "v":
            if command[1] == "+":
                volumeLevel = volumeLevel + 0.2 + (-0.05*volumeLevel)
                if volumeLevel > 0:
                    volumeLevel = 0
            elif command[1] == "-":
                volumeLevel = volumeLevel - 0.2 - (-0.05*volumeLevel)
                if volumeLevel < -80:
                    volumeLevel = -80
            volume.SetMasterVolumeLevel(volumeLevel, None)
            startingPoint = time.time()

        elif command[0] in ["x", "y"] and int(command[1]) != [mouseX, mouseY]:
            if command[0] == "x":
                mouseX = mouseX + int(command[1])
                if mouseX > screenWidth:
                    screenWidth = 3440
            elif command[0] == "y":
                mouseY = mouseY - int(command[1])
                if screenHeight > 1440:
                    screenHeight = 1440
            win32api.SetCursorPos((mouseX, mouseY))
            startingPoint = time.time()
        elif command[0] == "mClick\r\n":
            pyautogui.click(mouseX, mouseY, button='left')
            startingPoint = time.time()
        elif command[0] == "1":
            startingPoint = time.time()

        if time.time() - startingPoint > 10:
            ser.close()

    try:
        ser = serial.Serial(port="COM5", baudrate=9600, timeout=1)
    except:
        print("no connection")
    time.sleep(0.5)
