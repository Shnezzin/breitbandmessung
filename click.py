import time
import tkinter as tk
from pyautogui import *
import pyautogui
import tkinter as tk
import time

print('Sleep 20 sec', flush=True)
time.sleep(20)
print('Lets go', flush=True)

modus = 'setup'
#modus = 'position'
#modus = 'einzelmessung'
#modus = 'kampagne'

def click(x,y):
    x += 60
    converted_x = str(x)
    converted_y = str(y)
    print('Click button at location ' + converted_x + converted_y, flush=True)
    pyautogui.leftClick(x,y)

class onetime:

    def downaup():
        root = tk.Tk()
        pyautogui.doubleClick(369,170)
        pyautogui.hotkey('ctrl', 'c')
        Download = root.clipboard_get()
        print('Download: ' + Download + ' MBit/s', flush=True)
        pyautogui.doubleClick(337,340)
        pyautogui.hotkey('ctrl', 'c')
        Upload = root.clipboard_get()
        print('Upload: ' + Upload + ' MBit/s', flush=True)
        click(337,340)

    def measurement():
        happy = '2'
        click(100,259)
        if happy == '1':
            click(260,490)
        elif happy == '2':
            click(415,490)
        elif happy == '3':
            click(530,490)
        elif happy == '4':
            click(670,490)
        elif happy == '5':
            click(815,490)
        elif happy == '6':
            click(940,490)
        else: 
            print('No Set', flush=True)
        time.sleep(1)
        click(1000,670)      


class kampagne:

    def measurement():
        click(115,481)
        time.sleep(1)
        click(418,520)
        click(642,407)
        click(642,488)
        click(642,555)
        click(1120,407)
        click(1120,488)
        click(1120,555)
        time.sleep(1)
        click(1037,683)



if modus == 'einzelmessung':
    onetime.measurement() 
    time.sleep(55)
    onetime.downaup()
elif modus == 'kampagne':
    kampagne.measurement()
elif modus == 'position':
    while True:
        mouseposition = pyautogui.position()
        print(mouseposition, flush=True)
        sleep(1)
elif modus == 'setup':
    while True:
        sleep(10)

exit()
