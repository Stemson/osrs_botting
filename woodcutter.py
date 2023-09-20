from random import normalvariate, uniform, randint
from time import sleep, time
from bot_builder_and_functions import Bot, BotState, Needle, Haystack
import os
import cv2 as cv



### --------------- CONTROL PANEL --------------- ###
CLIENT_NAME = 'Runelite - Dalakane'
RUN_DURATION_HOURS = 3 + normalvariate(.25,0.1)
WHAT_LOGS = 'willow'#'logs'
BANK_LOGS = False
BANK_COLOUR = 'green'
LIGHT_FIRES = False #TO DO
AXE_IN_INV = True #lowers count required to drop logs by 1
TREE_SPOT_COLOUR = 'blue'
DEBUG = False

# Woodcutting Specific
logs_needle         = Needle(f'Images\\{WHAT_LOGS}.jpg')

# Inv Specific
inv_closed          = Needle('Images\\inv_closed.jpg')
inv_open            = Needle('Images\\inv_open.jpg')

# Chat Speccific
#chat_open_needle    = Needle('Images\\press_enter_to_chat.jpg')

# Bank Specific
# None

if LIGHT_FIRES: #UNTESTED
    tinder_box_needle = None

### --------------- Fishing Function --------------- ###
def woodcutter(client_name, run_duration_hours, tree_spot_colour, bank_colour, light_fires=False, bank_logs=False, axe_in_inv=False, debug=False):

    bot = Bot(client_name=client_name, debug=debug)
    botstate=BotState()

    time_start=time()
    t_end = time_start + (60 * 60 * run_duration_hours)

    logs_count_before_dropping = 28
    if AXE_IN_INV: logs_count_before_dropping -= 1

    bot.state=botstate.INITIALIZING

    while t_end > time():

        if DEBUG:
            #bot.show_windows()

            #screenshot, offset = bot.get_haystack('client').get_screenshot()
            #haystack = bot.get_haystack('bank')
            #debug_img, offset = haystack.get_screenshot()
            debug_img=bot.bank_is_open()
            #print(bot.skilling_check('fishing', config='--psm 1'))
            cv.imshow('DEBUG.jpeg', debug_img)
            # Saving a screenshot when 's' is pressed
            if cv.waitKey(1) == ord('s'):
                cv.imwrite(f'DEBUG + {time()}.jpg', debug_img)
            # Ending script when 'q' is pressed (Does not work)
            if cv.waitKey(1) == ord('q'):
                cv.destroyAllWindows()
                break

        # 1. Initilising
        if bot.state==botstate.INITIALIZING:
            print("INITIALIZING")
            #click north and "up" arrow key (Add a scroll out?)
            bot.set_view()
            bot.open_inv()
            bot.close_chat()
            bot.state=botstate.CHECKING_INV

        # 2. Checking Inventory
        if bot.state==botstate.CHECKING_INV:
            print("CHECKING_INV")
            a = bot.count_logs(logs_needle)
            #b = bot.count_bird_nests(None)
            b=0
            if a+b < logs_count_before_dropping: # space is avaliable in inv
                bot.state=botstate.WOODCUTTING
            else: # a+b => 26
                if bank_logs:
                    bot.state=botstate.DEPOSITING
                elif light_fires:
                    print('lighting fires is yet to be implemented')
                else: 
                     bot.state=botstate.DROPPING_LOGS


        # 3. Fnding and Catching fish
        if bot.state==botstate.WOODCUTTING:
            print("WOODCUTTING")
            if not bot.skilling_check('woodcutting'):
                bot.clickSleeper('spam')
                tree_spot=bot.find_contours(tree_spot_colour, "client")
                bot.click(tree_spot)
                bot.click(tree_spot)
                sleep(normalvariate(2.5,0.35)) # Wait time while character moves to fishing spot
                bot.shortSleep()
                bot.longSleep()
            sleep(uniform(2,4))
            bot.state=botstate.CHECKING_INV

        # 4. Dropping fish
        if bot.state==botstate.DROPPING_LOGS:
            print("DROPPING_LOGS")
            bot.drop_logs(logs_needle) #TO DO: Make a more natural dropping pattern. E.g left-right-right-left, maybe add randon check to miss one and go back.
            bot.state=botstate.WOODCUTTING

        if bot.state==botstate.DEPOSITING:
            print("BANKING LOGS")
            if bot.bank_is_open():
                if axe_in_inv: bot.click_item_in_inv(logs_needle)
                else:          bot.deposit()
                bot.close_bank()
                bot.longSleep()
                bot.state=botstate.WOODCUTTING
            else:
                bank_spot=bot.find_contours(bank_colour)
                if bank_spot:
                    bot.click(bank_spot)
                    bot.click(bank_spot)
                    sleep(uniform(2.8,3.5) + normalvariate(0.5,0.12))
                else:
                    print('No "bank colour" has been identified')

               

woodcutter(CLIENT_NAME, RUN_DURATION_HOURS, TREE_SPOT_COLOUR, BANK_COLOUR, LIGHT_FIRES, BANK_LOGS, AXE_IN_INV, DEBUG)
