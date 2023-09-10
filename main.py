from bot import BotState, Bot
from vision import Needle
import os
from time import time
import cv2 as cv

# Change working directory to whenever the script is found
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#### Loading all required imgs and setting threshold ###
PIE_DISH_PATH =      'Images\\pie_dish.jpg'
PASTRY_PATH =        'Images\\pastry.jpg'

# initalizing Needles, Haystack, and Hand
pie_dish =       Needle(PIE_DISH_PATH)
pastry =         Needle(PASTRY_PATH)

### Building the Bot ###
CLIENT_NAME='Runelite - Vithala'
DEBUG=True
bot = Bot(client_name=CLIENT_NAME, debug=DEBUG)

#bank_haystack = HaystackCapture(CLIENT_NAME, BANK_REGION)

# initalizing States if the Bot <- Left over, Unfinished. Need to review tutorials to see how this works
#bot = PieShellBot()

bot.state=BotState.INITIALIZING

#Below assumes inital state is 'empty inv', 'bank is stocked with supplies', bank is closed', 'item withdrawl is set to 13'.

loop_time=time()
while True:
    
    screenshot, offset = bot.get_screenshot()
    
    if bot.state==BotState.INITIALIZING:
        if bot.bank_is_open():
            bot.state=BotState.WITHRAWING
        else:
            bot.state=BotState.OPENING_BANK

    if bot.state==BotState.OPENING_BANK:
        bot.open_bank()
        bot.state=BotState.WITHRAWING
        pass

    if bot.state==BotState.WITHRAWING:
        items = [pie_dish, pastry]
        bot.withdraw(items)
        bot.close_bank()
        bot.state=BotState.MAKINMG

    if bot.state==BotState.MAKINMG:
        items = [pie_dish, pastry]
        bot.make(items)
        bot.state=BotState.DEPOSITING

    if bot.state==BotState.DEPOSITING:
        bot.deposit()
        bot.state=BotState.WITHRAWING

    #For debuging
    print(f'FPS {1/(time() - loop_time)}')
    loop_time=time()
    
    # Show image recognition in action. Used during the building and debuging of bot
    if DEBUG:
        # Show screenshots  
        pie_dish_coords=pie_dish.find(screenshot, offset, 0.8, debug_mode='rectangles')
        pastry_coords=pastry.find(screenshot, offset, 0.8, debug_mode='rectangles')
        cv.imshow('DEBUG', screenshot)
        # Saving a screenshot when 's' is pressed
        if cv.waitKey(1) == ord('s'):
            cv.imwrite(f'DEBUG + {time()}.jpg', screenshot)
        # Ending script when 'q' is pressed (Does not work)
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break



"""
# initalize time for debugging (calculating FPS)
loop_time = time()

while(True):

    screenshot = wincap.get_screenshot()

    cv.imshow('DEBUG', screenshot)
    if cv.waitKey(1) == ord('s'):
        cv.imwrite('DEBUG.jpg', screenshot)
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break
        

##############################
"""
"""
class BotState:
    INITIALIZING = 0
    DEPOSITING = 1
    SHELL_MAKING = 2
    WITHDRAWING = 3
    LOGGING_IN = 4
    LOGGING_OUT = 5

class PieShellBot:

    # constants
    pie_dish_img = ('pie_dish.jpg', cv.IMREAD_UNCHANGED)
    pastry_img = ('pastry.jpg', cv.IMREAD_UNCHANGED)
    bank_img = ('bank_sample.jpg', cv.IMREAD_UNCHANGED)
    inv_img = ('inv_sample.jpg', cv.IMREAD_UNCHANGED)

    # threading properties

    # properties
    client_name = None

    # constructor
    def __init__(self, window_offset, window_size):
        pass

"""