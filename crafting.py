from random import normalvariate, uniform, randint
from time import sleep, time
from bot_builder_and_functions import Bot, BotState, Needle, Haystack
import os
import cv2 as cv



### --------------- CONTROL PANEL --------------- ###
CLIENT_NAME = 'Runelite - Kinjor'
RUN_DURATION_HOURS = .8 + normalvariate(.25,0.1)
BANK_COLOUR = 'green'
FURNACE_COLOUR = 'blue'
INGREDIANTS=['gold_bar', 'emerald']
PRODUCT='emerald_necklace'
MOULD_IN_INV = True #lowers count required to drop logs by 1
DEBUG = False

### --------------- Fishing Function --------------- ###
def crafting(client_name, run_duration_hours, furnance_colour, bank_colour, ingrediants, product, mould_in_inv=False, debug=False):

    bot = Bot(client_name=client_name, debug=debug)
    botstate=BotState()

    time_start=time()
    t_end = time_start + (60 * 60 * run_duration_hours)

    ingrediant_needles = [Needle(f'Images\\{ingrediant}.jpg') for ingrediant in ingrediants]
    product_needle = Needle(f'Images\\{product}.jpg') 

    bot.state=botstate.INITIALIZING

    while t_end > time():

        if DEBUG:
            #bot.show_windows()

            #screenshot, offset = bot.get_haystack('client').get_screenshot()
            haystack = bot.get_haystack('bank')
            debug_img, offset = haystack.get_screenshot()
            #debug_img=bot.skilling_check('woodcutting')
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
            #bot.set_view()
            bot.open_inv()
            bot.close_chat()
            bot.state=botstate.CHECKING_INV

        # 2. Checking Inventory
        if bot.state==botstate.CHECKING_INV:
            print("CHECKING_INV")
            ing_count = bot.count_fish(ingrediant_needles)
            product_count = bot.count_fish(ingrediant_needles)
            if count < 26: # space is avaliable in inv
                bot.state=botstate.WOODCUTTING
            else: # a+b => 26
                if bank_logs:
                    bot.state=botstate.DEPOSITING
                elif light_fires:
                    print('lighting fires is yet to be implemented')
                else: 
                     bot.state=botstate.DROPPING_LOGS


        # 3. Fnding and Catching fish
        if bot.state==botstate.CRAFTING:
            time_temp = time()
            timer = time_temp + uniform(25,35)
            print("WOODCUTTING")
            if timer > time():
                bot.state=botstate.BANKING
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

               

crafting(CLIENT_NAME, RUN_DURATION_HOURS, FURNACE_COLOUR, BANK_COLOUR, INGREDIANTS, PRODUCT, MOULD_IN_INV, DEBUG)
