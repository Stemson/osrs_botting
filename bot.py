from hand import Hand
from sleep import *
import os
import cv2 as cv
import numpy as np
from time import time, sleep
from random import randint
from vision import Needle, Haystack
#from pieShellBot import PieShellBot
from hand import Hand
from sleep import Sleep

# Hand class has acess to click() and write() functions
hand = Hand()

#Change working directory to whenever the script is found
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#### Loading all required imgs and setting threshold ###
READY_TO_MAKE_PATH = 'Images\\ready_to_make_confirmation.jpg'
ALL_ICON_UNSELECTED_PATH =      'Images\\all_icon_unselected.jpg'
ALL_ICON_SELECTED_PATH =      'Images\\all_icon_selected.jpg'
OPEN_BANK_PATH =     'Images\\open_bank.jpg'
DEPOSIT_PATH =       'Images\\deposit.jpg'
BANK_TITLE =         'Images\\bank_title.jpg'
RED_SQUARE =         'Images\\red_square.jpg'

# initalizing Needles, Haystack, and Hand
ready_to_make =         Needle(READY_TO_MAKE_PATH)
all_icon_unselected =   Needle(ALL_ICON_UNSELECTED_PATH)
all_icon_selected =     Needle(ALL_ICON_SELECTED_PATH)
open_bank =             Needle(OPEN_BANK_PATH)
bank_title=             Needle(BANK_TITLE)
deposit =               Needle(DEPOSIT_PATH)
open_bank_icon =        Needle(RED_SQUARE)

class BotState: # Is there a reason this isnt a dictionary?
    #Constants
    INITIALIZING = 0
    OPENING_BANK = 1
    WITHRAWING = 2
    MAKINMG = 3
    DEPOSITING = 4

class Bot:
    # constants
    OFFSET=[0,0]                   # This surely isnt right, OFFSET will need to updated to be 
    THRESHOLD = 0.9                # Consider making individual thresholds for needles
    DEBUG_MODE = 'rectangles'
    RANDOMIZE_COORDS=True
    BANK_REGION = [36,27, 484,335] # [x,y,w,h]
    INV_REGION = [580, 194, 172, 250]
    GE_REGION = [] 

    def __init__(self, client_name, bank_region=BANK_REGION, inv_region=INV_REGION, debug=True, state=None):
        # properties
        self.client_haystack = Haystack(client_name)
        self.bank_haystack   = Haystack(client_name, cropped_region=bank_region)
        self.inv_haystack    = Haystack(client_name, cropped_region=inv_region)
        self.DEBUG=debug
        self.screenshot=None
        self.offset=None

    
    def get_screenshot(self, region='client'):
        if region == 'client':  return self.client_haystack.get_screenshot()
        if region == 'bank':    return self.bank_haystack.get_screenshot()
        if region == 'inv':     return self.inv_haystack.get_screenshot()
        if region == 'text':    pass
        if region == 'fullscreen': return Haystack().get_screenshot()
    
    def on_screen(self, item, region='client', threshold=THRESHOLD, debug_mode=DEBUG_MODE):
        screenshot, offset = self.get_screenshot(region)
        coords = item.find(screenshot, offset)
        return bool(coords)

    
    def bank_is_open(self):
        return self.on_screen(bank_title, region='bank')
        
    def open_bank(self):
        for i in range(randint(2,4)+randint(0,3)+randint(0,1)):
            #screenshot, offset = self.get_screenshot('client')
            #coords = open_bank_icon.find(screenshot, offset, threshold=0.5)
            #hand.click(coords) # Red square was too buggy, need alternate solution
            hand.click([466,335])
            Sleep.clickSleeper('spam')
        Sleep.clickSleeper('close_bank')

    def withdraw(self, items, threshold=THRESHOLD, debug_mode=DEBUG_MODE, randomizeCoord=RANDOMIZE_COORDS):
        for needle in items:
            screenshot, offset = self.get_screenshot('bank')
            coords = needle.find(screenshot, offset)
            hand.click(coords[0]) #0 index used in debugging
            Sleep.clickSleeper('widthdraw')
        

    def close_bank(self):
        hand.write('esc')
        Sleep.clickSleeper('close_bank')
        

    def make(self, items, threshold=THRESHOLD, debug_mode=DEBUG_MODE, randomizeCoord=RANDOMIZE_COORDS):
        for needle in items:
            screenshot, offset = self.get_screenshot('inv')
            coords = needle.find(screenshot, offset)
            hand.click(coords[0])
            Sleep.clickSleeper('inv_item')
        if self.on_screen(all_icon_unselected, threshold=0.90):
            screenshot, offset = self.get_screenshot('client')
            coords = all_icon_unselected.find(screenshot, offset)
            hand.click(coords[0])
            Sleep.clickSleeper('inv_item')
        hand.write('space')
        Sleep.clickSleeper('spam')
        if randint(0,1)== 0:  hand.write('space')
        Sleep.clickSleeper('make')

    def deposit(self):
        self.open_bank() # Assumes the open bank function clicks the deposit icon. 
                         # If open_bank() is changed then this will need to be updated 
                         # to find and click the deposit icon. 

    pass